"""Endpoints de funciones."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from datetime import datetime
from app.database import get_db
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.sala import Sala
from app.infrastructure.repositories.funcion_repository import FuncionRepository
from app.api.dependencies import get_current_admin_mx, get_current_admin_general

router = APIRouter(tags=["funciones"])


class FuncionCreate(BaseModel):
    peliculaId: int
    salaId: int
    fechaHora: datetime


@router.post("/funciones", status_code=201)
def crear_funcion(
    data: FuncionCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin_mx)
):
    repo = FuncionRepository(db)

    # Verificar sala
    sala = db.get(Sala, data.salaId)
    if not sala or not sala.estaActiva:
        raise HTTPException(status_code=404, detail="Sala no encontrada o inactiva")

    # Verificar película activa
    pelicula = db.get(Pelicula, data.peliculaId)
    if not pelicula or not pelicula.estaActiva:
        raise HTTPException(status_code=400, detail="Película no encontrada o inactiva")

    # Verificar película en cartelera del multiplex
    if not repo.pelicula_en_cartelera(data.peliculaId, sala.multiplexId):
        raise HTTPException(status_code=400, detail="La película no está en la cartelera de este multiplex")

    # Calcular hora de fin
    from datetime import timedelta
    fecha_fin = data.fechaHora + timedelta(minutes=pelicula.duracionMinutos)

    # Verificar solapamiento
    if repo.hay_solapamiento(data.salaId, data.fechaHora, fecha_fin):
        raise HTTPException(status_code=409, detail="Ya existe una función programada en ese horario para esta sala")

    funcion = Funcion(
        peliculaId=data.peliculaId,
        salaId=data.salaId,
        fechaHora=data.fechaHora,
        fechaHoraFin=fecha_fin,
        estaActiva=True,
    )
    return repo.add(funcion)


@router.get("/multiplex/{id}/funciones")
def funciones_por_multiplex(id: int, db: Session = Depends(get_db)):
    repo = FuncionRepository(db)
    return repo.listar_por_multiplex(id)


@router.get("/salas/{id}/funciones")
def funciones_por_sala(id: int, db: Session = Depends(get_db)):
    repo = FuncionRepository(db)
    return repo.listar_por_sala(id)


@router.delete("/funciones/{id}")
def eliminar_funcion(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin_mx)
):
    repo = FuncionRepository(db)
    funcion = repo.get(id)
    if not funcion:
        raise HTTPException(status_code=404, detail="Función no encontrada")
    if repo.tiene_boletas(id):
        raise HTTPException(status_code=409, detail="No se puede eliminar: la función tiene boletas vendidas")
    repo.delete(id)
    return {"mensaje": "Función eliminada correctamente"}