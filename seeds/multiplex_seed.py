"""Seed de multiplexes."""

from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.multiplex import (
    Multiplex
)


MULTIPLEX_DATA = [
    {
        "nombre": "Titán Plaza",
        "codigo": "TIT",
        "ciudad": "Bogotá",
        "direccion": "Calle 129B #71B-40",
        "latitud": Decimal("4.663100"),
        "longitud": Decimal("-74.150300"),
    },
    {
        "nombre": "Unicentro",
        "codigo": "UNI",
        "ciudad": "Bogotá",
        "direccion": "Av. 15 #124-30",
        "latitud": Decimal("4.697100"),
        "longitud": Decimal("-74.048100"),
    },
    {
        "nombre": "Plaza Central",
        "codigo": "PLC",
        "ciudad": "Bogotá",
        "direccion": "Calle 30 Sur #43C-80",
        "latitud": Decimal("4.628500"),
        "longitud": Decimal("-74.127200"),
    },
    {
        "nombre": "Gran Estación",
        "codigo": "GRE",
        "ciudad": "Bogotá",
        "direccion": "Av. El Dorado #65B-50",
        "latitud": Decimal("4.650300"),
        "longitud": Decimal("-74.092000"),
    },
    {
        "nombre": "Embajador Centro",
        "codigo": "EMB",
        "ciudad": "Bogotá",
        "direccion": "Cra. 13 #15-50",
        "latitud": Decimal("4.609900"),
        "longitud": Decimal("-74.083300"),
    },
    {
        "nombre": "Las Américas",
        "codigo": "AME",
        "ciudad": "Bogotá",
        "direccion": "Cra. 86 #30A-30",
        "latitud": Decimal("4.641300"),
        "longitud": Decimal("-74.088400"),
    },
]


def run():
    """
    Inserta multiplexes iniciales.

    El seed es idempotente:
    no duplica registros.
    """

    db = SessionLocal()

    try:

        existing = db.execute(
            select(Multiplex)
        ).scalar_one_or_none()

        if existing:

            print(
                "✓ Multiplex ya existentes."
            )

            return

        for data in MULTIPLEX_DATA:

            multiplex = Multiplex(**data)

            db.add(multiplex)

        db.commit()

        print(
            f"✓ {len(MULTIPLEX_DATA)} "
            f"multiplex creados."
        )

    except Exception as e:

        db.rollback()

        print(
            f"✗ Error seed multiplex: {e}"
        )

        raise

    finally:

        db.close()


if __name__ == "__main__":

    run()