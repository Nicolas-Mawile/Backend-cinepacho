"""Funcion model."""

from sqlalchemy import Column, Integer, ForeignKey, DateTime

from .base import Base, TimestampMixin


class Funcion(Base, TimestampMixin):
    sala_id = Column(Integer, ForeignKey("sala.id"), nullable=False)
    pelicula_id = Column(Integer, ForeignKey("pelicula.id"), nullable=False)
    inicio = Column(DateTime, nullable=False)
