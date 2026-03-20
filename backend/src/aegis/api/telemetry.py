"""Telemetry WebSocket — streams real-time simulation state to the frontend.

The frontend connects once and receives a JSON message every simulation tick
containing all asset positions, statuses, alerts, and mission progress.
This is the backbone of the real-time operator experience.
"""

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Connected WebSocket clients
_clients: list[WebSocket] = []


@router.websocket("/ws")
async def telemetry_stream(ws: WebSocket):
    """Accept a WebSocket connection and stream telemetry updates.

    The simulation engine calls `broadcast_state()` every tick,
    which pushes to all connected clients.
    """
    await ws.accept()
    _clients.append(ws)
    print(f"[Telemetry] Client connected. Total: {len(_clients)}")

    try:
        # Keep connection alive — listen for client pings or close
        while True:
            # We don't expect messages from the client on this socket,
            # but we need to await to detect disconnects
            await ws.receive_text()
    except WebSocketDisconnect:
        _clients.remove(ws)
        print(f"[Telemetry] Client disconnected. Total: {len(_clients)}")


async def broadcast_state(state: dict) -> None:
    """Push a simulation state snapshot to all connected WebSocket clients.

    Called by the SimulationEngine on every tick.

    Args:
        state: Dictionary containing assets, alerts, mission progress, timestamp.
    """
    if not _clients:
        return

    payload = json.dumps(state)
    disconnected = []

    for client in _clients:
        try:
            await client.send_text(payload)
        except Exception:
            disconnected.append(client)

    for client in disconnected:
        _clients.remove(client)
