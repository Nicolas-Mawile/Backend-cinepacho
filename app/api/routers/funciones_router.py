"""Endpoints de funciones."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import requirePermission
from app.api.schemas.funcion import FuncionCreate, FuncionResponse, FuncionUpdate, FuncionDetalleResponse
from app.database import get_db
from app.domain.exceptions import (
    FuncionNotFoundError,
    FuncionValidationError,
    MultiplexNotFoundError,
    SalaNotFoundError,
)
from app.domain.services.funcion_service import FuncionService

router = APIRouter(tags=["funciones"])


def _map_funcion_error(exc: Exception):
    if isinstance(exc, (FuncionNotFoundError, SalaNotFoundError, MultiplexNotFoundError)):
        raise HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, FuncionValidationError):
        message = str(exc).lower()
        status_code = 409 if any(token in message for token in ["dependencias", "solapamiento", "ya existe", "ya esta", "boletas vendidas"]) else 400
        raise HTTPException(status_code=status_code, detail=str(exc))
    raise exc


@router.post("/funciones", status_code=201, response_model=FuncionResponse)
def crear_funcion(data: FuncionCreate, db: Session = Depends(get_db), _=Depends(requirePermission("crear-funcion"))):
    service = FuncionService(db)
    try:
        return service.crear_funcion(data)
    except Exception as exc:
        _map_funcion_error(exc)


@router.get("/multiplex/{id}/funciones", response_model=list[FuncionResponse])
def funciones_por_multiplex(id: int, db: Session = Depends(get_db), ):
    service = FuncionService(db)
    try:
        return service.listar_por_multiplex(id)
    except Exception as exc:
        _map_funcion_error(exc)


@router.get("/salas/{id}/funciones", response_model=list[FuncionResponse])
def funciones_por_sala(id: int, db: Session = Depends(get_db), ):
    service = FuncionService(db)
    try:
        return service.listar_por_sala(id)
    except Exception as exc:
        _map_funcion_error(exc)


@router.get("/peliculas/{pelicula_id}/funciones", response_model=list[FuncionResponse])
def funciones_por_pelicula(
    pelicula_id: int,
    db: Session = Depends(get_db),
):
    service = FuncionService(db)
    try:
        return service.listar_por_pelicula(pelicula_id)
    except Exception as exc:
        _map_funcion_error(exc)

@router.get("/funciones/{id}", response_model=FuncionDetalleResponse,)
def obtener_funcion_por_id(id: int, db: Session = Depends(get_db),):
    service = FuncionService(db)
    try:
        return service.obtener_por_id(id)
    except Exception as exc:
        _map_funcion_error(exc)


@router.get("/multiplex/{multiplex_id}/peliculas/{pelicula_id}/funciones", response_model=list[FuncionResponse])
def funciones_pelicula_por_multiplex(
    multiplex_id: int,
    pelicula_id: int,
    db: Session = Depends(get_db),
):
    service = FuncionService(db)
    try:
        return service.listar_por_pelicula_y_multiplex(multiplex_id, pelicula_id)
    except Exception as exc:
        _map_funcion_error(exc)


@router.put("/funciones/{id}", response_model=FuncionResponse)
def editar_funcion(
    id: int,
    data: FuncionUpdate,
    db: Session = Depends(get_db),
    _=Depends(requirePermission("actualizar-funcion")),
):
    service = FuncionService(db)
    try:
        return service.editar_funcion(id, data)
    except Exception as exc:
        _map_funcion_error(exc)


@router.delete("/funciones/{id}")
def eliminar_funcion(id: int, db: Session = Depends(get_db), _=Depends(requirePermission("cambiar-estado-funcion"))):
    service = FuncionService(db)
    try:
        service.eliminar_funcion(id)
        return {"mensaje": "Funcion eliminada correctamente"}
    except Exception as exc:
        _map_funcion_error(exc)
