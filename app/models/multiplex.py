"""Multiplex model."""

from sqlalchemy import Column, String

from .base import Base, TimestampMixin


class Multiplex(Base, TimestampMixin):
    nombre = Column(String, nullable=False)
