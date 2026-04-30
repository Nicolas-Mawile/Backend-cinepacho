"""Multiplex model."""

from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import UUID, Boolean, Column, DateTime, Numeric, String

from .base import Base, TimestampMixin
import uuid


class Multiplex(Base, TimestampMixin):
    __tablename__ = "multiplex"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)

    latitud = Column(Numeric(9, 6), nullable=False)
    longitud = Column(Numeric(9, 6), nullable=False)

    activo = Column(Boolean, default=True)
    fechaCreacion = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

    salas = relationship("Sala", back_populates="multiplex")
