"""Pago model."""

from sqlalchemy import Column, Integer, ForeignKey, Float, String

from .base import Base, TimestampMixin


class Pago(Base, TimestampMixin):
    boleta_id = Column(Integer, ForeignKey("boleta.id"), nullable=False)
    monto = Column(Float, nullable=False)
    estado = Column(String, nullable=False)
