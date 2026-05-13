"""RefreshToken model."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from .base import Base, TimestampMixin

class RefreshToken(Base, TimestampMixin):
    """
    Tokens de refresco asociados
    a usuarios autenticados.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuarioId = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tokenHash = Column(String, nullable=False)
    expiresAt = Column(DateTime, nullable=False)
    revocado = Column(Boolean, default=False)