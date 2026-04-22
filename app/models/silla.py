"""Silla model."""

import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Silla(Base):
    __tablename__ = "silla"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    fila = Column(String, nullable=False)
    numero = Column(String, nullable=False)

    tipo = Column(String, nullable=False)

    sala_id = Column(String, ForeignKey("sala.id"), nullable=False)

    sala = relationship("Sala", back_populates="sillas")