from typing import List
from fastapi import WebSocket, WebSocketDisconnect

connections: List[WebSocket] = []

async def handle_websocket(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connections.remove(ws)

async def broadcast_state(state):
    data = {"grid": state.grid.tolist()}
    for conn in connections:
        await conn.send_json(data)
