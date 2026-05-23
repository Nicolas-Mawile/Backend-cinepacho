"""Endpoints de cartelera."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import requirePermission
from app.api.schemas.cartelera import CarteleraAdd, CarteleraItemResponse
from app.api.schemas.pelicula import PeliculaResponse
from app.database import get_db
from app.domain.exceptions import (CarteleraNotFoundError, CarteleraValidationError, MultiplexNotFoundError)
from app.domain.services.cartelera_service import CarteleraService

router = APIRouter(tags=["cartelera"])


def _map_cartelera_error(exc: Exception):
    if isinstance(exc, (MultiplexNotFoundError, CarteleraNotFoundError)):
        raise HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, CarteleraValidationError):
        status_code = 409 if "ya esta" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc))
    raise exc


@router.get("/cartelera", response_model=list[PeliculaResponse])
def ver_cartelera_general(
    db: Session = Depends(get_db),):
    service = CarteleraService(db)
    return service.ver_cartelera_general()


@router.get("/multiplex/{multiplex_id}/cartelera", response_model=list[CarteleraItemResponse])
def ver_cartelera(
    multiplex_id: int,
    db: Session = Depends(get_db),):
    service = CarteleraService(db)
    try:
        return service.ver_cartelera_por_multiplex(multiplex_id)
    except Exception as exc:
        _map_cartelera_error(exc)


@router.post("/multiplex/{multiplex_id}/cartelera", status_code=201, response_model=CarteleraItemResponse)
def agregar_a_cartelera(
    multiplex_id: int,
    data: CarteleraAdd,
    db: Session = Depends(get_db),
    _: object = Depends(requirePermission("administrar-cartelera-multiplex")),
):
    service = CarteleraService(db)
    try:
        return service.agregar_a_cartelera(multiplex_id, data.peliculaId)
    except Exception as exc:
        _map_cartelera_error(exc)


@router.delete("/multiplex/{multiplex_id}/cartelera/{pelicula_id}")
def remover_de_cartelera(
    multiplex_id: int,
    pelicula_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requirePermission("administrar-cartelera-multiplex")),
):
    service = CarteleraService(db)
    try:
        service.remover_de_cartelera(multiplex_id, pelicula_id)
        return {"mensaje": "Pelicula removida de la cartelera correctamente"}
    except Exception as exc:
        _map_cartelera_error(exc)


@router.post("/cartelera/general", status_code=201)
def agregar_a_cartelera_general(
    data: CarteleraAdd,
    db: Session = Depends(get_db),
    _: object = Depends(requirePermission("administrar-cartelera-general")),
):
    service = CarteleraService(db)
    try:
        resultado = service.agregar_a_cartelera_general(data.peliculaId)
        return {
            "mensaje": "Pelicula agregada a la cartelera general",
            **resultado,
        }
    except Exception as exc:
        _map_cartelera_error(exc)


@router.delete("/cartelera/general/{pelicula_id}")
def remover_de_cartelera_general(
    pelicula_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requirePermission("administrar-cartelera-general")),
):
    service = CarteleraService(db)
    try:
        resultado = service.remover_de_cartelera_general(pelicula_id)
        return {
            "mensaje": "Pelicula removida de la cartelera general",
            **resultado,
        }
    except Exception as exc:
        _map_cartelera_error(exc)
