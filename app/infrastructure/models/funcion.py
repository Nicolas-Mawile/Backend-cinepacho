"""Funcion model."""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from .base import Base
from sqlalchemy.orm import relationship

class Funcion(Base):
    __tablename__ = "funciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fechaHora = Column(DateTime, nullable=False)
    estaActiva = Column(Boolean, default=True, nullable=False)

    peliculaId = Column(Integer, ForeignKey("peliculas.id"), nullable=False)
    salaId = Column(Integer, ForeignKey("salas.id"), nullable=False)

    pelicula = relationship("Pelicula", back_populates="funciones")
    sala = relationship("Sala", back_populates="funciones")

    boletas = relationship("Boleta", back_populates="funcion")
