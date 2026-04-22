"""Sala model."""

import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Sala(Base):
    __tablename__ = "sala"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    nombre = Column(String, nullable=False)

    capacidad_general = Column(Integer, default=40)
    capacidad_preferencial = Column(Integer, default=20)

    # relaciones
    multiplex_id = Column(String, ForeignKey("multiplex.id"), nullable=False)
    multiplex = relationship("Multiplex", back_populates="salas")

    sillas = relationship("Silla", back_populates="sala", cascade="all, delete")
