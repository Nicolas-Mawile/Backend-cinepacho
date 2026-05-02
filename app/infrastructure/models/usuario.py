from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from cinepachobackend.app.infrastructure.models.base import Base, TimestampMixin
from sqlalchemy.orm import relationship

class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(String, nullable=False)
    estaActivo = Column(Boolean, nullable=False, default=True)

    persona_id = Column(Integer, ForeignKey("persona.id"), unique=True)
    persona = relationship("Persona")

    rol_id = Column(Integer, ForeignKey("rol.id"))
    rol = relationship("Rol", back_populates="usuarios")