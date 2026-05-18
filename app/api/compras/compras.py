"""Compras API router."""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.database import SessionLocal

from app.api.dependencies import requirePermission

from app.infrastructure.models.usuario import Usuario

from app.domain.services.checkout_service import CheckoutService

from app.api.schemas.compra import (
    CheckoutRequest,
    CheckoutResponse,

    PagarFacturaRequest,
    PagoResponse,

    ResumenCompraResponse,

    ConfirmacionCompraResponse,

    MisBoletasResponse
)


router = APIRouter(
    prefix="/api/v1",
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
    usuario: Usuario = Depends(
        requirePermission(
            "compra-boletas"
        )
    ),
):

    try:

        response = service.checkout(
            cliente_id=usuario.cliente.id,
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
# PAGAR
# =========================================================

@router.post(
    "/compras/{factura_id}/pagar",
    response_model=PagoResponse,
    summary="Pagar compra",
)
def pagar_compra(
    factura_id: int,
    request: PagarFacturaRequest,
    service: CheckoutService = Depends(
        get_checkout_service
    ),
    usuario: Usuario = Depends(
        requirePermission(
            "pagar-orden"
        )
    ),
):

    try:

        response = service.pagar(
            factura_id=factura_id,
            cliente_id=usuario.cliente.id
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
    usuario: Usuario = Depends(
        requirePermission(
            "compra-boletas"
        )
    ),
):

    try:

        response = service.obtener_resumen(
            factura_id=factura_id,
            cliente_id=usuario.cliente.id
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