"""Endpoints de funciones."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.sala import Sala
from app.infrastructure.repositories.funcion_repository import FuncionRepository
from app.api.dependencies import requireRole

router = APIRouter(tags=["funciones"])


class FuncionCreate(BaseModel):
    peliculaId: int
    salaId: int
    fechaHora: datetime


@router.post("/funciones", status_code=201)
def crear_funcion(data: FuncionCreate, db: Session = Depends(get_db), _=Depends(requireRole(["ADMIN-MX"]))):
    repo = FuncionRepository(db)
    sala = db.get(Sala, data.salaId)
    if not sala or not sala.estaActiva:
        raise HTTPException(status_code=404, detail="Sala no encontrada o inactiva")
    pelicula = db.get(Pelicula, data.peliculaId)
    if not pelicula or not pelicula.estaActiva:
        raise HTTPException(status_code=400, detail="Pelicula no encontrada o inactiva")
    if not repo.pelicula_en_cartelera(data.peliculaId, sala.multiplexId):
        raise HTTPException(status_code=400, detail="La pelicula no esta en la cartelera de este multiplex")
    fecha_fin = data.fechaHora + timedelta(minutes=pelicula.duracionMinutos)
    if repo.hay_solapamiento(data.salaId, data.fechaHora, fecha_fin):
        raise HTTPException(status_code=409, detail="Ya existe una funcion programada en ese horario para esta sala")
    return repo.add(Funcion(peliculaId=data.peliculaId, salaId=data.salaId, fechaHora=data.fechaHora, fechaHoraFin=fecha_fin, estaActiva=True))


@router.get("/multiplex/{id}/funciones")
def funciones_por_multiplex(id: int, db: Session = Depends(get_db)):
    return FuncionRepository(db).listar_por_multiplex(id)


@router.get("/salas/{id}/funciones")
def funciones_por_sala(id: int, db: Session = Depends(get_db)):
    return FuncionRepository(db).listar_por_sala(id)


@router.delete("/funciones/{id}")
def eliminar_funcion(id: int, db: Session = Depends(get_db), _=Depends(requireRole(["ADMIN-MX"]))):
    repo = FuncionRepository(db)
    funcion = repo.get(id)
    if not funcion:
        raise HTTPException(status_code=404, detail="Funcion no encontrada")
    if repo.tiene_boletas(id):
        raise HTTPException(status_code=409, detail="No se puede eliminar: la funcion tiene boletas vendidas")
    repo.delete(id)
    return {"mensaje": "Funcion eliminada correctamente"}
