"""Seed data for tipoSilla."""

from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.tipoSilla import TipoSilla


TIPOS_SILLA = [
    {"nombre": "ESTANDAR", "precio": 14000.0},
    {"nombre": "PREFERENCIAL", "precio": 20000.0},
]


def run():
    """
    Inserta tipos de silla.
    Idempotente: no duplica registros.
    """
    with SessionLocal() as db:
        try:
            existing = db.execute(select(TipoSilla).limit(1)).scalar_one_or_none()
            if existing:
                print("✔ Seed tipoSilla: ya existen registros, omitiendo.")
                return

            for data in TIPOS_SILLA:
                db.add(TipoSilla(**data))

            db.commit()
            print(f"✔ Seed tipoSilla: {len(TIPOS_SILLA)} tipos insertados.")

        except Exception as e:
            db.rollback()
            print(f"✗ Error en seed tipoSilla: {e}")
            raise


if __name__ == "__main__":
    run()