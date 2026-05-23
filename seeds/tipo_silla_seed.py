"""
Seed de tipos de silla.
"""

from app.database import SessionLocal

from app.infrastructure.models.tipoSilla import TipoSilla


TIPOS_SILLA = [
    {
        "nombre": "GENERAL",
        "precio": 11000
    },
    {
        "nombre": "PREFERENCIAL",
        "precio": 15000
    }
]


def run():

    db = SessionLocal()

    try:

        for data in TIPOS_SILLA:

            existe = (
                db.query(TipoSilla)
                .filter(
                    TipoSilla.nombre == data["nombre"]
                )
                .first()
            )

            if existe:
                continue

            tipo_silla = TipoSilla(
                nombre=data["nombre"],
                precio=data["precio"]
            )

            db.add(tipo_silla)

        db.commit()

        print(
            "✅ Seed tipos de silla ejecutado"
        )

    except Exception as e:

        db.rollback()

        print(
            f"❌ Error seed tipos silla: {e}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()