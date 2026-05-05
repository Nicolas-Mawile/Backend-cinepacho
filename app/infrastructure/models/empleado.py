"""Empleado model."""

from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.infrastructure.models.cargoEnum import CargoEnum
from app.infrastructure.models.persona import Persona

class Empleado(Persona):
    __tablename__ = "empleados"
    id = Column(Integer, ForeignKey('personas.id'), primary_key=True)

    cedula = Column(String, unique=True, nullable=False)
    nombre_completo = Column(String, nullable=False)
    fecha_inicio_contrato = Column(Date, nullable=False)
    salario = Column(Numeric(12, 2), nullable=False)
    cargo = Column(Enum(CargoEnum), nullable=False)
    activo = Column(Boolean, default=True)
    multiplex_id = Column(Integer, ForeignKey("multiplex.id"), nullable=True)
    correo_laboral = Column(String, unique=True, nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'empleado'
    }

    multiplex = relationship("Multiplex")
    contratos = relationship("Contrato", back_populates="empleado")
    historial_cargos = relationship("HistorialCargo", back_populates="empleado")