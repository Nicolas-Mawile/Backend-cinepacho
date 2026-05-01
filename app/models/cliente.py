"""Cliente model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from cinepachobackend.app.models.persona import Persona
from sqlalchemy.orm import relationship

class Cliente(Persona):
    __tablename__ = "clientes"
    id = Column(Integer, ForeignKey('personas.id'), primary_key=True)
    puntaje = Column(Integer, nullable=False, default=0)

    usuario = relationship("Usuario", back_populates="cliente", uselist=False, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'cliente'
    }