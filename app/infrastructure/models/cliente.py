"""Cliente model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from app.infrastructure.models.persona import Persona
from sqlalchemy.orm import relationship

class Cliente(Persona):
    __tablename__ = "clientes"
    id = Column(Integer, ForeignKey('personas.id'), primary_key=True)
    puntaje = Column(Integer, nullable=False, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'cliente'
    }

    evaluaciones = relationship("Evaluacion", back_populates="cliente")
    facturas = relationship("Factura", back_populates="cliente")