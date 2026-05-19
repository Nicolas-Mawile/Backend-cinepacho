"""Endpoints de cartelera por multiplex."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.database import get_db
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.multiplex import Multiplex
from app.api.dependencies import requireRole
from app.api.schemas.cartelera import CarteleraAdd

router = APIRouter(tags=["cartelera"])


@router.get("/cartelera")
def ver_cartelera_general(db: Session = Depends(get_db)):
    result = db.execute(
        select(Pelicula)
        .join(MultiplexCartelera, MultiplexCartelera.peliculaId == Pelicula.id)
        .distinct()
    )
    return result.scalars().all()


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


@router.post("/cartelera/general", status_code=201)
def agregar_a_cartelera_general(
    data: CarteleraAdd,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-GENERAL"]))
):
    pelicula = db.get(Pelicula, data.peliculaId)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Pelicula no encontrada")
    if not pelicula.estaActiva:
        raise HTTPException(status_code=400, detail="No se puede agregar una pelicula inactiva a la cartelera")

    multiplex_ids = db.execute(
        select(Multiplex.id).where(Multiplex.estaActivo == True)
    ).scalars().all()

    if not multiplex_ids:
        raise HTTPException(status_code=404, detail="No hay multiplex activos para actualizar cartelera")

    existentes = db.execute(
        select(MultiplexCartelera.multiplexId).where(
            and_(
                MultiplexCartelera.peliculaId == data.peliculaId,
                MultiplexCartelera.multiplexId.in_(multiplex_ids),
            )
        )
    ).scalars().all()

    existentes_set = set(existentes)
    nuevos = [
        MultiplexCartelera(multiplexId=multiplex_id, peliculaId=data.peliculaId)
        for multiplex_id in multiplex_ids
        if multiplex_id not in existentes_set
    ]

    if nuevos:
        db.add_all(nuevos)
        db.commit()

    return {
        "mensaje": "Pelicula agregada a la cartelera general",
        "peliculaId": data.peliculaId,
        "multiplexesActualizados": len(nuevos),
        "multiplexesSinCambio": len(existentes_set),
    }


@router.delete("/cartelera/general/{pelicula_id}")
def remover_de_cartelera_general(
    pelicula_id: int,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-GENERAL"]))
):
    entradas = db.execute(
        select(MultiplexCartelera).where(MultiplexCartelera.peliculaId == pelicula_id)
    ).scalars().all()

    if not entradas:
        raise HTTPException(status_code=404, detail="La pelicula no esta en la cartelera general")

    for entrada in entradas:
        db.delete(entrada)

    db.commit()

    return {
        "mensaje": "Pelicula removida de la cartelera general",
        "peliculaId": pelicula_id,
        "multiplexesAfectados": len(entradas),
    }
