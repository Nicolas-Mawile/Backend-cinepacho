from sqlalchemy import Column, ForeignKey, String
from app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

class Contrato(Base):
    __tablename__ = "contratos"

    fechaInicio = Column(String, nullable=False)
    fechaFin = Column(String, nullable=True)
    salario = Column(String, nullable=False)

    empleadoId = Column(ForeignKey("empleados.id"), nullable=False)
    empleado = relationship("Empleado", back_populates="contratos")
    
    multiplexId = Column(ForeignKey("multiplex.id"), nullable=False)
    multiplex = relationship("Multiplex", back_populates="contratos")