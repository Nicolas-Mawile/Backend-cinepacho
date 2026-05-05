"""Seed data for multiplexes - Datos iniciales de cines."""

from decimal import Decimal
from sqlalchemy import select

from app.infrastructure.models.multiplex import Multiplex
from app.database import SessionLocal


MULTIPLEX_DATA = [
    {
        "nombre": "Titán Plaza",
        "codigo": "TIT",
        "ciudad": "Bogotá",
        "direccion": "Calle 129B #71B-40, Bogotá",
        "latitud": Decimal("4.663100"),
        "longitud": Decimal("-74.150300"),
    },
    {
        "nombre": "Unicentro",
        "codigo": "UNI",
        "ciudad": "Bogotá",
        "direccion": "Av. 15 #124-30, Bogotá",
        "latitud": Decimal("4.697100"),
        "longitud": Decimal("-74.048100"),
    },
    {
        "nombre": "Plaza Central",
        "codigo": "PLC",
        "ciudad": "Bogotá",
        "direccion": "Calle 30 Sur #43C-80, Bogotá",
        "latitud": Decimal("4.628500"),
        "longitud": Decimal("-74.127200"),
    },
    {
        "nombre": "Gran Estación",
        "codigo": "GRE",
        "ciudad": "Bogotá",
        "direccion": "Av. El Dorado #65B-50, Bogotá",
        "latitud": Decimal("4.650300"),
        "longitud": Decimal("-74.092000"),
    },
    {
        "nombre": "Embajador (Centro)",
        "codigo": "EMB",
        "ciudad": "Bogotá",
        "direccion": "Cra. 13 #15-50, Bogotá",
        "latitud": Decimal("4.609900"),
        "longitud": Decimal("-74.083300"),
    },
    {
        "nombre": "Las Américas",
        "codigo": "AME",
        "ciudad": "Bogotá",
        "direccion": "Cra. 86 #30A-30, Bogotá",
        "latitud": Decimal("4.641300"),
        "longitud": Decimal("-74.088400"),
    },
]


def run():
    """
    Carga datos iniciales de multiplexes.
    Idempotente: no inserta si ya existen registros.
    """
    with SessionLocal() as db:
        try:
            # Verificar si ya existen registros
            stmt = select(Multiplex).limit(1)
            result = db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                print("✓ Seed multiplex: ya existen registros, omitiendo.")
                return
            
            # Insertar nuevos datos
            for data in MULTIPLEX_DATA:
                multiplex = Multiplex(**data)
                db.add(multiplex)
            
            db.commit()
            print(f"✓ Seed multiplex: {len(MULTIPLEX_DATA)} multiplexes insertados correctamente.")
            
        except Exception as e:
            db.rollback()
            print(f"✗ Error en seed multiplex: {str(e)}")
            raise


if __name__ == "__main__":
    """Permite ejecutar este seed directamente: python seeds/multiplex.py"""
    run()