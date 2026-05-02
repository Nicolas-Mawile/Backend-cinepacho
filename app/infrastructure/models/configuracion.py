"""Configuración del sistema model."""

from sqlalchemy import Column, String, Integer, Boolean

from .base import Base, TimestampMixin


class Configuracion(Base, TimestampMixin):
    clave = Column(String, nullable=False, unique=True, index=True)
    valor = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)  # Documentación
    tipo = Column(String, default="str")  # int, bool, str, decimal
    activo = Column(Boolean, default=True)  # Desactivar sin borrar
