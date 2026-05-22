"""Repositorio de películas."""

from sqlalchemy.orm import Session

from sqlalchemy import select

from app.infrastructure.models.pelicula import (
    Pelicula
)


class PeliculaRepository:

    def __init__(
        self,
        db: Session
    ):

        self.db = db

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        pelicula: Pelicula
    ):

        self.db.add(pelicula)

        self.db.commit()

        self.db.refresh(pelicula)

        return pelicula

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(self):

        return (
            self.db.execute(
                select(Pelicula)
            )
            .scalars()
            .all()
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        pelicula_id: int
    ):

        return (
            self.db.get(
                Pelicula,
                pelicula_id
            )
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        pelicula: Pelicula
    ):

        self.db.commit()

        self.db.refresh(pelicula)

        return pelicula

    # =====================================================
    # EXISTS BY TITULO
    # =====================================================

    def exists_by_titulo(
        self,
        titulo: str
    ):

        return (
            self.db.execute(
                select(Pelicula).where(
                    Pelicula.titulo == titulo
                )
            )
            .scalar_one_or_none()
        )