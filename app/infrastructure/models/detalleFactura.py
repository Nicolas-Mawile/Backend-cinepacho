from sqlalchemy import Column, ForeignKey, Integer, Float
from app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

class DetalleFactura(Base):
    __tablename__ = "detalle_facturas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    cantidad = Column(Integer, nullable=False, default=1)
    precioUnitario = Column(Float, nullable=False)
    subTotal = Column(Float, nullable=False)

    facturaId = Column(Integer, ForeignKey("facturas.id"), nullable=False)

    boletaId = Column(Integer, ForeignKey("boletas.id"), nullable=True)
    comidaId = Column(Integer, ForeignKey("comidas.id"), nullable=True)

    factura = relationship("Factura", back_populates="detalles")

    boleta = relationship("Boleta", back_populates="detalle")
    comida = relationship("Comida", back_populates="detalles")