"""Admin configuracion endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_configuracion():
    return {"message": "configuración del sistema"}


@router.post("")
async def update_configuracion():
    return {"message": "configuración actualizada"}
