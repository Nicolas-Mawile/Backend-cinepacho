"""Empleado model."""

from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from cinepachobackend.app.models.cargo import Cargo
from cinepachobackend.app.models.persona import Persona

class Empleado(Persona):
    __tablename__ = "Empleados"
    id = Column(Integer, ForeignKey('personas.id'), primary_key=True)

    codigoEmpleado = Column(String, nullable=False, unique=True)
    fechaIngreso = Column(String, nullable=False)
    cargo = Column(Enum(Cargo), nullable=False)
    correoEmpleado = Column(String, nullable=False, unique=True)
    
    usuario = relationship("Usuario", back_populates="empleado", uselist=False)
    __mapper_args__ = {
        'polymorphic_identity': 'empleado'
    }

    contratos = relationship("Contrato", back_populates="empleado")