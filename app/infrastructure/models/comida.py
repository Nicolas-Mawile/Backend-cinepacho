"""Snack model."""
from sqlalchemy import Column, Integer, String, Float, Boolean
from .base import Base
from sqlalchemy.orm import relationship

class Comida(Base):
    __tablename__ = "comidas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    precio = Column(Float, nullable=False)
    imagenUrl = Column(String, nullable=True)
    estaActiva = Column(Boolean, default=True, nullable=False)
    detalles = relationship("DetalleFactura", back_populates="comida")
