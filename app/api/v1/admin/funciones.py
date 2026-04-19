"""Admin funciones endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def programar_funcion():
    return {"message": "función programada"}
