from sqlalchemy import Column, Boolean, Integer, String

from .base import Base

class Persona(Base):
    """
    Entidad base que representa información humana
    compartida entre clientes y empleados.
    """
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    correo = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    tipo = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'persona',
        'polymorphic_on': tipo
    }