from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, Numeric
from app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

from app.infrastructure.models.cargoEnum import CargoEnum

class Contrato(Base):
    """
    Representa la relación contractual
    de un empleado dentro de un multiplex.
    """
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleadoId = Column(ForeignKey("empleados.id"), nullable=False)
    multiplexId = Column(ForeignKey("multiplex.id"), nullable=False)
    cargo = Column(Enum(CargoEnum), nullable=False)
    salario = Column(Numeric(12, 2), nullable=False)
    fechaInicio = Column(Date, nullable=False)
    fechaFin = Column(Date, nullable=True)
    activo = Column(Boolean, default=True)


    empleado = relationship("Empleado", back_populates="contratos")
    multiplex = relationship("Multiplex", back_populates="contratos")