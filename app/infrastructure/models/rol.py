from sqlalchemy import Column, Integer, String
from cinepachobackend.app.infrastructure.models.rol_permiso import rol_permiso
from cinepachobackend.app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

class Rol(Base):
    __tablename__ = "rol"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    permisos = relationship(
        "Permiso", 
        secondary=rol_permiso, 
        back_populates="roles")

    usuarios = relationship("Usuario", back_populates="rol")