"""Puntos endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_historial():
    return {"message": "historial de puntos"}


@router.get("/boletas")
async def get_boletas_regalo():
    return {"message": "boletas regalo"}
