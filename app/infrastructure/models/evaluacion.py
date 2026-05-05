"""Evaluación model."""
from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship

class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    comentario = Column(String, nullable=False)
    puntuacion = Column(Integer, nullable=False)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="evaluaciones")

    pelicula_id = Column(Integer, ForeignKey("peliculas.id"), nullable=True)
    pelicula = relationship("Pelicula", back_populates="evaluaciones")

    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=True)
    servicio = relationship("Servicio", back_populates="evaluaciones")
    
