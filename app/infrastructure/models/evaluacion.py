"""Evaluación model."""
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from .base import Base
from sqlalchemy.orm import relationship

class Evaluacion(Base):
    __tablename__ = "evaluaciones"
    __table_args__ = (

        UniqueConstraint(
            "cliente_id",
            "funcion_id",
            "pelicula_id",
            name="uq_cliente_funcion_pelicula",
        ),

        UniqueConstraint(
            "cliente_id",
            "factura_id",
            "servicio_id",
            name="uq_cliente_factura_servicio",
        ),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    comentario = Column(String, nullable=False)
    puntuacion = Column(Integer, nullable=False)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="evaluaciones")

    pelicula_id = Column(Integer, ForeignKey("peliculas.id"), nullable=True)
    pelicula = relationship("Pelicula", back_populates="evaluaciones")
    funcion_id = Column(Integer, ForeignKey("funciones.id"), nullable=True)
    funcion = relationship("Funcion")

    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=True)
    servicio = relationship("Servicio", back_populates="evaluaciones")
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=True)
    factura = relationship("Factura")
