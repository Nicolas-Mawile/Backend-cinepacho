from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base

class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    precio = Column(Integer)

    evaluaciones = relationship("Evaluacion", back_populates="servicio")