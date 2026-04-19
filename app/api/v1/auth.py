"""Auth endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"message": "login"}


@router.post("/registro")
async def registro():
    return {"message": "registro"}


@router.post("/refresh")
async def refresh():
    return {"message": "refresh"}
