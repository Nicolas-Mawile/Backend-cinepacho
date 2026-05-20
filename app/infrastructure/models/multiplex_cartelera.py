"""MultiplexCartelera model - tabla intermedia."""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.models.base import Base

class MultiplexCartelera(Base):
    __tablename__ = "multiplex_cartelera"

    id = Column(Integer, primary_key=True, autoincrement=True)
    multiplexId = Column(Integer, ForeignKey("multiplex.id"), nullable=False)
    peliculaId = Column(Integer, ForeignKey("peliculas.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("multiplexId", "peliculaId", name="uq_multiplex_pelicula"),
    )