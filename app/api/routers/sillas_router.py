"""Sillas API router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime
from app.api.dependencies import requirePermission
from app.database import SessionLocal
from app.infrastructure.repositories.silla_repository import SillaRepository
from app.domain.services.sala_service import SalaService
from app.domain.exceptions import SalaNotFoundError
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.api.schemas.compra import DisponibilidadSillaResponse
from app.domain.services.checkout_service import CheckoutService
from app.api.routers.compras_router import get_checkout_service
from app.utils.timezone import nowColombia


router = APIRouter(tags=["Sillas"])


def get_silla_repository():
    """Obtiene instancia del repositorio de sillas."""
    db = SessionLocal()
    try:
        yield SillaRepository(db)
    finally:
        db.close()


def get_sala_service():
    """Obtiene instancia del servicio de salas."""
    db = SessionLocal()
    try:
        yield SalaService(db)
    finally:
        db.close()


@router.get(
    "/salas/{sala_id}/sillas/contar",
    response_model=dict,
    summary="Obtener cantidad de sillas de una sala",
    responses={
        200: {"description": "Cantidad de sillas y detalles"},
        404: {"description": "Sala no encontrada"},
    },
)
def contar_sillas_sala(
    sala_id: int,
    sala_service: SalaService = Depends(get_sala_service),
    _: Usuario = Depends(requirePermission("ver-detalles-sillas-sala")),
):
    """
    Obtiene la cantidad de sillas que se le van a cargar a una sala.
    
    - **sala_id**: ID de la sala
    
    Retorna:
    - `cantidad_total`: Total de sillas en la sala
    - `cantidad_activas`: Sillas activas
    - `cantidad_inactivas`: Sillas desactivadas
    - `tiene_boletas_vendidas`: Si hay boletas vendidas para funciones de esta sala
    - `dependencias`: Objeto con todos los detalles de dependencias
    
    **Nota**: Endpoint para admin - futuro control basado en roles
    """
    try:
        sala = sala_service.obtener_sala(sala_id)
        dependencias = sala_service.tiene_dependencias(sala_id)
        
        return {
            "sala_id": sala_id,
            "numero_sala": sala.numero,
            "cantidad_total": dependencias["cantidad_sillas"],
            "cantidad_activas": dependencias["cantidad_sillas_activas"],
            "cantidad_inactivas": dependencias["cantidad_sillas"] - dependencias["cantidad_sillas_activas"],
            "tiene_boletas_vendidas": dependencias["tiene_boletas_vendidas"],
            "dependencias": dependencias,
        }
    except SalaNotFoundError:
        raise HTTPException(status_code=404, detail="Sala no encontrada")


@router.get(
    "/multiplex/{multiplex_id}/sillas",
    response_model=list,
    summary="Listar sillas de un multiplex",
    responses={
        200: {"description": "Lista de sillas"},
    },
)
def listar_sillas_multiplex(
    multiplex_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    repo: SillaRepository = Depends(get_silla_repository),
    _: Usuario = Depends(requirePermission("listar-sillas-multiplex")),
):
    """
    Lista todas las sillas de un multiplex.
    
    - **multiplex_id**: ID del multiplex
    - **skip**: Sillas a saltar (paginación)
    - **limit**: Máximo de sillas a retornar (1-500)
    
    **Nota**: Endpoint para admin - futuro control basado en roles
    """
    sillas = repo.obtener_por_multiplex(multiplex_id, skip, limit)
    return [
        {
            "id": s.id,
            "fila": s.fila,
            "columna": s.columna,
            "estaActiva": s.estaActiva,
            "salaId": s.salaId,
            "tipoSillaId": s.tipoSillaId,
        }
        for s in sillas
    ]


@router.patch(
    "/multiplex/{multiplex_id}/sillas/estado",
    response_model=dict,
    summary="Desactivar todas las sillas de un multiplex",
    responses={
        200: {"description": "Sillas desactivadas"},
    },
)
def desactivar_sillas_multiplex(
    multiplex_id: int,
    repo: SillaRepository = Depends(get_silla_repository),
    _: Usuario = Depends(requirePermission("desactivar-sillas-multiplex")),
):
    """
    Desactiva todas las sillas activas de un multiplex.
    
    **Nota**: 
    - Endpoint administrativo para desactivar sillas en batch
    - Futuro control basado en roles del usuario
    - Solo desactiva, no elimina
    
    Retorna:
    - `cantidad_desactivadas`: Número de sillas desactivadas
    - `multiplex_id`: ID del multiplex afectado
    - `timestamp`: Marca de tiempo de la operación
    """
    from datetime import datetime
    
    cantidad = repo.desactivar_por_multiplex(multiplex_id)
    
    return {
        "cantidad_desactivadas": cantidad,
        "multiplex_id": multiplex_id,
        "timestamp": nowColombia().isoformat(),
        "mensaje": f"Se desactivaron {cantidad} sillas del multiplex {multiplex_id}",
    }


@router.get(
    "/salas/{sala_id}/sillas/detalles",
    response_model=dict,
    summary="Obtener detalles completos de sillas de una sala",
    responses={
        200: {"description": "Detalles de sillas"},
        404: {"description": "Sala no encontrada"},
    },
)
def obtener_detalles_sillas_sala(
    sala_id: int,
    sala_service: SalaService = Depends(get_sala_service),
    repo: SillaRepository = Depends(get_silla_repository),
    _: Usuario = Depends(requirePermission("ver-detalles-sillas-sala")),
):
    """
    Obtiene detalles completos sobre las sillas de una sala.
    
    **Nota**: Endpoint para admin - futuro control basado en roles
    
    Retorna información:
    - Total de sillas
    - Sillas activas/inactivas
    - Si tiene boletas vendidas
    - Lista de sillas (con paginación implícita)
    """
    try:
        sala = sala_service.obtener_sala(sala_id)
        dependencias = sala_service.tiene_dependencias(sala_id)
        sillas = repo.obtener_por_sala(sala_id, skip=0, limit=100)
        
        return {
            "sala_id": sala_id,
            "numero_sala": sala.numero,
            "multiplex_id": sala.multiplexId,
            "resumen": {
                "cantidad_total": dependencias["cantidad_sillas"],
                "cantidad_activas": dependencias["cantidad_sillas_activas"],
                "cantidad_inactivas": dependencias["cantidad_sillas"] - dependencias["cantidad_sillas_activas"],
                "tiene_boletas_vendidas": dependencias["tiene_boletas_vendidas"],
            },
            "sillas": [
                {
                    "id": s.id,
                    "fila": s.fila,
                    "columna": s.columna,
                    "activa": s.estaActiva,
                    "tipo_silla_id": s.tipoSillaId,
                }
                for s in sillas
            ],
        }
    except SalaNotFoundError:
        raise HTTPException(status_code=404, detail="Sala no encontrada")

@router.get(
    "/funciones/{funcion_id}/sillas/disponibilidad",
    response_model=list[DisponibilidadSillaResponse],
    summary="Obtener disponibilidad de sillas",
)
def obtener_disponibilidad_sillas(
    funcion_id: int,
    service: CheckoutService = Depends(
        get_checkout_service
    ),
    _: Usuario = Depends(
        requirePermission(
            "ver-detalle-funcion"
        )
    ),
):
    """
    Retorna disponibilidad de sillas:
    
    - DISPONIBLE
    - RESERVADA
    - OCUPADA
    """

    try:

        response = (
            service.obtener_disponibilidad(
                funcion_id
            )
        )

        return response

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
