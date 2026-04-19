"""Sala model."""

from sqlalchemy import Column, Integer, String, ForeignKey

from .base import Base, TimestampMixin


class Sala(Base, TimestampMixin):
    multiplex_id = Column(Integer, ForeignKey("multiplex.id"), nullable=False)
    nombre = Column(String, nullable=False)
