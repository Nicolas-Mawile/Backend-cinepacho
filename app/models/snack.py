"""Snack model."""

from sqlalchemy import Column, String, Float

from .base import Base, TimestampMixin


class Snack(Base, TimestampMixin):
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
