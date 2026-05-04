"""Multiplex model."""

from sqlalchemy import Boolean, Column, Integer, String, Float

from .base import Base
from sqlalchemy.orm import relationship


class Multiplex(Base):
    __tablename__ = "multiplex"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, nullable=False, unique=True)
    nombre = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    direccion = Column(String, nullable=False) 
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    estaActivo = Column(Boolean, default=True)

    salas = relationship("Sala", back_populates="multiplex")
    contratos = relationship("Contrato", back_populates="multiplex")