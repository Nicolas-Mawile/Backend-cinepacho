"""Endpoints de funciones."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta
from app.database import get_db
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.repositories.funcion_repository import FuncionRepository
from app.api.dependencies import requireRole
from app.api.schemas.funcion import FuncionCreate, FuncionUpdate

router = APIRouter(tags=["funciones"])


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


@router.get("/peliculas/{pelicula_id}/funciones")
def funciones_por_pelicula(pelicula_id: int, db: Session = Depends(get_db)):
    pelicula = db.get(Pelicula, pelicula_id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Pelicula no encontrada")

    result = db.execute(
        select(Funcion).where(Funcion.peliculaId == pelicula_id)
    )
    return result.scalars().all()


@router.get("/multiplex/{multiplex_id}/peliculas/{pelicula_id}/funciones")
def funciones_pelicula_por_multiplex(
    multiplex_id: int,
    pelicula_id: int,
    db: Session = Depends(get_db),
):
    multiplex = db.get(Multiplex, multiplex_id)
    if not multiplex:
        raise HTTPException(status_code=404, detail="Multiplex no encontrado")

    pelicula = db.get(Pelicula, pelicula_id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Pelicula no encontrada")

    result = db.execute(
        select(Funcion)
        .join(Sala, Sala.id == Funcion.salaId)
        .where(
            Sala.multiplexId == multiplex_id,
            Funcion.peliculaId == pelicula_id,
        )
    )
    return result.scalars().all()


@router.put("/funciones/{id}")
def editar_funcion(
    id: int,
    data: FuncionUpdate,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-MX"])),
):
    repo = FuncionRepository(db)
    funcion = repo.get(id)
    if not funcion:
        raise HTTPException(status_code=404, detail="Funcion no encontrada")

    if repo.tiene_boletas(id):
        raise HTTPException(status_code=409, detail="No se puede editar: la funcion tiene dependencias")

    nueva_sala_id = data.salaId if data.salaId is not None else funcion.salaId
    nueva_pelicula_id = data.peliculaId if data.peliculaId is not None else funcion.peliculaId
    nueva_fecha_hora = data.fechaHora if data.fechaHora is not None else funcion.fechaHora

    sala = db.get(Sala, nueva_sala_id)
    if not sala or not sala.estaActiva:
        raise HTTPException(status_code=404, detail="Sala no encontrada o inactiva")

    pelicula = db.get(Pelicula, nueva_pelicula_id)
    if not pelicula or not pelicula.estaActiva:
        raise HTTPException(status_code=400, detail="Pelicula no encontrada o inactiva")

    if not repo.pelicula_en_cartelera(nueva_pelicula_id, sala.multiplexId):
        raise HTTPException(status_code=400, detail="La pelicula no esta en la cartelera de este multiplex")

    nueva_fecha_fin = nueva_fecha_hora + timedelta(minutes=pelicula.duracionMinutos)
    if repo.hay_solapamiento(nueva_sala_id, nueva_fecha_hora, nueva_fecha_fin, excluir_id=id):
        raise HTTPException(status_code=409, detail="Ya existe una funcion programada en ese horario para esta sala")

    cambios = {
        "salaId": nueva_sala_id,
        "peliculaId": nueva_pelicula_id,
        "fechaHora": nueva_fecha_hora,
        "fechaHoraFin": nueva_fecha_fin,
    }

    return repo.update(id, cambios)


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
