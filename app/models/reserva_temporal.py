"""Reserva temporal model."""

from sqlalchemy import Column, Integer, ForeignKey, DateTime

from .base import Base, TimestampMixin


class ReservaTemporal(Base, TimestampMixin):
    funcion_id = Column(Integer, ForeignKey("funcion.id"), nullable=False)
    silla_id = Column(Integer, ForeignKey("silla.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
