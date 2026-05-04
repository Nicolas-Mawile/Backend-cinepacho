from sqlalchemy import Column, Float, ForeignKey, Integer
from app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    clienteId = Column(ForeignKey("clientes.id"), nullable=False)

    cliente = relationship("Cliente", back_populates="facturas")    
    detalles = relationship("DetalleFactura", back_populates="factura")

    pagos = relationship("Pago", back_populates="factura")
