"""Empleado model."""

from sqlalchemy import Column, String

from .base import Base, TimestampMixin


class Empleado(Base, TimestampMixin):
    nombre = Column(String, nullable=False)
