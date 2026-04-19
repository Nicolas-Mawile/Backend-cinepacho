"""Admin empleados endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def listar_empleados():
    return {"message": "lista empleados"}


@router.patch("/cambio-cargo")
async def cambiar_cargo():
    return {"message": "cargo actualizado"}
