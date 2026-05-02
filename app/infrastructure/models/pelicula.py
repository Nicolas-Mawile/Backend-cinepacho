"""Pelicula model."""
from sqlalchemy import Column, String, Integer
from .base import Base
from sqlalchemy.orm import relationship

class Pelicula(Base):
    __tablename__ = "Peliculas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    titulo = Column(String, nullable=False)
    duracionMinutos = Column(Integer, nullable=False)
    linkTrailer = Column(String, nullable=True)
    linkPoster = Column(String, nullable=True)
    sinopsis = Column(String, nullable=True)

    evaluaciones = relationship("Evaluacion", back_populates="pelicula")
    funciones = relationship("Funcion", back_populates="pelicula")