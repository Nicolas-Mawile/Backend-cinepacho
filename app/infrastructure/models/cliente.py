"""Cliente model."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from .base import Base
from sqlalchemy.orm import relationship

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)
    puntos_acumulados = Column(Integer, default=0)
    idioma_preferido = Column(String, default="es")

    evaluaciones = relationship("Evaluacion", back_populates="cliente")
    facturas = relationship("Factura", back_populates="cliente")