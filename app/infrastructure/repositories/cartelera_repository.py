"""Repositorio de cartelera."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.models.pelicula import Pelicula


class CarteleraRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_multiplex(self, multiplex_id: int) -> Multiplex | None:
        return self.db.get(Multiplex, multiplex_id)

    def get_pelicula(self, pelicula_id: int) -> Pelicula | None:
        return self.db.get(Pelicula, pelicula_id)

    def listar_general(self) -> list[Pelicula]:
        stmt = (
            select(Pelicula)
            .join(MultiplexCartelera, MultiplexCartelera.peliculaId == Pelicula.id)
            .distinct()
            .order_by(Pelicula.titulo)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def listar_por_multiplex(self, multiplex_id: int) -> list[MultiplexCartelera]:
        stmt = (
            select(MultiplexCartelera)
            .options(
                selectinload(MultiplexCartelera.multiplex),
                selectinload(MultiplexCartelera.pelicula),
            )
            .where(MultiplexCartelera.multiplexId == multiplex_id)
            .order_by(MultiplexCartelera.id)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def obtener_entrada(self, multiplex_id: int, pelicula_id: int) -> MultiplexCartelera | None:
        stmt = (
            select(MultiplexCartelera)
            .options(
                selectinload(MultiplexCartelera.multiplex),
                selectinload(MultiplexCartelera.pelicula),
            )
            .where(
                MultiplexCartelera.multiplexId == multiplex_id,
                MultiplexCartelera.peliculaId == pelicula_id,
            )
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def existe_entrada(self, multiplex_id: int, pelicula_id: int) -> bool:
        stmt = select(MultiplexCartelera.id).where(
            MultiplexCartelera.multiplexId == multiplex_id,
            MultiplexCartelera.peliculaId == pelicula_id,
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    def agregar(self, multiplex_id: int, pelicula_id: int) -> MultiplexCartelera:
        entrada = MultiplexCartelera(multiplexId=multiplex_id, peliculaId=pelicula_id)
        self.db.add(entrada)
        self.db.commit()
        self.db.refresh(entrada)
        return entrada

    def agregar_varios(self, entradas: list[MultiplexCartelera]) -> list[MultiplexCartelera]:
        if not entradas:
            return []

        self.db.add_all(entradas)
        self.db.commit()
        for entrada in entradas:
            self.db.refresh(entrada)
        return entradas

    def eliminar_entrada(self, multiplex_id: int, pelicula_id: int) -> bool:
        entrada = self.db.execute(
            select(MultiplexCartelera).where(
                MultiplexCartelera.multiplexId == multiplex_id,
                MultiplexCartelera.peliculaId == pelicula_id,
            )
        ).scalar_one_or_none()

        if not entrada:
            return False

        self.db.delete(entrada)
        self.db.commit()
        return True

    def listar_multiplex_activos_ids(self) -> list[int]:
        stmt = select(Multiplex.id).where(Multiplex.estaActivo.is_(True))
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def listar_entradas_por_pelicula(self, pelicula_id: int) -> list[MultiplexCartelera]:
        stmt = (
            select(MultiplexCartelera)
            .options(
                selectinload(MultiplexCartelera.multiplex),
                selectinload(MultiplexCartelera.pelicula),
            )
            .where(MultiplexCartelera.peliculaId == pelicula_id)
            .order_by(MultiplexCartelera.multiplexId)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def eliminar_por_pelicula(self, pelicula_id: int) -> int:
        entradas = self.db.execute(
            select(MultiplexCartelera).where(MultiplexCartelera.peliculaId == pelicula_id)
        ).scalars().all()

        for entrada in entradas:
            self.db.delete(entrada)

        if entradas:
            self.db.commit()

        return len(entradas)