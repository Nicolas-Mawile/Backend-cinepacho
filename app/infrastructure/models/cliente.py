"""Modelo ORM para la entidad Cliente."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from .persona import Persona
from .base import Base

class Cliente(Base, Persona):
    """
    Entidad que representa clientes del sistema.

    Un cliente puede:
    - Tener usuario (registrado)
    - No tener usuario (invitado)
    """
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    puntosAcumulados = Column(Integer, default=0)
    fechaRegistro = Column(DateTime, server_default=func.now())
    estaActivo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="cliente", uselist=False)   
    empleado = relationship("Empleado", back_populates="cliente", uselist=False) 
    evaluaciones = relationship("Evaluacion", back_populates="cliente")
    facturas = relationship("Factura", back_populates="cliente", cascade="all")
    recompensas = relationship("RecompensaBoleta", back_populates="cliente",cascade="all, delete-orphan")