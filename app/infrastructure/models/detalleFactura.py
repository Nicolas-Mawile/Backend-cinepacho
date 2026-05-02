from sqlalchemy import Column, ForeignKey, Integer
from cinepachobackend.app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

class DetalleFactura(Base):
    __tablename__ = "detalle_facturas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    cantidad = Column(Integer, nullable=False, default=1)

    facturaId = Column(Integer, ForeignKey("facturas.id"), nullable=False)

    boletaId = Column(Integer, ForeignKey("boletas.id"), nullable=True)
    comidaId = Column(Integer, ForeignKey("comidas.id"), nullable=True)

    factura = relationship("Factura", back_populates="detalles")

    boleta = relationship("Boleta", back_populates="detalle")
    comida = relationship("Comida", back_populates="detalles")