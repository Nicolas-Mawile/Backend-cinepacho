"""Compras API router."""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from app.database import SessionLocal

from app.api.dependencies import (
    requirePermission,
    getCurrentUserOptional
)

from app.infrastructure.models.usuario import Usuario

from app.domain.services.checkout_service import (
    CheckoutService
)

from app.api.schemas.compra import (
    CheckoutRequest,
    CheckoutResponse,

    PagarFacturaRequest,
    PagoResponse,

    ResumenCompraResponse,

    ConfirmacionCompraResponse,

    MisBoletasResponse,

    ConfirmarPagoRequest
)

router = APIRouter(
    tags=["Compras"]
)


# =========================================================
# DEPENDENCIES
# =========================================================

def get_checkout_service():

    db = SessionLocal()

    try:

        yield CheckoutService(db)

    finally:

        db.close()


# =========================================================
# CHECKOUT
# =========================================================

@router.post(
    "/compras/checkout",
    response_model=CheckoutResponse,
    summary="Realizar checkout temporal",
)
def checkout(
    request: CheckoutRequest,
    service: CheckoutService = Depends(
        get_checkout_service
    ),
    usuario: Usuario | None = Depends(
        getCurrentUserOptional
    ),
):

    try:

        cliente_id = None

        if (
            usuario
            and
            usuario.cliente
        ):

            cliente_id = usuario.cliente.id

        response = service.checkout(
            cliente_id=cliente_id,
            funcion_id=request.funcionId,
            silla_ids=request.sillaIds,
        )

        return response

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# SOLICITAR PAGO
# =========================================================

@router.post(
    "/compras/{factura_id}/solicitar-pago",
    response_model=PagoResponse,
    summary="Solicitar pago",
)
def solicitar_pago(
    factura_id: int,
    request: PagarFacturaRequest,
    service: CheckoutService = Depends(
        get_checkout_service
    ),
    usuario: Usuario | None = Depends(
        getCurrentUserOptional
    ),
):

    try:

        cliente_id = None

        if (
            usuario
            and
            usuario.cliente
        ):

            cliente_id = usuario.cliente.id

        response = service.pagar(
            factura_id=factura_id,
            metodo_pago=request.metodoPago,
            correo=request.correo,
            cliente_id=cliente_id
        )

        return response

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# CONFIRMAR PAGO
# =========================================================

@router.post(
    "/compras/confirmar-pago",
    response_model=PagoResponse,
    summary="Confirmar pago",
)
def confirmar_pago(
    token: str = Query(...),
    request: ConfirmarPagoRequest = ...,
    service: CheckoutService = Depends(
        get_checkout_service
    ),
):

    try:

        response = service.confirmar_pago(
            token=token,
            nombres=request.nombres,
            apellidos=request.apellidos,
            correo=request.correo,
            telefono=request.telefono
        )

        return response

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# CONFIRMACIÓN
# =========================================================

@router.get(
    "/compras/{factura_id}/confirmacion",
    response_model=ConfirmacionCompraResponse,
    summary="Obtener confirmación de compra",
)
def obtener_confirmacion(
    factura_id: int,
    service: CheckoutService = Depends(
        get_checkout_service
    ),
    usuario: Usuario = Depends(
        requirePermission(
            "compra-boletas"
        )
    ),
):

    try:

        response = (
            service.obtener_confirmacion(
                factura_id=factura_id,
                cliente_id=usuario.cliente.id
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


# =========================================================
# RESUMEN
# =========================================================

@router.get(
    "/compras/{factura_id}/resumen",
    response_model=ResumenCompraResponse,
    summary="Obtener resumen de compra",
)
def obtener_resumen(
    factura_id: int,
    service: CheckoutService = Depends(
        get_checkout_service
    ),
    usuario: Usuario | None = Depends(
        getCurrentUserOptional
    ),
):

    try:

        cliente_id = None

        if (
            usuario
            and
            usuario.cliente
        ):

            cliente_id = usuario.cliente.id

        response = service.obtener_resumen(
            factura_id=factura_id,
            cliente_id=cliente_id
        )

        return response

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# MIS BOLETAS
# =========================================================

@router.get(
    "/clientes/me/boletas",
    response_model=list[MisBoletasResponse],
    summary="Obtener mis boletas",
)
def obtener_mis_boletas(
    service: CheckoutService = Depends(
        get_checkout_service
    ),
    usuario: Usuario = Depends(
        requirePermission(
            "compra-boletas"
        )
    ),
):

    try:

        response = (
            service.obtener_mis_boletas(
                cliente_id=usuario.cliente.id
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