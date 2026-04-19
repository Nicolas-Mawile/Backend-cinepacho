"""Clientes endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/perfil")
async def obtener_perfil():
    return {"message": "perfil del cliente"}


@router.patch("/perfil")
async def actualizar_perfil():
    return {"message": "perfil actualizado"}


@router.get("/mis-compras")
async def mis_compras():
    return {"message": "mis compras"}
