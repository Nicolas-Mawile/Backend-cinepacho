"""Pagos endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/procesar")
async def procesar_pago():
    return {"message": "pago procesado"}
