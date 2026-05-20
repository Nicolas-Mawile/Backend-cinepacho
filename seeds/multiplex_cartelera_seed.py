"""Seed data for cartelera por multiplex."""

from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.pelicula import Pelicula


def run():
    """
    Asigna las películas activas a todos los multiplexes.
    Idempotente: no duplica registros.
    """
    with SessionLocal() as db:
        try:
            existing = db.execute(select(MultiplexCartelera).limit(1)).scalar_one_or_none()
            if existing:
                print("✔ Seed cartelera: ya existen registros, omitiendo.")
                return

            multiplexes = db.execute(select(Multiplex)).scalars().all()
            peliculas_activas = db.execute(
                select(Pelicula).where(Pelicula.estaActiva == True)
            ).scalars().all()

            if not multiplexes:
                print("✗ Seed cartelera: no hay multiplexes, ejecuta seed_multiplex primero.")
                return
            if not peliculas_activas:
                print("✗ Seed cartelera: no hay películas activas, ejecuta seed_peliculas primero.")
                return

            count = 0
            for multiplex in multiplexes:
                for pelicula in peliculas_activas:
                    entrada = MultiplexCartelera(
                        multiplexId=multiplex.id,
                        peliculaId=pelicula.id,
                    )
                    db.add(entrada)
                    count += 1

            db.commit()
            print(f"✔ Seed cartelera: {count} entradas insertadas ({len(multiplexes)} multiplexes × {len(peliculas_activas)} películas).")

        except Exception as e:
            db.rollback()
            print(f"✗ Error en seed cartelera: {e}")
            raise


if __name__ == "__main__":
    run()