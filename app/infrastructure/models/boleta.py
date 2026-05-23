"""Boleta model."""
from sqlalchemy import Column, Integer, ForeignKey, Float, UniqueConstraint
from .base import Base
from sqlalchemy.orm import relationship

class Boleta(Base):
    __tablename__ = "boletas"
    __table_args__ = (
        UniqueConstraint(
            "funcionId",
            "sillaId",
            name="uq_boleta_funcion_silla"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)    
    funcionId = Column(Integer, ForeignKey("funciones.id"), nullable=False)
    sillaId = Column(Integer, ForeignKey("sillas.id"), nullable=False)

    funcion = relationship("Funcion", back_populates="boletas")
    silla = relationship("Silla", back_populates="boletas")

    detalle = relationship("DetalleFactura", back_populates="boleta", uselist=False)

