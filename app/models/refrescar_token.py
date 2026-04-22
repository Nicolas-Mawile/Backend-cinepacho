"""RefreshToken model."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from .base import Base, TimestampMixin

class RefreshToken(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revocado = Column(Boolean, default=False)