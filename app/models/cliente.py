"""Cliente model."""

from sqlalchemy import Column, String

from .base import Base, TimestampMixin


class Cliente(Base, TimestampMixin):
    nombre = Column(String, nullable=False)
