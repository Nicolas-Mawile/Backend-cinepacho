"""Entidad Usuario para autenticación y autorización."""
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint

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

    rolId = Column(Integer, ForeignKey("rol.id"))
    clienteId = Column(Integer, ForeignKey("clientes.id"), nullable=True, unique=True)
    empleadoId = Column(Integer, ForeignKey("empleados.id"), nullable=True, unique=True)

    rol = relationship("Rol", back_populates="usuarios")
    cliente = relationship("Cliente", back_populates="usuario")
    empleado = relationship("Empleado", back_populates="usuario")

    @property
    def nombres(self):

        if self.cliente:
            return self.cliente.nombres

        if self.empleado:
            return self.empleado.nombres

        return None

    @property
    def apellidos(self):

        if self.cliente:
            return self.cliente.apellidos

        if self.empleado:
            return self.empleado.apellidos

        return None

    @property
    def correo(self):

        if self.cliente:
            return self.cliente.correo

        if self.empleado:
            return self.empleado.correoLaboral

        return None