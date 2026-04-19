"""Boleta model."""

from sqlalchemy import Column, Integer, ForeignKey, Float

from .base import Base, TimestampMixin


class Boleta(Base, TimestampMixin):
    reserva_id = Column(Integer, ForeignKey("reserva_temporal.id"), nullable=False)
    total = Column(Float, nullable=False)
