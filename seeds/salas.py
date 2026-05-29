"""Seed data for salas y sillas."""

from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.tipoSilla import TipoSilla


# Cada multiplex tendrá estas salas
# (numero, capacidadTotal, capacidadPreferencial)
SALAS_POR_MULTIPLEX = [
    {"numero": 1, "capacidadTotal": 80, "capacidadPreferencial": 10},
    {"numero": 2, "capacidadTotal": 80, "capacidadPreferencial": 10},
    {"numero": 3, "capacidadTotal": 60, "capacidadPreferencial": 8},
]


def crear_sillas(db, sala: Sala, tipo_estandar: TipoSilla, tipo_preferencial: TipoSilla):
    """
    Crea las sillas de una sala.
    Las últimas filas son preferenciales según capacidadPreferencial.
    Layout: filas × 10 columnas aproximadamente.
    """
    total = sala.capacidadTotal
    preferenciales = sala.capacidadPreferencial
    estandar = total - preferenciales

    columnas = 10
    filas_estandar = estandar // columnas
    filas_preferencial = preferenciales // columnas

    # Filas estándar
    for fila in range(1, filas_estandar + 1):
        for col in range(1, columnas + 1):
            db.add(Silla(
                fila=fila,
                columna=col,
                estaActiva=True,
                salaId=sala.id,
                tipoSillaId=tipo_estandar.id,
            ))

    # Filas preferenciales (al final)
    for fila in range(filas_estandar + 1, filas_estandar + filas_preferencial + 1):
        for col in range(1, columnas + 1):
            db.add(Silla(
                fila=fila,
                columna=col,
                estaActiva=True,
                salaId=sala.id,
                tipoSillaId=tipo_preferencial.id,
            ))


def run():
    """
    Crea salas y sillas para todos los multiplexes.
    Idempotente: no duplica registros.
    """
    with SessionLocal() as db:
        try:
            existing = db.execute(select(Sala).limit(1)).scalar_one_or_none()
            if existing:
                return

            tipo_estandar = db.execute(
                select(TipoSilla).where(TipoSilla.nombre == "ESTANDAR")
            ).scalar_one_or_none()
            tipo_preferencial = db.execute(
                select(TipoSilla).where(TipoSilla.nombre == "PREFERENCIAL")
            ).scalar_one_or_none()

            if not tipo_estandar or not tipo_preferencial:
                return

            multiplexes = db.execute(select(Multiplex)).scalars().all()
            if not multiplexes:
                return

            total_salas = 0
            total_sillas = 0

            for multiplex in multiplexes:
                for config in SALAS_POR_MULTIPLEX:
                    sala = Sala(
                        numero=config["numero"],
                        capacidadTotal=config["capacidadTotal"],
                        capacidadPreferencial=config["capacidadPreferencial"],
                        estaActiva=True,
                        multiplexId=multiplex.id,
                    )
                    db.add(sala)
                    db.flush()  # para obtener sala.id

                    crear_sillas(db, sala, tipo_estandar, tipo_preferencial)
                    total_sillas += config["capacidadTotal"]
                    total_salas += 1

            db.commit()

        except Exception as e:
            db.rollback()
            raise


if __name__ == "__main__":
    run()