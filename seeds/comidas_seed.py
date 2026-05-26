"""Seed data for comidas."""

from sqlalchemy import select

from app.database import SessionLocal
from app.infrastructure.models.comida import Comida


_IMG_POPCORN      = "https://yarbixjgzlbgnlpegxvp.supabase.co/storage/v1/object/public/images-cinepacho/comidas/1779706732373-mathrppn3e.png"
_IMG_NACHOS       = "https://yarbixjgzlbgnlpegxvp.supabase.co/storage/v1/object/public/images-cinepacho/comidas/Nachos.png"
_IMG_HOTDOG       = "https://yarbixjgzlbgnlpegxvp.supabase.co/storage/v1/object/public/images-cinepacho/comidas/Hot_dog.png"
_IMG_GASEOSA      = "https://yarbixjgzlbgnlpegxvp.supabase.co/storage/v1/object/public/images-cinepacho/comidas/Bebida.png"
_IMG_CHOCOLATINA  = "https://yarbixjgzlbgnlpegxvp.supabase.co/storage/v1/object/public/images-cinepacho/comidas/Chocolatina.png"
_IMG_AGUA         = "https://yarbixjgzlbgnlpegxvp.supabase.co/storage/v1/object/public/images-cinepacho/comidas/Agua.jpg"
_IMG_MYM          = "https://yarbixjgzlbgnlpegxvp.supabase.co/storage/v1/object/public/images-cinepacho/comidas/MyM.jpg"


COMIDAS_DATA = [

    # POPCORN

    {
        "nombre": "Pop Corn Sal Pequeño",
        "descripcion": "Crispetas saladas tamaño pequeño.",
        "precio": 12000,
        "imagenUrl": _IMG_POPCORN,
    },
    {
        "nombre": "Pop Corn Sal Mediano",
        "descripcion": "Crispetas saladas tamaño mediano.",
        "precio": 16000,
        "imagenUrl": _IMG_POPCORN,
    },
    {
        "nombre": "Pop Corn Sal Grande",
        "descripcion": "Crispetas saladas tamaño grande.",
        "precio": 22000,
        "imagenUrl": _IMG_POPCORN,
    },
    {
        "nombre": "Pop Corn Dulce Pequeño",
        "descripcion": "Crispetas dulces tamaño pequeño.",
        "precio": 13000,
        "imagenUrl": _IMG_POPCORN,
    },
    {
        "nombre": "Pop Corn Mixto Grande",
        "descripcion": "Crispetas mitad sal mitad dulce tamaño grande.",
        "precio": 24000,
        "imagenUrl": _IMG_POPCORN,
    },

    # GASEOSAS

    {
        "nombre": "Gaseosa Pequeña",
        "descripcion": "Gaseosa en vaso pequeño con hielo.",
        "precio": 8000,
        "imagenUrl": _IMG_GASEOSA,
    },
    {
        "nombre": "Gaseosa Mediana",
        "descripcion": "Gaseosa en vaso mediano con hielo.",
        "precio": 10000,
        "imagenUrl": _IMG_GASEOSA,
    },
    {
        "nombre": "Gaseosa Grande",
        "descripcion": "Gaseosa en vaso grande con hielo.",
        "precio": 12000,
        "imagenUrl": _IMG_GASEOSA,
    },

    # PERROS

    {
        "nombre": "Hot Dog Tradicional",
        "descripcion": "Perro caliente con salsa de tomate y mostaza.",
        "precio": 15000,
        "imagenUrl": _IMG_HOTDOG,
    },
    {
        "nombre": "Hot Dog Especial",
        "descripcion": "Perro caliente con papas, queso y salsas especiales.",
        "precio": 19000,
        "imagenUrl": _IMG_HOTDOG,
    },

    # NACHOS

    {
        "nombre": "Nachos con Queso",
        "descripcion": "Nachos crujientes bañados en salsa de queso caliente.",
        "precio": 18000,
        "imagenUrl": _IMG_NACHOS,
    },

    # DULCERÍA

    {
        "nombre": "M&M's",
        "descripcion": "Chocolates de colores M&M's tamaño individual.",
        "precio": 9000,
        "imagenUrl": _IMG_MYM,
    },
    {
        "nombre": "Chocolatina",
        "descripcion": "Chocolatina tamaño normal.",
        "precio": 7000,
        "imagenUrl": _IMG_CHOCOLATINA,
    },

    # AGUA

    {
        "nombre": "Agua Botella",
        "descripcion": "Agua mineral en botella 500ml.",
        "precio": 6000,
        "imagenUrl": _IMG_AGUA,
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
        comida.descripcion = data.get("descripcion")
        comida.imagenUrl = data.get("imagenUrl")

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