"""Evaluaciones endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def crear_evaluacion():
    return {"message": "evaluación creada"}
