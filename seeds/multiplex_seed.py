"""Seed de multiplexes, salas y sillas."""

from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.multiplex import (
    Multiplex
)

from app.infrastructure.models.sala import Sala

from app.infrastructure.models.silla import Silla

from app.infrastructure.models.tipoSilla import (
    TipoSilla
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
    }
]


def crear_tipos_silla(db):

    general = (
        db.execute(
            select(TipoSilla).where(
                TipoSilla.nombre == "GENERAL"
            )
        )
        .scalar_one_or_none()
    )

    if not general:

        general = TipoSilla(
            nombre="GENERAL",
            precio=15000
        )

        db.add(general)

    preferencial = (
        db.execute(
            select(TipoSilla).where(
                TipoSilla.nombre
                == "PREFERENCIAL"
            )
        )
        .scalar_one_or_none()
    )

    if not preferencial:

        preferencial = TipoSilla(
            nombre="PREFERENCIAL",
            precio=22000
        )

        db.add(preferencial)

    db.flush()

    return general, preferencial


def crear_sillas(
    db,
    sala,
    general,
    preferencial
):

    existing = (
        db.execute(
            select(Silla).where(
                Silla.salaId == sala.id
            )
        )
        .scalar_one_or_none()
    )

    if existing:

        return

    # ==========================================
    # FILAS 1-4 = GENERAL
    # 4 x 10 = 40
    # ==========================================

    for fila in range(1, 5):

        for columna in range(1, 11):

            silla = Silla(
                fila=fila,
                columna=columna,
                salaId=sala.id,
                tipoSillaId=general.id,
                estaActiva=True
            )

            db.add(silla)

    # ==========================================
    # FILAS 5-6 = PREFERENCIAL
    # 2 x 10 = 20
    # ==========================================

    for fila in range(5, 7):

        for columna in range(1, 11):

            silla = Silla(
                fila=fila,
                columna=columna,
                salaId=sala.id,
                tipoSillaId=preferencial.id,
                estaActiva=True
            )

            db.add(silla)


def crear_salas(
    db,
    multiplex,
    general,
    preferencial
):

    existing = (
        db.execute(
            select(Sala).where(
                Sala.multiplexId
                == multiplex.id
            )
        )
        .scalar_one_or_none()
    )

    if existing:

        return

    # ==========================================
    # 5 SALAS POR MULTIPLEX
    # ==========================================

    for numero in range(1, 6):

        sala = Sala(
            numero=numero,
            multiplexId=multiplex.id,
            capacidadTotal=60,
            capacidadPreferencial=20,
            estaActiva=True
        )

        db.add(sala)

        db.flush()

        crear_sillas(
            db=db,
            sala=sala,
            general=general,
            preferencial=preferencial
        )


def run():

    db = SessionLocal()

    try:

        general, preferencial = (
            crear_tipos_silla(db)
        )

        for data in MULTIPLEX_DATA:

            existing = (
                db.execute(
                    select(Multiplex).where(
                        Multiplex.codigo
                        == data["codigo"]
                    )
                )
                .scalar_one_or_none()
            )

            if existing:

                print(
                    f"✓ Multiplex ya existe: "
                    f"{data['nombre']}"
                )

                continue

            multiplex = Multiplex(
                nombre=data["nombre"],
                codigo=data["codigo"],
                ciudad=data["ciudad"],
                direccion=data["direccion"],
                latitud=data["latitud"],
                longitud=data["longitud"],
                estaActivo=True
            )

            db.add(multiplex)

            db.flush()

            crear_salas(
                db=db,
                multiplex=multiplex,
                general=general,
                preferencial=preferencial
            )

            print(
                f"✓ Multiplex creado: "
                f"{multiplex.nombre}"
            )

        db.commit()

        print(
            "✓ Seed multiplex/salas/"
            "sillas completado."
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