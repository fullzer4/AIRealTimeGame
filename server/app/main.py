import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from config import GameConfig
from state import GameState
from teams import TeamParams
from logic import GameLogic
import uvicorn
from ws_manager import handle_websocket, broadcast_state

config = GameConfig()
game_state = GameState(config.WIDTH, config.HEIGHT)
params_team_x = TeamParams(aggressiveness=config.INITIAL_TEAM_X_AGG)
params_team_y = TeamParams(aggressiveness=config.INITIAL_TEAM_Y_AGG)
game_logic = GameLogic(game_state, params_team_x, params_team_y, config)

async def game_loop():
    iteration = 0
    while True:
        if config.game_ended:
            break

        game_logic.update_grid(iteration)

        x_count = game_state.count_team_cells(1)
        y_count = game_state.count_team_cells(2)
        params_team_x.update_strategy(x_count)
        params_team_y.update_strategy(y_count)

        await broadcast_state(game_state)

        iteration += 1
        await asyncio.sleep(config.TICK_RATE)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(game_loop())
    yield

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await handle_websocket(ws)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
