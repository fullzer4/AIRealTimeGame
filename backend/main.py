from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from concurrent.futures import ThreadPoolExecutor
import torch.nn as nn
import numpy as np
import asyncio
import random
import struct
import torch
import time
import os

app = FastAPI()

ball = {"x": 300, "y": 200, "vx": 3, "vy": 3}
paddles = {"player1": 150, "player2": 150}

FPS = 60
WIDTH, HEIGHT = 600, 400

executor = ThreadPoolExecutor()

train_count1 = 0
train_count2 = 0
game_start_time = int(time.time())

connected_clients = set()

MODEL1_PATH = "model1.pth"
MODEL2_PATH = "model2.pth"

class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(5, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 3)
        )

    def forward(self, x):
        return self.fc(x)


model1 = DQN()
model2 = DQN()

optimizer1 = torch.optim.Adam(model1.parameters(), lr=0.001)
optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)

loss_fn = nn.MSELoss()

def load_models():
    if os.path.exists(MODEL1_PATH):
        checkpoint = torch.load(MODEL1_PATH)
        model1.load_state_dict(checkpoint["model_state"])
        optimizer1.load_state_dict(checkpoint["optimizer_state"])
        print("Model 1 loaded successfully.")
    if os.path.exists(MODEL2_PATH):
        checkpoint = torch.load(MODEL2_PATH)
        model2.load_state_dict(checkpoint["model_state"])
        optimizer2.load_state_dict(checkpoint["optimizer_state"])
        print("Model 2 loaded successfully.")

def save_models():
    torch.save({
        "model_state": model1.state_dict(),
        "optimizer_state": optimizer1.state_dict()
    }, MODEL1_PATH)
    torch.save({
        "model_state": model2.state_dict(),
        "optimizer_state": optimizer2.state_dict()
    }, MODEL2_PATH)
    print("Models saved successfully.")

replay_buffer1 = []
replay_buffer2 = []

MAX_MEMORY = 10000
BATCH_SIZE = 64
GAMMA = 0.99

epsilon = 1.0
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.1

def remember(replay_buffer, state, action, reward, next_state, done):
    if len(replay_buffer) > MAX_MEMORY:
        replay_buffer.pop(0)
    replay_buffer.append((state, action, reward, next_state, done))

def train(replay_buffer, model, optimizer):
    if len(replay_buffer) < BATCH_SIZE:
        return
    batch = random.sample(replay_buffer, BATCH_SIZE)
    states, actions, rewards, next_states, dones = zip(*batch)

    states = torch.tensor(np.array(states), dtype=torch.float32)
    actions = torch.tensor(np.array(actions), dtype=torch.int64)
    rewards = torch.tensor(np.array(rewards), dtype=torch.float32)
    next_states = torch.tensor(np.array(next_states), dtype=torch.float32)
    dones = torch.tensor(np.array(dones), dtype=torch.float32)

    q_values = model(states).gather(1, actions.unsqueeze(1)).squeeze(1)
    next_q_values = model(next_states).max(1)[0]
    target_q_values = rewards + GAMMA * next_q_values * (1 - dones)

    loss = loss_fn(q_values, target_q_values.detach())
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

async def send_game_state(websocket):
    global train_count1, train_count2, game_start_time
    response = struct.pack(
        "HHHHIHH",
        max(0, min(65535, int(ball["x"]))),
        max(0, min(65535, int(ball["y"]))),
        max(0, min(65535, int(paddles["player1"]))),
        max(0, min(65535, int(paddles["player2"]))),
        int(time.time() - game_start_time),
        train_count1,
        train_count2
    )
    await websocket.send_bytes(response)

def update_game_state():
    global ball, paddles, epsilon, train_count1, train_count2

    ball["x"] += ball["vx"]
    ball["y"] += ball["vy"]

    if ball["y"] <= 0 or ball["y"] >= HEIGHT:
        ball["vy"] = -ball["vy"]

    if ball["x"] <= 30 and paddles["player1"] <= ball["y"] <= paddles["player1"] + 100:
        ball["vx"] = -ball["vx"]
    if ball["x"] >= WIDTH - 30 and paddles["player2"] <= ball["y"] <= paddles["player2"] + 100:
        ball["vx"] = -ball["vx"]

    state1 = np.array([ball["x"], ball["y"], ball["vx"], ball["vy"], paddles["player1"]])
    if random.random() < epsilon:
        action1 = random.randint(0, 2)
    else:
        with torch.no_grad():
            action1 = torch.argmax(model1(torch.tensor(state1, dtype=torch.float32))).item()

    if action1 == 1:
        paddles["player1"] = max(0, paddles["player1"] - 5)
    elif action1 == 2:
        paddles["player1"] = min(300, paddles["player1"] + 5)

    state2 = np.array([ball["x"], ball["y"], ball["vx"], ball["vy"], paddles["player2"]])
    if random.random() < epsilon:
        action2 = random.randint(0, 2)
    else:
        with torch.no_grad():
            action2 = torch.argmax(model2(torch.tensor(state2, dtype=torch.float32))).item()

    if action2 == 1:
        paddles["player2"] = max(0, paddles["player2"] - 5)
    elif action2 == 2:
        paddles["player2"] = min(300, paddles["player2"] + 5)

    reward1, reward2 = 0, 0
    done = False

    if ball["x"] <= 0:
        reward1, reward2 = -1, 1
        train_count1 += 1
        remember(replay_buffer1, state1, action1, reward1, state1, True)
        executor.submit(train, replay_buffer1, model1, optimizer1)
        done = True
    elif ball["x"] >= WIDTH:
        reward1, reward2 = 1, -1
        train_count2 += 1
        remember(replay_buffer2, state2, action2, reward2, state2, True)
        executor.submit(train, replay_buffer2, model2, optimizer2)
        done = True

    next_state1 = np.array([ball["x"], ball["y"], ball["vx"], ball["vy"], paddles["player1"]])
    next_state2 = np.array([ball["x"], ball["y"], ball["vx"], ball["vy"], paddles["player2"]])

    if done:
        ball["x"], ball["y"] = WIDTH // 2, HEIGHT // 2
        ball["vx"] = 3 * (1 if random.choice([True, False]) else -1)
        ball["vy"] = 3 * (1 if random.choice([True, False]) else -1)

    epsilon = max(MIN_EPSILON, epsilon * EPSILON_DECAY)

async def game_loop():
    while True:
        update_game_state()
        await asyncio.sleep(1 / FPS)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await send_game_state(websocket)
            await asyncio.sleep(1 / FPS)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("WebSocket desconectado.")

@app.on_event("startup")
async def startup_event():
    load_models()
    asyncio.create_task(game_loop())

@app.on_event("shutdown")
async def shutdown_event():
    save_models()