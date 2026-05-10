"""Empleado model."""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Empleado(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_empleado = Column(String, nullable=False, unique=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # EMPLEADO-CAJERO, EMPLEADO-OTRO, ADMIN-MULTIPLEX, ADMIN-GENERAL
    multiplex_id = Column(Integer, ForeignKey("multiplex.id"), nullable=True)
    activo = Column(Boolean, default=True)

    multiplex = relationship("Multiplex", backref="empleados")