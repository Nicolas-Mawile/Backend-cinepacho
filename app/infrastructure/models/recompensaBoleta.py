from sqlalchemy import (Column, Integer, DateTime, Boolean, ForeignKey)
from sqlalchemy.orm import relationship
from app.infrastructure.models.base import Base

class RecompensaBoleta(Base):

    __tablename__ = "recompensas_boleta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clienteId = Column(ForeignKey("clientes.id"), nullable=False)
    fechaOtorgamiento = Column(DateTime, nullable=False)
    fechaVencimiento = Column(DateTime, nullable=False)
    utilizada = Column(Boolean, nullable=False, default=False)
    
    cliente = relationship(
        "Cliente",
        back_populates="recompensas"
    )