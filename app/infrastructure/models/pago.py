"""Pago model."""
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Float, String
from .base import Base
from enum import Enum
from .EstadoPagoEnum import EstadoPagoEnum
from sqlalchemy.orm import relationship

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    monto = Column(Float, nullable=False)
    estado = Column(Enum(EstadoPagoEnum), nullable=False)
    metodoPago = Column(String, nullable=False)
    fechaPago = Column(DateTime, nullable=False)

    facturaId = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    factura = relationship("Factura", back_populates="pagos")