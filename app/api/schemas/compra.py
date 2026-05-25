"""Schemas de compras."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


# =========================================================
# PIEZAS BASE — deben ir primero
# =========================================================

class CompraComidaItem(BaseModel):
    comidaId: int
    cantidad: int


class ClienteCheckoutRequest(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: str


# =========================================================
# REQUESTS
# =========================================================

class CheckoutRequest(BaseModel):
    funcionId: Optional[int] = None
    sillaIds: List[int] = Field(default_factory=list)
    comidas: List[CompraComidaItem] = Field(default_factory=list)


class PagarFacturaRequest(BaseModel):
    metodoPago: str

    nombres: str
    apellidos: str
    correo: str
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
    descuento: float
    subtotalBoletas: float
    subtotalSnacks: float
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


class ConfirmarPagoResponse(BaseModel):
    mensaje: str
    facturaId: int
    codigoTransaccion: str
    estadoFactura: str
    total: float


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


class ResumenComidaResponse(BaseModel):
    comidaId: int
    nombre: str
    cantidad: int
    precioUnitario: float
    subtotal: float


class ResumenCompraResponse(BaseModel):
    facturaId: int
    estado: str
    subtotal: float
    descuento: float
    total: float
    expira: Optional[datetime]
    boletas: List[ResumenDetalleResponse]
    comidas: List[ResumenComidaResponse]


# =========================================================
# CONFIRMACIÓN
# =========================================================

class ConfirmacionComidaResponse(BaseModel):
    comidaId: int
    nombre: str
    cantidad: int
    subtotal: float


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
    boletas: List[ConfirmacionBoletaResponse]
    comidas: List[ConfirmacionComidaResponse]


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

# =========================================================
# BOLETAS POR FACTURA
# =========================================================
class BoletaFacturaResponse(BaseModel):
    boletaId: int
    pelicula: str
    sala: str
    fechaHora: datetime
    fila: str
    columna: int

class FacturaBoletasResponse(BaseModel):
    facturaId: int
    codigoTransaccion: str
    estado: str
    fechaCompra: datetime
    total: float
    boletas: List[BoletaFacturaResponse]

class MisComprasSnackResponse(BaseModel):
    facturaId: int
    comida: str
    cantidad: int
    subtotal: float
    fechaCompra: datetime
class SolicitarPagoRequest(BaseModel):
    metodoPago: str

    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: str