"""Reservas endpoints."""

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.post("")
async def create_reserva():
    return {"message": "reserva creada"}


@router.websocket("/ws/sillas")
async def websocket_sillas(websocket: WebSocket):
    await websocket.accept()
    await websocket.close()
