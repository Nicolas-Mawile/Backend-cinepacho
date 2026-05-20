"""Servicio de películas."""

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.infrastructure.models.pelicula import (
    Pelicula
)

from app.infrastructure.repositories.pelicula_repository import (
    PeliculaRepository
)


class PeliculaService:

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = (
            PeliculaRepository(db)
        )

    # =====================================================
    # LISTAR
    # =====================================================

    def listar_peliculas(self):

        return (
            self.repository.get_all()
        )

    # =====================================================
    # OBTENER
    # =====================================================

    def obtener_pelicula(
        self,
        pelicula_id: int
    ):

        pelicula = (
            self.repository.get_by_id(
                pelicula_id
            )
        )

        if not pelicula:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Película no encontrada"
                )
            )

        return pelicula

    # =====================================================
    # CREAR
    # =====================================================

    def crear_pelicula(
        self,
        data
    ):

        existe = (
            self.repository
            .exists_by_titulo(
                data.titulo
            )
        )

        if existe:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Ya existe una "
                    "película con ese título"
                )
            )

        pelicula = Pelicula(

            titulo=data.titulo,

            duracionMinutos=(
                data.duracionMinutos
            ),

            linkTrailer=data.linkTrailer,

            linkPoster=data.linkPoster,

            sinopsis=data.sinopsis,

            estaActiva=True
        )

        return (
            self.repository.create(
                pelicula
            )
        )

    # =====================================================
    # ACTUALIZAR
    # =====================================================

    def actualizar_pelicula(
        self,
        pelicula_id: int,
        data
    ):

        pelicula = (
            self.obtener_pelicula(
                pelicula_id
            )
        )

        for key, value in (
            data.model_dump(
                exclude_none=True
            )
            .items()
        ):

            setattr(
                pelicula,
                key,
                value
            )

        return (
            self.repository.update(
                pelicula
            )
        )

    # =====================================================
    # DESACTIVAR
    # =====================================================

    # =====================================================
    # CAMBIAR ESTADO
    # =====================================================

    def cambiar_estado_pelicula(
        self,
        pelicula_id: int,
        esta_activa: bool
    ):

        pelicula = (
            self.obtener_pelicula(
                pelicula_id
            )
        )

        pelicula.estaActiva = (
            esta_activa
        )

        self.repository.update(
            pelicula
        )

        estado = (
            "activada"
            if esta_activa
            else "desactivada"
        )

        return {
            "mensaje": (
                f"Película {estado} "
                f"correctamente"
            ), 
            "pelicula": pelicula
        }