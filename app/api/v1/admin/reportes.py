"""Admin reportes endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def obtener_reportes():
    return {"message": "reportes"}
