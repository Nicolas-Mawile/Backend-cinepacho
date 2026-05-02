"""Configuración del sistema model."""

from sqlalchemy import Column, String, Integer

from .base import Base, TimestampMixin


class Configuracion(Base, TimestampMixin):
    clave = Column(String, nullable=False, unique=True)
    valor = Column(String, nullable=False)
