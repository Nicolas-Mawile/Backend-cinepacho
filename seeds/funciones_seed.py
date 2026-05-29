"""Seed data for funciones."""

from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.multiplex_cartelera import (
    MultiplexCartelera
)


HORARIOS_BASE = [
    (11, 0),
    (14, 0),
    (17, 0),
    (20, 0),
]

DIAS_GENERAR = 3

MINUTOS_LIMPIEZA = 20


def function_exists(
    db,
    sala_id,
    fecha_inicio
):

    existing = db.execute(
        select(Funcion).where(
            Funcion.salaId == sala_id,
            Funcion.fechaHora == fecha_inicio
        )
    ).scalar_one_or_none()

    return existing is not None


def has_overlap(
    db,
    sala_id,
    fecha_inicio,
    fecha_fin
):

    funciones = db.execute(
        select(Funcion).where(
            Funcion.salaId == sala_id
        )
    ).scalars().all()

    for funcion in funciones:

        overlap = (
            fecha_inicio < funcion.fechaHoraFin
            and
            fecha_fin > funcion.fechaHora
        )

        if overlap:
            return True

    return False


def create_funcion_if_valid(
    db,
    pelicula,
    sala,
    fecha_inicio
):

    fecha_fin = (
        fecha_inicio
        + timedelta(
            minutes=(
                pelicula.duracionMinutos
                + MINUTOS_LIMPIEZA
            )
        )
    )

    # Evitar traslapes

    if has_overlap(
        db,
        sala.id,
        fecha_inicio,
        fecha_fin
    ):
        return False

    # Evitar duplicados exactos

    if function_exists(
        db,
        sala.id,
        fecha_inicio
    ):
        return False

    # Evitar funciones muy tarde

    if fecha_fin.hour >= 23:
        return False

    funcion = Funcion(
        peliculaId=pelicula.id,
        salaId=sala.id,
        fechaHora=fecha_inicio,
        fechaHoraFin=fecha_fin,
        estaActiva=True
    )

    db.add(funcion)

    return True


def validate_integrity(db):

    funciones = db.execute(
        select(Funcion)
    ).scalars().all()

    for funcion in funciones:

        if funcion.fechaHoraFin <= funcion.fechaHora:

            raise Exception(
                f"Función inválida ID "
                f"{funcion.id}"
            )


def run():

    with SessionLocal() as db:

        try:

            salas = db.execute(
                select(Sala).where(
                    Sala.estaActiva == True
                )
            ).scalars().all()

            if not salas:

                raise Exception(
                    "No existen salas activas"
                )

            hoy = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            count = 0

            for sala in salas:

                cartelera = db.execute(
                    select(MultiplexCartelera).where(
                        MultiplexCartelera.multiplexId
                        == sala.multiplexId
                    )
                ).scalars().all()

                if not cartelera:
                    continue

                peliculas_ids = [
                    c.peliculaId
                    for c in cartelera
                ]

                peliculas = db.execute(
                    select(Pelicula).where(
                        Pelicula.id.in_(peliculas_ids),
                        Pelicula.estaActiva == True
                    )
                ).scalars().all()

                if not peliculas:
                    continue

                pelicula_index = 0

                for dia in range(DIAS_GENERAR):

                    fecha_base = hoy + timedelta(days=dia)

                    for hora, minuto in HORARIOS_BASE:

                        pelicula = peliculas[
                            pelicula_index % len(peliculas)
                        ]

                        pelicula_index += 1

                        fecha_inicio = fecha_base.replace(
                            hour=hora,
                            minute=minuto
                        )

                        creada = create_funcion_if_valid(
                            db,
                            pelicula,
                            sala,
                            fecha_inicio
                        )

                        if creada:
                            count += 1


            db.commit()
            validate_integrity(db)

        except Exception as e:
            db.rollback()
            raise e

if __name__ == "__main__":
    run()