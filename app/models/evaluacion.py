"""Evaluación model."""

from sqlalchemy import Column, Integer, String, ForeignKey

from .base import Base, TimestampMixin


class Evaluacion(Base, TimestampMixin):
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    texto = Column(String, nullable=False)
    puntuacion = Column(Integer, nullable=False)
