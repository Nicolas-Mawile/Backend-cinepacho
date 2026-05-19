"""Funcion repository."""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.infrastructure.base_repository import AbstractRepository
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera


class FuncionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        funcion_id: int
    ):

        return (
            self.db.query(Funcion)
            .filter(Funcion.id == funcion_id)
            .first()
        )

    def add(self, entity: Funcion) -> Funcion:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, entity_id: int) -> Funcion | None:
        return self.db.get(Funcion, entity_id)

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Funcion]:
        result = self.db.execute(select(Funcion).offset(skip).limit(limit))
        return list(result.scalars().all())

    def update(self, entity_id: int, data: dict) -> Funcion | None:
        f = self.get(entity_id)
        if not f:
            return None
        for k, v in data.items():
            setattr(f, k, v)
        self.db.commit()
        self.db.refresh(f)
        return f

    def delete(self, entity_id: int) -> bool:
        f = self.get(entity_id)
        if not f:
            return False
        self.db.delete(f)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        return self.get(entity_id) is not None

    def hay_solapamiento(self, sala_id: int, inicio: datetime, fin: datetime, excluir_id: int = None) -> bool:
        stmt = select(Funcion).where(
            and_(
                Funcion.salaId == sala_id,
                Funcion.estaActiva == True,
                Funcion.fechaHora < fin,
                Funcion.fechaHoraFin > inicio,
            )
        )
        if excluir_id:
            stmt = stmt.where(Funcion.id != excluir_id)
        result = self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none() is not None

    def listar_por_multiplex(self, multiplex_id: int) -> list[Funcion]:
        from app.infrastructure.models.sala import Sala
        result = self.db.execute(
            select(Funcion).join(Sala).where(Sala.multiplexId == multiplex_id)
        )
        return list(result.scalars().all())

    def listar_por_sala(self, sala_id: int) -> list[Funcion]:
        result = self.db.execute(
            select(Funcion).where(Funcion.salaId == sala_id)
        )
        return list(result.scalars().all())

    def tiene_boletas(self, funcion_id: int) -> bool:
        from app.infrastructure.models.boleta import Boleta
        result = self.db.execute(
            select(Boleta).where(Boleta.funcionId == funcion_id).limit(1)
        )
        return result.scalar_one_or_none() is not None

    def pelicula_en_cartelera(self, pelicula_id: int, multiplex_id: int) -> bool:
        result = self.db.execute(
            select(MultiplexCartelera).where(
                and_(
                    MultiplexCartelera.peliculaId == pelicula_id,
                    MultiplexCartelera.multiplexId == multiplex_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None