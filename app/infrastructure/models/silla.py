"""Silla model."""
from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Silla(Base):
    __tablename__ = "sillas"
    __table_args__ = (UniqueConstraint("fila", "columna", "salaId", name="uq_silla_sala"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    fila = Column(Integer, nullable=False)
    columna = Column(Integer, nullable=False)
    estaActiva = Column(Boolean, default=True)

    salaId = Column(Integer, ForeignKey("salas.id"), nullable=False)
    sala = relationship("Sala", back_populates="sillas")

    tipoSillaId = Column(Integer, ForeignKey("tipoSilla.id"), nullable=False)
    tipoSilla = relationship("TipoSilla")

    boletas = relationship("Boleta", back_populates="silla")

    @property
    def tipo_silla(self) -> str | None:
        return self.tipoSilla.nombre if self.tipoSilla is not None else None
