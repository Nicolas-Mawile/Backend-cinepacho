"""Compras API router."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.api.dependencies import requirePermission, getCurrentUserOptional
from app.infrastructure.models.usuario import Usuario
from app.domain.services.checkout_service import CheckoutService
from app.domain.services.pago_service import PagoService
from app.domain.services.factura_service import FacturaService
from app.api.schemas.compra import (CheckoutRequest, CheckoutResponse, PagarFacturaRequest, PagoResponse,
                                    ResumenCompraResponse, ConfirmacionCompraResponse, MisBoletasResponse,
                                    ConfirmarPagoResponse,FacturaBoletasResponse,)

router = APIRouter(tags=["Compras"])

# =========================================================
# DEPENDENCIES
# =========================================================

def get_checkout_service():
    db = SessionLocal()
    try:
        yield CheckoutService(db)
    finally:
        db.close()


def get_pago_service(db: Session = Depends(get_db)):
    return PagoService(db)

def get_factura_service(db: Session = Depends(get_db)):
    return FacturaService(db)

# =========================================================
# CHECKOUT — WEB
# =========================================================
@router.post(
    "/compras/checkout",
    response_model=CheckoutResponse,
    summary="Realizar checkout desde la web",
)
def checkout(
    request: CheckoutRequest,
    service: CheckoutService = Depends(get_checkout_service),
):
    try:

        return service.checkout(
            funcion_id=request.funcionId,
            silla_ids=request.sillaIds,
            comidas=request.comidas,
            permitir_solo_snacks=False,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# CHECKOUT — PUNTO ÁGIL
# Valida que la función pertenezca al multiplex del cajero
# =========================================================

@router.post(
    "/punto-agil/compras",
    response_model=CheckoutResponse,
    summary="Compra desde punto ágil (cajero)",
)
def checkout_punto_agil(
    request: CheckoutRequest,
    service: CheckoutService = Depends(get_checkout_service),
    usuario: Usuario = Depends(requirePermission("compra-snacks")),
):
    try:
        # Validar que si hay función, pertenezca al multiplex del cajero
        if request.funcionId and request.sillaIds:
            contrato = usuario.empleado.contratoActivo if usuario.empleado else None
            if contrato and request.funcionId:
                from app.infrastructure.repositories.funcion_repository import FuncionRepository
                db_local = service.db
                funcion_repo = FuncionRepository(db_local)
                funcion = funcion_repo.get_by_id(request.funcionId)
                if funcion and funcion.sala.multiplexId != contrato.multiplexId:
                    raise HTTPException(
                        status_code=403,
                        detail="La función no pertenece al multiplex asignado al cajero",
                    )

        return service.checkout(
            funcion_id=request.funcionId,
            silla_ids=request.sillaIds,
            comidas=request.comidas,
            permitir_solo_snacks=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# SOLICITAR PAGO
# =========================================================

@router.post(
    "/compras/{factura_id}/solicitar-pago",
    response_model=PagoResponse,
    summary="Solicitar pago y enviar email de confirmación",
)
def solicitar_pago(
    factura_id: int,
    request: PagarFacturaRequest,
    service: PagoService = Depends(get_pago_service),
):
    try:

        return service.pagar(
            factura_id=factura_id,
            metodo_pago=request.metodoPago,
            usarRecompensa= request.usarRecompensa,

            nombres=request.nombres,
            apellidos=request.apellidos,
            correo=request.correo,
            telefono=request.telefono,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# CONFIRMAR PAGO (link del correo)
# =========================================================

@router.get(
    "/compras/confirmar-pago",
    response_model=ConfirmarPagoResponse,
    summary="Confirmar pago via token del correo",
)
def confirmar_pago(
    token: str = Query(...),
    service: PagoService = Depends(get_pago_service),
):
    try:
        return service.confirmar_pago(token=token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# RESUMEN
# =========================================================

@router.get(
    "/compras/{factura_id}/resumen",
    response_model=ResumenCompraResponse,
    summary="Obtener resumen de compra (accesible para invitados)",
)
def obtener_resumen(
    factura_id: int,
    service: FacturaService = Depends(get_factura_service),
    usuario: Usuario | None = Depends(getCurrentUserOptional),
):
    try:
        cliente_id = None
        if usuario and usuario.cliente:
            cliente_id = usuario.cliente.id
        return service.obtener_resumen(factura_id=factura_id, cliente_id=cliente_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# CONFIRMACIÓN
# =========================================================

@router.get(
    "/compras/{factura_id}/confirmacion",
    response_model=ConfirmacionCompraResponse,
    summary="Obtener confirmación de compra pagada",
)
def obtener_confirmacion(
    factura_id: int,
    service: FacturaService = Depends(get_factura_service),
):
    try:

        return service.obtener_confirmacion(
            factura_id=factura_id,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# =========================================================
# MIS BOLETAS
# =========================================================

@router.get(
    "/clientes/me/boletas",
    response_model=list[MisBoletasResponse],
    summary="Obtener mis boletas compradas",
)
def obtener_mis_boletas(
    service: FacturaService = Depends(get_factura_service),
    usuario: Usuario = Depends(requirePermission("compra-boletas")),
):
    try:
        return service.obtener_mis_boletas(cliente_id=usuario.cliente.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# BOLETAS POR FACTURA
# =========================================================

@router.get(
    "/facturas/{factura_id}/boletas",
    response_model=FacturaBoletasResponse,
    summary="Obtener boletas de una factura específica",
)
def obtener_boletas_factura(
    factura_id: int,
    service: FacturaService = Depends(get_factura_service),
    usuario: Usuario = Depends(requirePermission("compra-boletas")),
):
    try:
        return service.obtener_boletas_factura(
            factura_id=factura_id,
            cliente_id=usuario.cliente.id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
