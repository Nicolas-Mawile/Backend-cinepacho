"""Empleado model."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.base import Base

class Empleado(Base, Persona):
    """
    Representa empleados internos de CinePacho.
    """
    __tablename__ = "empleados"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigoEmpleado = Column(String, unique=True, nullable=False)
    correoLaboral = Column(String, unique=True, nullable=False)

    clienteId = Column(Integer, ForeignKey("clientes.id"), nullable=False, unique =True)
    cliente = relationship("Cliente", back_populates="empleado")

    usuario = relationship("Usuario", back_populates="empleado", uselist=False)
    contratos = relationship("Contrato", back_populates="empleado")
    historial_cargos = relationship("HistorialCargo", back_populates="empleado")

    @property
    def contratoActivo(self):
        """Retorna el contrato activo del empleado."""
        return next((contrato for contrato in self.contratos if contrato.activo),None)

    @property
    def cargoActual(self):
        """Retorna el cargo actual del empleado."""
        contrato = self.contratoActivo
        return contrato.cargo if contrato else None

    @property
    def multiplexActual(self):
        """Retorna el multiplex actual del empleado."""
        contrato = self.contratoActivo
        return contrato.multiplex.nombre if contrato and contrato.multiplex else None
    
    @property
    def salarioActual(self):
        contrato = self.contratoActivo
        return float(contrato.salario) if contrato else None