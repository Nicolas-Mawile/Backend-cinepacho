"""Silla model."""

import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Silla(Base):
    __tablename__ = "silla"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    fila = Column(String, nullable=False)   # A, B, C...
    numero = Column(String, nullable=False) # 1, 2, 3...

    tipo = Column(String, nullable=False)  # GENERAL | PREFERENCIAL

    sala_id = Column(String, ForeignKey("sala.id"), nullable=False)

    sala = relationship("Sala", back_populates="sillas")