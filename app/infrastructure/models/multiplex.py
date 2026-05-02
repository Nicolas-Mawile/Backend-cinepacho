"""Multiplex model."""

from sqlalchemy import Boolean, Column, Integer, String

from .base import Base
from sqlalchemy.orm import relationship


class Multiplex(Base):
    __tablename__ = "Multiplex"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    latitud = Column(float, nullable=False)
    longitud = Column(float, nullable=False)
    estaActivo = Column(Boolean, default=True)

    salas = relationship("Sala", back_populates="multiplex")
    contratos = relationship("Contrato", back_populates="multiplex")