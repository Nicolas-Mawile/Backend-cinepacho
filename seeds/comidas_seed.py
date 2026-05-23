"""Seed data for comidas."""

from sqlalchemy import select

from app.database import SessionLocal
from app.infrastructure.models.comida import Comida


COMIDAS_DATA = [

    # POPCORN

    {
        "nombre": "Pop Corn Sal Pequeño",
        "precio": 12000,
    },
    {
        "nombre": "Pop Corn Sal Mediano",
        "precio": 16000,
    },
    {
        "nombre": "Pop Corn Sal Grande",
        "precio": 22000,
    },
    {
        "nombre": "Pop Corn Dulce Pequeño",
        "precio": 13000,
    },
    {
        "nombre": "Pop Corn Mixto Grande",
        "precio": 24000,
    },

    # GASEOSAS

    {
        "nombre": "Gaseosa Pequeña",
        "precio": 8000,
    },
    {
        "nombre": "Gaseosa Mediana",
        "precio": 10000,
    },
    {
        "nombre": "Gaseosa Grande",
        "precio": 12000,
    },

    # PERROS

    {
        "nombre": "Hot Dog Tradicional",
        "precio": 15000,
    },
    {
        "nombre": "Hot Dog Especial",
        "precio": 19000,
    },

    # NACHOS

    {
        "nombre": "Nachos con Queso",
        "precio": 18000,
    },

    # DULCERÍA

    {
        "nombre": "M&M's",
        "precio": 9000,
    },
    {
        "nombre": "Chocolatina Jumbo",
        "precio": 7000,
    },

    # AGUA

    {
        "nombre": "Agua Botella",
        "precio": 6000,
    },
]


def validate_comida_data(data: dict):

    if not data["nombre"].strip():

        raise ValueError(
            "Nombre de comida vacío"
        )

    if data["precio"] <= 0:

        raise ValueError(
            f"Precio inválido para "
            f"{data['nombre']}"
        )


def create_or_update_comida(
    db,
    data: dict
):

    comida = db.execute(
        select(Comida).where(
            Comida.nombre == data["nombre"]
        )
    ).scalar_one_or_none()

    if comida:

        comida.precio = data["precio"]

        print(
            f"🔄 Comida actualizada: "
            f"{comida.nombre}"
        )

        return

    comida = Comida(**data)

    db.add(comida)

    print(
        f"✅ Comida creada: "
        f"{comida.nombre}"
    )


def validate_integrity(db):

    comidas = db.execute(
        select(Comida)
    ).scalars().all()

    nombres = set()

    for comida in comidas:

        if comida.nombre in nombres:

            raise Exception(
                f"Comida duplicada: "
                f"{comida.nombre}"
            )

        nombres.add(comida.nombre)

        if comida.precio <= 0:

            raise Exception(
                f"Precio inválido: "
                f"{comida.nombre}"
            )

    print("✅ Validación comidas completada")


def run():

    with SessionLocal() as db:

        try:

            print(
                "\n🍿 Iniciando seed comidas...\n"
            )

            for data in COMIDAS_DATA:

                validate_comida_data(data)

                create_or_update_comida(
                    db,
                    data
                )

            db.commit()

            validate_integrity(db)

            print(
                f"\n✅ Seed comidas completado "
                f"({len(COMIDAS_DATA)} comidas)\n"
            )

        except Exception as e:

            db.rollback()

            print(
                f"\n❌ Error seed comidas:\n{e}"
            )

            raise e


if __name__ == "__main__":

    run()