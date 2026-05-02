from sqlalchemy import Column, Float, Integer, String

from app.infrastructure.models.base import Base

class TipoSilla(Base):
    __tablename__ = "tipoSilla"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False, unique=True)
    precio = Column(Float, nullable=False)