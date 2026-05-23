"""Seed data for cartelera por multiplex."""

from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.multiplex_cartelera import (
    MultiplexCartelera
)


def create_cartelera_if_not_exists(
    db,
    multiplex_id: int,
    pelicula_id: int
):

    existing = db.execute(
        select(MultiplexCartelera).where(
            MultiplexCartelera.multiplexId == multiplex_id,
            MultiplexCartelera.peliculaId == pelicula_id
        )
    ).scalar_one_or_none()

    if existing:
        return False

    entrada = MultiplexCartelera(
        multiplexId=multiplex_id,
        peliculaId=pelicula_id
    )

    db.add(entrada)

    return True


def remove_inactive_movies_from_cartelera(db):

    relaciones = db.execute(
        select(MultiplexCartelera)
    ).scalars().all()

    eliminadas = 0

    for relacion in relaciones:

        pelicula = db.execute(
            select(Pelicula).where(
                Pelicula.id == relacion.peliculaId
            )
        ).scalar_one_or_none()

        if not pelicula:

            db.delete(relacion)
            eliminadas += 1
            continue

        if not pelicula.estaActiva:

            db.delete(relacion)
            eliminadas += 1

    if eliminadas > 0:

        print(
            f"🗑️ Relaciones eliminadas "
            f"de cartelera: {eliminadas}"
        )


def validate_integrity(db):

    relaciones = db.execute(
        select(MultiplexCartelera)
    ).scalars().all()

    combinaciones = set()

    for relacion in relaciones:

        key = (
            relacion.multiplexId,
            relacion.peliculaId
        )

        if key in combinaciones:

            raise Exception(
                "Relación duplicada en cartelera"
            )

        combinaciones.add(key)

    print("✅ Validación cartelera completada")


def run():

    with SessionLocal() as db:

        try:

            print(
                "\n🎬 Iniciando seed cartelera...\n"
            )

            multiplexes = db.execute(
                select(Multiplex)
            ).scalars().all()

            peliculas_activas = db.execute(
                select(Pelicula).where(
                    Pelicula.estaActiva == True
                )
            ).scalars().all()

            if not multiplexes:

                raise Exception(
                    "No existen multiplexes"
                )

            if not peliculas_activas:

                raise Exception(
                    "No existen películas activas"
                )

            count = 0

            for multiplex in multiplexes:

                for pelicula in peliculas_activas:

                    created = create_cartelera_if_not_exists(
                        db,
                        multiplex.id,
                        pelicula.id
                    )

                    if created:

                        count += 1

                        print(
                            f"✅ {multiplex.nombre} -> "
                            f"{pelicula.titulo}"
                        )

            remove_inactive_movies_from_cartelera(db)

            db.commit()

            validate_integrity(db)

            print(
                f"\n✅ Seed cartelera completado "
                f"({count} nuevas relaciones)\n"
            )

        except Exception as e:

            db.rollback()

            print(
                f"\n❌ Error en seed cartelera:\n{e}"
            )

            raise e


if __name__ == "__main__":

    run()