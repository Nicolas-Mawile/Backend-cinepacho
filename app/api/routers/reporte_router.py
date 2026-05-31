from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.database import get_db

from app.api.dependencies import (
    requirePermission
)

from app.infrastructure.models.usuario import (
    Usuario
)

from app.domain.services.reporte_service import (
    ReporteService
)

from app.domain.services.reporte_pdf_service import (
    ReportePdfService
)

from app.api.schemas.reporte import (
    ReporteMovilidadResponse,
    ReporteVentasMensualesResponse,
    RendimientoMultiplexResponse
)

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)


def get_reporte_service(
    db: Session = Depends(get_db)
):
    return ReporteService(db)


def get_reporte_pdf_service(
    db: Session = Depends(get_db)
):
    return ReportePdfService(db)


# =====================================================
# REPORTES JSON
# =====================================================

@router.get(
    "/empleados/movilidad",
    response_model=ReporteMovilidadResponse,
    summary="Reporte estadístico de empleados"
)
def obtener_movilidad_empleados(
    service: ReporteService = Depends(
        get_reporte_service
    ),
    _: Usuario = Depends(
        requirePermission(
            "ver-listado-empleados"
        )
    ),
):
    try:

        return (
            service.obtener_movilidad_empleados()
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/ventas-mensuales",
    response_model=ReporteVentasMensualesResponse,
    summary="Reporte mensual de ventas"
)
def obtener_ventas_mensuales(
    mes: int = Query(
        ...,
        ge=1,
        le=12
    ),
    anio: int = Query(
        ...,
        ge=2025
    ),
    service: ReporteService = Depends(
        get_reporte_service
    ),
    _: Usuario = Depends(
        requirePermission(
            "ver-listado-empleados"
        )
    ),
):
    try:

        return (
            service.obtener_ventas_mensuales(
                mes=mes,
                anio=anio,
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/multiplex-mensual",
    response_model=list[
        RendimientoMultiplexResponse
    ],
    summary="Reporte de rendimiento por multiplex"
)
def obtener_rendimiento_multiplex(
    mes: int = Query(
        ...,
        ge=1,
        le=12
    ),
    anio: int = Query(
        ...,
        ge=2025
    ),
    service: ReporteService = Depends(
        get_reporte_service
    ),
    _: Usuario = Depends(
        requirePermission(
            "ver-listado-empleados"
        )
    ),
):
    try:

        return (
            service.obtener_rendimiento_multiplex(
                mes=mes,
                anio=anio,
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# PDF MOVILIDAD
# =====================================================

@router.get(
    "/pdf/movilidad",
    summary="Descargar reporte PDF de movilidad"
)
def descargar_pdf_movilidad(
    service: ReportePdfService = Depends(
        get_reporte_pdf_service
    ),
    _: Usuario = Depends(
        requirePermission(
            "ver-listado-empleados"
        )
    ),
):

    pdf = service.generar_pdf_movilidad()

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=reporte_movilidad.pdf"
        }
    )


# =====================================================
# PDF OPERACIONAL
# =====================================================

@router.get(
    "/pdf/operacional",
    summary="Descargar reporte operacional mensual"
)
def descargar_pdf_operacional(
    mes: int = Query(
        ...,
        ge=1,
        le=12
    ),
    anio: int = Query(
        ...,
        ge=2025
    ),
    service: ReportePdfService = Depends(
        get_reporte_pdf_service
    ),
    _: Usuario = Depends(
        requirePermission(
            "ver-listado-empleados"
        )
    ),
):

    pdf = service.generar_pdf_operacional(
        mes=mes,
        anio=anio,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=reporte_operacional_{mes}_{anio}.pdf"
        }
    )


# =====================================================
# PDF MULTIPLEX
# =====================================================

@router.get(
    "/pdf/multiplex",
    summary="Descargar reporte desempeño multiplex"
)
def descargar_pdf_multiplex(
    mes: int = Query(
        ...,
        ge=1,
        le=12
    ),
    anio: int = Query(
        ...,
        ge=2025
    ),
    service: ReportePdfService = Depends(
        get_reporte_pdf_service
    ),
    _: Usuario = Depends(
        requirePermission(
            "ver-listado-empleados"
        )
    ),
):

    pdf = service.generar_pdf_desempeno_multiplex(
        mes=mes,
        anio=anio,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=reporte_multiplex_{mes}_{anio}.pdf"
        }
    )