"""Empleado model."""

from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.infrastructure.models.cargoEnum import CargoEnum
from app.infrastructure.models.persona import Persona

class Empleado(Persona):
    """
    Representa empleados internos de CinePacho.
    """
    __tablename__ = "empleados"
    id = Column(Integer, ForeignKey('personas.id'), primary_key=True)
    usuarioId = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    codigoEmpleado = Column(String, unique=True, nullable=False)
    correoLaboral = Column(String, unique=True, nullable=False)

    usuario = relationship("Usuario", back_populates="empleado", foreign_keys=[usuarioId])
    contratos = relationship("Contrato", back_populates="empleado")
    historial_cargos = relationship(
        "HistorialCargo",
        back_populates="empleado"
    )

    __mapper_args__ = {
        "polymorphic_identity": "empleado"
    }

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