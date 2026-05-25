"""Endpoints de evaluaciones."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.dependencies import requirePermission
from app.infrastructure.models.usuario import Usuario
from app.api.schemas.evaluacion import (
    EvaluarPeliculaRequest,
    EvaluarServicioRequest,
    EvaluacionResponse,
)
from app.domain.services.evaluacion_service import EvaluacionService

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


def _get_cliente_id(usuario: Usuario) -> int:
    """
    Extrae el clienteId del usuario.
    Solo clientes registrados pueden evaluar.
    """
    if not usuario.clienteId:
        raise HTTPException(
            status_code=403,
            detail="Solo los clientes registrados pueden evaluar",
        )
    return usuario.clienteId


@router.post("/pelicula", response_model=EvaluacionResponse, summary="Evaluar una película")
def evaluar_pelicula(
    data: EvaluarPeliculaRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requirePermission("calificar")),
):
    cliente_id = _get_cliente_id(usuario)
    service = EvaluacionService(db)
    return service.evaluar_pelicula(
        cliente_id=cliente_id,
        funcion_id=data.funcionId,
        pelicula_id=data.peliculaId,
        puntuacion=data.puntuacion,
        comentario=data.comentario,
    )


@router.post("/servicio", response_model=EvaluacionResponse, summary="Evaluar un servicio")
def evaluar_servicio(
    data: EvaluarServicioRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requirePermission("calificar")),
):
    cliente_id = _get_cliente_id(usuario)
    service = EvaluacionService(db)
    return service.evaluar_servicio(
        cliente_id=cliente_id,
        factura_id=data.facturaId,
        servicio_id=data.servicioId,
        puntuacion=data.puntuacion,
        comentario=data.comentario,
    )


# =========================================================
# PELÍCULAS EVALUABLES
# =========================================================

@router.get(
    "/peliculas-evaluables",
    summary="Películas que el cliente puede evaluar",
)
def obtener_peliculas_evaluables(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requirePermission("calificar")),
):

    cliente_id = _get_cliente_id(usuario)

    service = EvaluacionService(db)

    return service.obtener_peliculas_evaluables(
        cliente_id=cliente_id
    )


# =========================================================
# SERVICIOS EVALUABLES
# =========================================================

@router.get(
    "/servicios-evaluables",
    summary="Servicios que el cliente puede evaluar",
)
def obtener_servicios_evaluables(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requirePermission("calificar")),
):

    cliente_id = _get_cliente_id(usuario)

    service = EvaluacionService(db)

    return service.obtener_servicios_evaluables(
        cliente_id=cliente_id
    )


# =========================================================
# MIS EVALUACIONES
# =========================================================

@router.get(
    "/mis-evaluaciones",
    summary="Obtener mis evaluaciones",
)
def obtener_mis_evaluaciones(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requirePermission("calificar")),
):

    cliente_id = _get_cliente_id(usuario)

    service = EvaluacionService(db)

    return service.obtener_mis_evaluaciones(
        cliente_id=cliente_id
    )