"""Puntos model."""

from sqlalchemy import Column, Integer, ForeignKey

from .base import Base, TimestampMixin


class Puntos(Base, TimestampMixin):
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    saldo = Column(Integer, default=0)
