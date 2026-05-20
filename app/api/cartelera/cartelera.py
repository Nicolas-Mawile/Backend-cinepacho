"""Endpoints de cartelera por multiplex."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.database import get_db
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.multiplex import Multiplex
from app.api.dependencies import requireRole

router = APIRouter(tags=["cartelera"])


class CarteleraAdd(BaseModel):
    peliculaId: int


@router.get("/multiplex/{multiplex_id}/cartelera")
def ver_cartelera(multiplex_id: int, db: Session = Depends(get_db)):
    multiplex = db.get(Multiplex, multiplex_id)
    if not multiplex:
        raise HTTPException(status_code=404, detail="Multiplex no encontrado")
    result = db.execute(
        select(MultiplexCartelera).where(MultiplexCartelera.multiplexId == multiplex_id)
    )
    return result.scalars().all()


@router.post("/multiplex/{multiplex_id}/cartelera", status_code=201)
def agregar_a_cartelera(
    multiplex_id: int,
    data: CarteleraAdd,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-MX"]))
):
    multiplex = db.get(Multiplex, multiplex_id)
    if not multiplex:
        raise HTTPException(status_code=404, detail="Multiplex no encontrado")

    pelicula = db.get(Pelicula, data.peliculaId)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Pelicula no encontrada")
    if not pelicula.estaActiva:
        raise HTTPException(status_code=400, detail="No se puede agregar una pelicula inactiva a la cartelera")

    existing = db.execute(
        select(MultiplexCartelera).where(
            and_(
                MultiplexCartelera.multiplexId == multiplex_id,
                MultiplexCartelera.peliculaId == data.peliculaId,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="La pelicula ya esta en la cartelera de este multiplex")

    entrada = MultiplexCartelera(multiplexId=multiplex_id, peliculaId=data.peliculaId)
    db.add(entrada)
    db.commit()
    db.refresh(entrada)
    return entrada


@router.delete("/multiplex/{multiplex_id}/cartelera/{pelicula_id}")
def remover_de_cartelera(
    multiplex_id: int,
    pelicula_id: int,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-MX"]))
):
    entrada = db.execute(
        select(MultiplexCartelera).where(
            and_(
                MultiplexCartelera.multiplexId == multiplex_id,
                MultiplexCartelera.peliculaId == pelicula_id,
            )
        )
    ).scalar_one_or_none()

    if not entrada:
        raise HTTPException(status_code=404, detail="La pelicula no esta en la cartelera de este multiplex")

    db.delete(entrada)
    db.commit()
    return {"mensaje": "Pelicula removida de la cartelera correctamente"}
