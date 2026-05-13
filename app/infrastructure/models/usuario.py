"""Entidad Usuario para autenticación y autorización."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.models.base import Base, TimestampMixin
from sqlalchemy.orm import relationship

class Usuario(Base, TimestampMixin):
    """
    Entidad encargada de autenticación
    y autorización del sistema.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    passwordHash = Column(String, nullable=False)
    intentosFallidos = Column(Integer, default=0)
    bloqueadoHasta =  Column(DateTime, nullable=True)
    estaActivo = Column(Boolean, nullable=False, default=True)

    personaId = Column(Integer, ForeignKey("personas.id"), unique=True)
    rolId = Column(Integer, ForeignKey("rol.id"))
    rol = relationship("Rol", back_populates="usuarios")
    persona = relationship("Persona")
    cliente = relationship(
        "Cliente",
        back_populates="usuario",
        uselist=False,
        foreign_keys="Cliente.usuarioId"
    )

    empleado = relationship(
        "Empleado",
        back_populates="usuario",
        uselist=False,
        foreign_keys="Empleado.usuarioId"
    )
