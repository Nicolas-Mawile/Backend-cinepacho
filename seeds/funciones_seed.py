"""Seed data for funciones."""

from datetime import datetime, timedelta
from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera


def run():
    """
    Crea funciones para los próximos 3 días.
    Cada sala del multiplex tendrá funciones rotando entre las películas de su cartelera.
    Idempotente: no duplica registros.
    """
    with SessionLocal() as db:
        try:
            existing = db.execute(select(Funcion).limit(1)).scalar_one_or_none()
            if existing:
                print("✔ Seed funciones: ya existen registros, omitiendo.")
                return

            salas = db.execute(select(Sala).where(Sala.estaActiva == True)).scalars().all()
            if not salas:
                print("✗ Seed funciones: no hay salas activas.")
                return

            # Horarios base para cada día (hora de inicio)
            HORARIOS = ["11:00", "13:30", "16:00", "18:30", "21:00"]

            hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            count = 0

            for sala in salas:
                # Obtener películas en cartelera de este multiplex
                cartelera = db.execute(
                    select(MultiplexCartelera).where(
                        MultiplexCartelera.multiplexId == sala.multiplexId
                    )
                ).scalars().all()

                if not cartelera:
                    continue

                peliculas_ids = [c.peliculaId for c in cartelera]
                peliculas = db.execute(
                    select(Pelicula).where(Pelicula.id.in_(peliculas_ids))
                ).scalars().all()

                if not peliculas:
                    continue

                for dia in range(3):  # Hoy, mañana, pasado
                    fecha_base = hoy + timedelta(days=dia)

                    for i, horario_str in enumerate(HORARIOS):
                        hora, minuto = map(int, horario_str.split(":"))
                        pelicula = peliculas[i % len(peliculas)]

                        fecha_inicio = fecha_base.replace(hour=hora, minute=minuto)
                        fecha_fin = fecha_inicio + timedelta(minutes=pelicula.duracionMinutos)

                        funcion = Funcion(
                            peliculaId=pelicula.id,
                            salaId=sala.id,
                            fechaHora=fecha_inicio,
                            fechaHoraFin=fecha_fin,
                            estaActiva=True,
                        )
                        db.add(funcion)
                        count += 1

            db.commit()
            print(f"✔ Seed funciones: {count} funciones creadas.")

        except Exception as e:
            db.rollback()
            print(f"✗ Error en seed funciones: {e}")
            raise


if __name__ == "__main__":
    run()