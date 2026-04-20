"""Cliente model."""
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from .base import Base, TimestampMixin

class Cliente(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    intentos_fallidos = Column(Integer, default=0)
    ultimo_intento = Column(DateTime(timezone=True), nullable=True)
    activo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime(timezone=True), nullable=True)