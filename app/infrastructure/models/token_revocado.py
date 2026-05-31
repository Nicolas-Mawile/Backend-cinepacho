"""Modelo para tokens de acceso revocados (blacklist de logout)."""
from sqlalchemy import Column, String, DateTime, Integer
from .base import Base, TimestampMixin


class TokenRevocado(Base, TimestampMixin):
    __tablename__ = "tokens_revocados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String, nullable=False, unique=True, index=True)
    expiresAt = Column(DateTime, nullable=False)
