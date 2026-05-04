"""Sala model."""
from sqlalchemy import Boolean, Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Sala(Base):
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(Integer, nullable=False)
    estaActiva = Column(Boolean, default=True)
    capacidadTotal = Column(Integer, nullable=False)
    capacidadPreferencial = Column(Integer, nullable=False)

    multiplexId = Column(Integer, ForeignKey("multiplex.id"), nullable=False)
    multiplex = relationship("Multiplex", back_populates="salas")

    sillas = relationship("Silla", back_populates="sala")
    funciones = relationship("Funcion", back_populates="sala")

    __table_args__ = (
    UniqueConstraint('numero', 'multiplexId', name='uq_sala_numero_multiplex'),
)

    @property
    def cantidad_sillas(self) -> int:
        return len(self.sillas or [])

    @property
    def activa(self) -> bool:
        return self.estaActiva

    @activa.setter
    def activa(self, value: bool) -> None:
        self.estaActiva = value