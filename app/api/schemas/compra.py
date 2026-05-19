"""Schemas de compras."""

from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr

from typing import List


# =========================================================
# REQUESTS
# =========================================================

class CheckoutRequest(BaseModel):

    funcionId: int

    sillaIds: List[int]


class PagarFacturaRequest(BaseModel):

    metodoPago: str

    correo: EmailStr


class ConfirmarPagoRequest(BaseModel):

    nombres: str

    apellidos: str

    correo: EmailStr

    telefono: str


# =========================================================
# DISPONIBILIDAD
# =========================================================

class DisponibilidadSillaResponse(BaseModel):

    sillaId: int

    fila: str

    columna: int

    estado: str


# =========================================================
# CHECKOUT
# =========================================================

class CheckoutResponse(BaseModel):

    mensaje: str

    facturaId: int

    estado: str

    expira: datetime

    subtotal: float

    total: float


# =========================================================
# PAGO
# =========================================================

class PagoResponse(BaseModel):

    mensaje: str

    facturaId: int

    pagoId: int

    estadoPago: str

    expira: datetime


# =========================================================
# RESUMEN
# =========================================================

class ResumenDetalleResponse(BaseModel):

    boletaId: int

    funcionId: int

    pelicula: str

    sala: str

    fechaHora: datetime

    sillaId: int

    fila: str

    columna: int

    subtotal: float


class ResumenCompraResponse(BaseModel):

    facturaId: int

    estado: str

    subtotal: float

    descuento: float

    total: float

    expira: datetime | None

    detalles: List[
        ResumenDetalleResponse
    ]


# =========================================================
# CONFIRMACIÓN
# =========================================================

class ConfirmacionBoletaResponse(BaseModel):

    boletaId: int

    funcionId: int

    pelicula: str

    sala: str

    fechaHora: datetime

    sillaId: int

    fila: str

    columna: int


class ConfirmacionFacturaResponse(BaseModel):

    id: int

    total: float

    estado: str

    codigoTransaccion: str

    fecha: datetime


class ConfirmacionCompraResponse(BaseModel):

    factura: ConfirmacionFacturaResponse

    boletas: List[
        ConfirmacionBoletaResponse
    ]


# =========================================================
# MIS BOLETAS
# =========================================================

class MisBoletasResponse(BaseModel):

    boletaId: int

    facturaId: int

    funcionId: int

    pelicula: str

    sala: str

    fechaHora: datetime

    sillaId: int

    fila: str

    columna: int

    fechaCompra: datetime