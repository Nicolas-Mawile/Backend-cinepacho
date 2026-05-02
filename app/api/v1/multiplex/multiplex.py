"""Admin multiplex endpoints."""
from app.api.schemas.multiplex import (
    MultiplexCreate, MultiplexUpdate, MultiplexResponse
)
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_admin_general
from app.infrastructure.repositories.multiplex_repository import MultiplexRepository
from app.domain.services.multiplex_service import generar_codigo
from app.infrastructure.models import Multiplex

import uuid

from fastapi import APIRouter

router = APIRouter(prefix="/admin/multiplex", tags=["Admin - Multiplex"])

def get_repository():
    from app.infrastructure.repositories.multiplex_repository import MultiplexRepository
    from app.database import SessionLocal 
    db = SessionLocal()
    try:
        yield MultiplexRepository(db)
    finally:
        db.close()


@router.get("/", response_model=list[MultiplexResponse])
def listar_multiplex(ciudad: str | None = Query(None), activo: bool | None = Query(None),
                           pagina: int = Query(1, ge=1), limite: int = Query(20, ge=1, le=100),
                           repo: MultiplexRepository = Depends(get_repository),
                           _: dict = Depends(get_current_admin_general),):
    
    return repo.listar(ciudad=ciudad, activo=activo, limite=limite)

@router.post("/", response_model=MultiplexResponse, status_code=201)
def crear_multiplex(datos: MultiplexCreate, repo: MultiplexRepository = Depends(get_repository),
                          _: dict = Depends(get_current_admin_general),):
    
    code = generar_codigo(datos.nombre, repo)
    multiplex = Multiplex(**datos.model_dump(), codigo=code)
    return repo.crear(multiplex)

@router.put("/{id}", response_model=MultiplexResponse)
def editar_multiplex(id: str, datos: MultiplexUpdate,
                           repo: MultiplexRepository = Depends(get_repository),
                           _: dict = Depends(get_current_admin_general),):
    
    existente = repo.buscar_por_id(id)
    if not existente:
        raise HTTPException(404, "Multiplex no encontrado")
    actualizado = repo.update(id, datos.model_dump(exclude_none=True))
    return actualizado

@router.delete("/{id}", status_code=204)
def eliminar_multiplex(id: str, repo: MultiplexRepository = Depends(get_repository),
                             _: dict = Depends(get_current_admin_general),):
    
    existente = repo.buscar_por_id(id)
    if not existente:
        raise HTTPException(404, "Multiplex no encontrado")
    if repo.tiene_dependencias(id):
        raise HTTPException(
            409,
            "No se puede eliminar: el multiplex tiene salas activas. "
            "Use PATCH /{id}/estado para desactivarlo."
        )
    repo.desactivar(id)

@router.patch("/{id}/estado", response_model=MultiplexResponse)
def cambiar_estado_multiplex(
    id: int,
    activo: bool,
    repo: MultiplexRepository = Depends(get_repository),
    _: dict = Depends(get_current_admin_general),
):
    multiplex = repo.buscar_por_id(id)

    if not multiplex:
        raise HTTPException(status_code=404, detail="Multiplex no encontrado")

    multiplex = repo.update(id, {"activo": activo})

    return multiplex