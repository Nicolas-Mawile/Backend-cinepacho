"""Snacks endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_snacks():
    return {"message": "snacks"}


@router.post("")
async def create_snack():
    return {"message": "snack creado"}
