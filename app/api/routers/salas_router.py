"""Salas API router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import requirePermission
from app.api.schemas.sala import SalaCreate, SalaUpdate, SalaResponse
from app.database import SessionLocal
from app.domain.services.sala_service import SalaService
from app.domain.exceptions import (SalaNotFoundError, MultiplexNotFoundError, SalaLimitExceededError, DuplicateNumeroSalaError, SalaConfigurationError,)
from app.infrastructure.models.usuario import Usuario

router = APIRouter(tags=["Salas"])

def get_service():
    """Obtiene instancia del servicio de salas."""
    db = SessionLocal()
    try:
        yield SalaService(db)
    finally:
        db.close()

# Mapeo de excepciones de dominio a respuestas HTTP
def handle_domain_error(exc: Exception):
    """Convierte excepciones de dominio a respuestas HTTP."""
    if isinstance(exc, MultiplexNotFoundError):
        raise HTTPException(status_code=404, detail="Multiplex no encontrado")
    elif isinstance(exc, SalaNotFoundError):
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    elif isinstance(exc, SalaLimitExceededError):
        raise HTTPException(status_code=409, detail=str(exc))
    elif isinstance(exc, DuplicateNumeroSalaError):
        raise HTTPException(status_code=409, detail=str(exc))
    elif isinstance(exc, SalaConfigurationError):
        raise HTTPException(status_code=400, detail=str(exc))
    raise exc


@router.post("/multiplex/{multiplex_id}/salas", response_model=SalaResponse, status_code=status.HTTP_201_CREATED, 
             summary="Crear sala en un multiplex", responses={
                 201: {"description": "Sala creada exitosamente"},
                 404: {"description": "Multiplex no encontrado"},
                 409: {"description": "Conflicto: límite de salas alcanzado o número duplicado"},},)
def crear_sala(multiplex_id: int, datos: SalaCreate, service: SalaService = Depends(get_service), _: Usuario = Depends(requirePermission("crear-sala")),):
    """
    Crea una nueva sala en un multiplex.
    
    - **multiplex_id**: ID del multiplex propietario
    - **numero**: Número de sala (1-999)
    - **capacidadTotal**: Capacidad total
    - **capacidadPreferencial**: Capacidad de sillas preferenciales (≤ capacidadTotal)
    
    Validaciones:
    - El multiplex debe existir
    - No se puede exceder el límite de 10 salas por multiplex
    - El número de sala debe ser único
    """
    try:
        sala = service.crear_sala(multiplex_id, datos)
        return sala
    except (MultiplexNotFoundError, SalaLimitExceededError, DuplicateNumeroSalaError, SalaConfigurationError) as e:
        handle_domain_error(e)


@router.get("/multiplex/{multiplex_id}/salas", response_model=list[SalaResponse], summary="Listar salas por multiplex",
            responses={200: {"description": "Lista de salas"}, 404: {"description": "Multiplex no encontrado"},},)
def listar_salas_multiplex(multiplex_id: int, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), service: SalaService = Depends(get_service),):
    """
    Lista todas las salas de un multiplex.
    
    - **multiplex_id**: ID del multiplex
    - **skip**: Salas a saltar (para paginación)
    - **limit**: Máximo de salas a retornar (1-100)
    """
    try:
        salas = service.obtener_salas_multiplex(multiplex_id, skip, limit)
        return salas
    except MultiplexNotFoundError as e:
        handle_domain_error(e)

@router.get("/salas/{sala_id}", response_model=SalaResponse, summary="Obtener una sala específica", 
            responses={200: {"description": "Sala encontrada"}, 404: {"description": "Sala no encontrada"},},)
def obtener_sala(sala_id: int, service: SalaService = Depends(get_service),):
    """
    Obtiene los datos de una sala específica.
    
    - **sala_id**: ID de la sala
    """
    try:
        sala = service.obtener_sala(sala_id)
        return sala
    except SalaNotFoundError as e:
        handle_domain_error(e)


@router.put("/salas/{sala_id}", response_model=SalaResponse, summary="Actualizar una sala",
            responses={200: {"description": "Sala actualizada"}, 404: {"description": "Sala no encontrada"}, 409: {"description": "Conflicto: número duplicado"},},)
def actualizar_sala(sala_id: int, datos: SalaUpdate, service: SalaService = Depends(get_service), _: Usuario = Depends(requirePermission("actualizar-sala")),):
    """
    Actualiza una sala existente.
    
    - **sala_id**: ID de la sala
    - Todos los campos son opcionales
    """
    try:
        sala = service.actualizar_sala(sala_id, datos)
        return sala

    except SalaNotFoundError:
        raise HTTPException(status_code=404, detail="Sala no encontrada")

    except SalaConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/salas/{sala_id}", status_code=status.HTTP_200_OK, summary="Eliminar una sala",
               responses={200: {"description": "Sala eliminada"}, 404: {"description": "Sala no encontrada"},},)
def eliminar_sala(sala_id: int, service: SalaService = Depends(get_service), _: Usuario = Depends(requirePermission("eliminar-sala")),):
    """
    Elimina una sala.
    - **sala_id**: ID de la sala
    **Nota**: Por ahora no valida dependencias (funciones, sillas).
    """
    if not service.eliminar_sala(sala_id):
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return {"message": "Sala eliminada"}


@router.patch("/salas/{sala_id}/estado", response_model=SalaResponse, summary="Cambiar estado de una sala",
              responses={200: {"description": "Estado actualizado"}, 404: {"description": "Sala no encontrada"},},)
def cambiar_estado_sala(sala_id: int, activo: bool = Query(..., description="Nuevo estado: True (activa) o False (inactiva)"),
                        service: SalaService = Depends(get_service), _: Usuario = Depends(requirePermission("cambiar-estado-sala")),):
    """
    Cambia el estado de una sala (activa/inactiva).
    
    - **sala_id**: ID de la sala
    - **activo**: True para activar, False para desactivar
    """
    try:
        sala = service.cambiar_estado(sala_id, activo)
        return sala
    except SalaNotFoundError as e:
        handle_domain_error(e)
