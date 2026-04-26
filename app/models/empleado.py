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
    cargo = Column(String, nullable=False)  # cajero, admin_multiplex, admin_general
    multiplex_id = Column(Integer, ForeignKey("multiplex.id"), nullable=True)  # nullable para admin_general
    activo = Column(Boolean, default=True)

    multiplex = relationship("Multiplex", backref="empleados")