"""Modelo ORM para la entidad Cliente."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from .persona import Persona


class Cliente(Persona):
    """
    Entidad que representa clientes del sistema.

    Un cliente puede:
    - Tener usuario (registrado)
    - No tener usuario (invitado)
    """
    __tablename__ = "clientes"

    id = Column(Integer, ForeignKey("personas.id"), primary_key=True)
    usuarioId = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario = relationship("Usuario", back_populates="cliente", foreign_keys=[usuarioId])
    puntosAcumulados = Column(Integer, default=0)
    fechaRegistro = Column(DateTime, server_default=func.now())
    estaActivo = Column(Boolean, default=True)
    
    evaluaciones = relationship("Evaluacion", back_populates="cliente")
    facturas = relationship("Factura", back_populates="cliente")

    __mapper_args__ = {
        "polymorphic_identity": "cliente"
    }
