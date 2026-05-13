"""Historial de cargos de empleados."""

from sqlalchemy import Column, ForeignKey, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base
from .cargoEnum import CargoEnum

class HistorialCargo(Base):
    """
    Historial de cambios de cargo
    de empleados.
    """
    __tablename__ = "historial_cargos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleadoId = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    cargoAnterior = Column(Enum(CargoEnum), nullable=True)
    cargoNuevo = Column(Enum(CargoEnum), nullable=False)
    multiplexId = Column(Integer, ForeignKey("multiplex.id"), nullable=True)
    fechaCambio = Column(DateTime, server_default=func.now())
    motivo = Column(String, nullable=True)
    registradoPorId = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    empleado = relationship("Empleado", back_populates="historial_cargos")
    registrado_por = relationship("Usuario")
