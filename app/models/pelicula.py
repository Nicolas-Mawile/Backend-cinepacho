"""Pelicula model."""

from sqlalchemy import Column, String, Integer

from .base import Base, TimestampMixin


class Pelicula(Base, TimestampMixin):
    titulo = Column(String, nullable=False)
    duracion_minutos = Column(Integer, nullable=False)
