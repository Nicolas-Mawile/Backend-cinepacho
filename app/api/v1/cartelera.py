"""Cartelera endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_cartelera():
    return {"message": "cartelera"}


@router.get("/peliculas")
async def get_peliculas():
    return {"message": "peliculas"}
