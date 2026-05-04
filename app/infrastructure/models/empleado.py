"""Empleado model."""

from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.infrastructure.models.cargoEnum import CargoEnum
from app.infrastructure.models.persona import Persona

class Empleado(Persona):
    __tablename__ = "empleados"
    id = Column(Integer, ForeignKey('personas.id'), primary_key=True)

    codigoEmpleado = Column(String, nullable=False, unique=True)
    fechaIngreso = Column(String, nullable=False)
    cargo = Column(Enum(CargoEnum), nullable=False)
    correoEmpleado = Column(String, nullable=False, unique=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'empleado'
    }

    contratos = relationship("Contrato", back_populates="empleado")