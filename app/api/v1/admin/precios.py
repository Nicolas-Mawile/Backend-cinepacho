"""Admin precios endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def obtener_precios():
    return {"message": "precios"}


@router.post("")
async def actualizar_precios():
    return {"message": "precios actualizados"}
