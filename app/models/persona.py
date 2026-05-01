from sqlalchemy import Column, Date, Integer, String

from .base import Base, TimestampMixin

class Persona(Base, TimestampMixin):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)

    tipo = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'persona',
        'polymorphic_on': tipo
    }