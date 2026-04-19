"""Silla model."""

from sqlalchemy import Column, Integer, ForeignKey, Boolean

from .base import Base, TimestampMixin


class Silla(Base, TimestampMixin):
    sala_id = Column(Integer, ForeignKey("sala.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    disponible = Column(Boolean, default=True)
