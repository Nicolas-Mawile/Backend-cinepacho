"""Seed de funciones."""

from datetime import datetime
from datetime import timedelta

from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.funcion import (
    Funcion
)

from app.infrastructure.models.pelicula import (
    Pelicula
)

from app.infrastructure.models.sala import (
    Sala
)


def run():

    db = SessionLocal()

    try:

        existing = (
            db.execute(
                select(Funcion)
            )
            .scalar_one_or_none()
        )

        if existing:

            print(
                "✓ Funciones ya existen."
            )

            return

        peliculas = (
            db.execute(
                select(Pelicula)
            )
            .scalars()
            .all()
        )

        salas = (
            db.execute(
                select(Sala)
            )
            .scalars()
            .all()
        )

        if not peliculas:

            print(
                "✗ Debe ejecutar "
                "pelicula_seed primero"
            )

            return

        if not salas:

            print(
                "✗ Debe ejecutar "
                "multiplex_seed primero"
            )

            return

        horas = [
            2,
            5,
            8,
            11,
            14
        ]

        index_pelicula = 0

        for sala in salas:

            for hora in horas:

                pelicula = peliculas[
                    index_pelicula
                    % len(peliculas)
                ]

                funcion = Funcion(
                    peliculaId=pelicula.id,
                    salaId=sala.id,
                    fechaHora=(
                        datetime.utcnow()
                        + timedelta(hours=hora)
                    )
                )

                db.add(funcion)

                print(
                    f"✓ Función creada | "
                    f"{pelicula.titulo} | "
                    f"Sala {sala.numero}"
                )

                index_pelicula += 1

        db.commit()

        print(
            "✓ Seed funciones completado."
        )

    except Exception as e:

        db.rollback()

        print(
            f"✗ Error seed funciones: {e}"
        )

        raise

    finally:

        db.close()


if __name__ == "__main__":

    run()