from sqlalchemy import Column, Float, ForeignKey, Integer, DateTime, String, Enum
from app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

from app.infrastructure.models import EstadoFacturaEnum

class Factura(Base):
    """
    Representa compras realizadas
    en el sistema.
    """
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clienteId = Column(ForeignKey("clientes.id"), nullable=False)

    subTotal = Column(Float, nullable=False, default=0)
    descuento = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)

    fechaCreacion = Column(DateTime, nullable=False)
    fechaExpiracionReserva = Column(DateTime, nullable=True)
    codigoTransaccion = Column(String(100), nullable=False)
    estadoFactura = Column(Enum(EstadoFacturaEnum), nullable=False, default=EstadoFacturaEnum.RESERVADA)

    cliente = relationship("Cliente", back_populates="facturas")    
    detalles = relationship("DetalleFactura", back_populates="factura")
    pagos = relationship("Pago", back_populates="factura")
