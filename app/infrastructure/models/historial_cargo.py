"""Historial de cargos de empleados."""

from sqlalchemy import Column, ForeignKey, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base
from .cargoEnum import CargoEnum

class HistorialCargo(Base):
    __tablename__ = "historial_cargos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    cargo_anterior = Column(Enum(CargoEnum), nullable=True)
    cargo_nuevo = Column(Enum(CargoEnum), nullable=False)
    multiplex_id = Column(Integer, ForeignKey("multiplex.id"), nullable=True)
    fecha_cambio = Column(DateTime, server_default=func.now())
    motivo = Column(String, nullable=True)
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    empleado = relationship("Empleado", back_populates="historial_cargos")
    multiplex = relationship("Multiplex")
    registrado_por = relationship("Usuario")
