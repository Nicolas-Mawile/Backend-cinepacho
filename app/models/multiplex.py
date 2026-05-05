"""Multiplex model."""
from sqlalchemy import Column, String, Integer, Boolean
from .base import Base, TimestampMixin

class Multiplex(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    ciudad = Column(String, nullable=True)
    activo = Column(Boolean, default=True)