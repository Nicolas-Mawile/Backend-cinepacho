from sqlalchemy import Column, Integer, String

from cinepachobackend.app.infrastructure.models import rol_permiso
from cinepachobackend.app.infrastructure.models.base import Base
from sqlalchemy.orm import relationship

class Permiso(Base):
    __tablename__ = "permiso"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    roles = relationship(
        "Rol", 
        secondary=rol_permiso, 
        back_populates="permisos")