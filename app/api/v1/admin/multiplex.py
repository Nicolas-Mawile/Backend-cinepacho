"""Admin multiplex endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def listar_multiplex():
    return {"message": "lista multiplex"}


@router.post("")
async def crear_multiplex():
    return {"message": "multiplex creado"}
