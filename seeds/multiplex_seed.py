from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.tipoSilla import TipoSilla


MULTIPLEX_DATA = [
    {
        "nombre": "Titán Plaza",
        "codigo": "TIT",
        "ciudad": "Bogotá",
        "direccion": "Calle 80 #69Q-85",
        "latitud": Decimal("4.694928"),
        "longitud": Decimal("-74.082200"),
    },
    {
        "nombre": "Unicentro",
        "codigo": "UNI",
        "ciudad": "Bogotá",
        "direccion": "Av. 15 #124-30",
        "latitud": Decimal("4.701594"),
        "longitud": Decimal("-74.042420"),
    },
    {
        "nombre": "Plaza Central",
        "codigo": "PLC",
        "ciudad": "Bogotá",
        "direccion": "Carrera 65 #11-50",
        "latitud": Decimal("4.628660"),
        "longitud": Decimal("-74.121750"),
    },
    {
        "nombre": "Gran Estación",
        "codigo": "GRE",
        "ciudad": "Bogotá",
        "direccion": "Av. Calle 26 #62-47",
        "latitud": Decimal("4.648969"),
        "longitud": Decimal("-74.102120"),
    },
    {
        "nombre": "Embajador",
        "codigo": "EMB",
        "ciudad": "Bogotá",
        "direccion": "Av. Carrera 24 #52-25",
        "latitud": Decimal("4.640720"),
        "longitud": Decimal("-74.084310"),
    },
    {
        "nombre": "Las Américas",
        "codigo": "AME",
        "ciudad": "Bogotá",
        "direccion": "Cra. 71D #6-94 Sur",
        "latitud": Decimal("4.605310"),
        "longitud": Decimal("-74.141150"),
    },
]


SALAS_POR_MULTIPLEX = 5

FILAS_GENERALES = 4
FILAS_PREFERENCIALES = 2

COLUMNAS = 10

TOTAL_GENERALES = 40
TOTAL_PREFERENCIALES = 20


def get_or_create_tipos_silla(db: Session):

    general = db.execute(
        select(TipoSilla).where(
            TipoSilla.nombre == "GENERAL"
        )
    ).scalar_one_or_none()

    if not general:

        general = TipoSilla(
            nombre="GENERAL",
            precio=11000
        )

        db.add(general)
        db.commit()
        db.refresh(general)

        print("✅ Tipo GENERAL creado")

    preferencial = db.execute(
        select(TipoSilla).where(
            TipoSilla.nombre == "PREFERENCIAL"
        )
    ).scalar_one_or_none()

    if not preferencial:

        preferencial = TipoSilla(
            nombre="PREFERENCIAL",
            precio=15000
        )

        db.add(preferencial)
        db.commit()
        db.refresh(preferencial)

        print("✅ Tipo PREFERENCIAL creado")

    return general, preferencial


def create_multiplex_if_not_exists(
    db: Session,
    multiplex_data: dict
):

    multiplex = db.execute(
        select(Multiplex).where(
            Multiplex.codigo == multiplex_data["codigo"]
        )
    ).scalar_one_or_none()

    if multiplex:

        print(
            f"ℹ️ Multiplex ya existe: "
            f"{multiplex.nombre}"
        )

        return multiplex

    multiplex = Multiplex(
        nombre=multiplex_data["nombre"],
        codigo=multiplex_data["codigo"],
        ciudad=multiplex_data["ciudad"],
        direccion=multiplex_data["direccion"],
        latitud=float(multiplex_data["latitud"]),
        longitud=float(multiplex_data["longitud"]),
        estaActivo=True
    )

    db.add(multiplex)
    db.commit()
    db.refresh(multiplex)

    print(f"✅ Multiplex creado: {multiplex.nombre}")

    return multiplex


def create_salas_if_needed(
    db: Session,
    multiplex: Multiplex
):

    salas_existentes = db.execute(
        select(Sala).where(
            Sala.multiplexId == multiplex.id
        )
    ).scalars().all()

    cantidad_actual = len(salas_existentes)

    if cantidad_actual >= SALAS_POR_MULTIPLEX:

        print(
            f"ℹ️ {multiplex.nombre} ya tiene "
            f"{cantidad_actual} salas"
        )

        return salas_existentes

    for numero in range(
        cantidad_actual + 1,
        SALAS_POR_MULTIPLEX + 1
    ):

        sala = Sala(
            numero=numero,
            multiplexId=multiplex.id,
            estaActiva=True,
            capacidadTotal=60,
            capacidadPreferencial=20
        )

        db.add(sala)

    db.commit()

    print(
        f"✅ Salas creadas para "
        f"{multiplex.nombre}"
    )

    return db.execute(
        select(Sala).where(
            Sala.multiplexId == multiplex.id
        )
    ).scalars().all()


def create_sillas_if_needed(
    db: Session,
    sala: Sala,
    tipo_general: TipoSilla,
    tipo_preferencial: TipoSilla
):

    sillas_existentes = db.execute(
        select(Silla).where(
            Silla.salaId == sala.id
        )
    ).scalars().all()

    if len(sillas_existentes) >= 60:

        print(
            f"ℹ️ Sala {sala.numero} ya tiene "
            f"{len(sillas_existentes)} sillas"
        )

        return

    existentes = {
        (s.fila, s.columna)
        for s in sillas_existentes
    }

    # -------------------------
    # GENERALES
    # -------------------------

    for fila in range(1, FILAS_GENERALES + 1):

        for columna in range(1, COLUMNAS + 1):

            if (fila, columna) in existentes:
                continue

            silla = Silla(
                fila=fila,
                columna=columna,
                salaId=sala.id,
                tipoSillaId=tipo_general.id,
                estaActiva=True
            )

            db.add(silla)

    # -------------------------
    # PREFERENCIALES
    # -------------------------

    for fila in range(
        FILAS_GENERALES + 1,
        FILAS_GENERALES + FILAS_PREFERENCIALES + 1
    ):

        for columna in range(1, COLUMNAS + 1):

            if (fila, columna) in existentes:
                continue

            silla = Silla(
                fila=fila,
                columna=columna,
                salaId=sala.id,
                tipoSillaId=tipo_preferencial.id,
                estaActiva=True
            )

            db.add(silla)

    db.commit()

    print(
        f"✅ Sillas creadas para "
        f"Sala {sala.numero}"
    )


def validate_integrity(db: Session):

    multiplexes = db.execute(
        select(Multiplex)
    ).scalars().all()

    for multiplex in multiplexes:

        salas = db.execute(
            select(Sala).where(
                Sala.multiplexId == multiplex.id
            )
        ).scalars().all()

        if len(salas) != 5:

            raise Exception(
                f"{multiplex.nombre} no tiene 5 salas"
            )

        for sala in salas:

            sillas = db.execute(
                select(Silla).where(
                    Silla.salaId == sala.id
                )
            ).scalars().all()

            if len(sillas) != 60:

                raise Exception(
                    f"Sala {sala.numero} no tiene 60 sillas"
                )

            generales = [
                s for s in sillas
                if s.tipoSilla.nombre == "GENERAL"
            ]

            preferenciales = [
                s for s in sillas
                if s.tipoSilla.nombre == "PREFERENCIAL"
            ]

            if len(generales) != TOTAL_GENERALES:

                raise Exception(
                    f"Sala {sala.numero} "
                    f"no tiene 40 generales"
                )

            if len(preferenciales) != TOTAL_PREFERENCIALES:

                raise Exception(
                    f"Sala {sala.numero} "
                    f"no tiene 20 preferenciales"
                )

    print("✅ Validación completada correctamente")


def run():

    db = SessionLocal()

    try:

        print("\n🎬 Iniciando seed multiplex...\n")

        tipo_general, tipo_preferencial = (
            get_or_create_tipos_silla(db)
        )

        for multiplex_data in MULTIPLEX_DATA:

            multiplex = create_multiplex_if_not_exists(
                db,
                multiplex_data
            )

            salas = create_salas_if_needed(
                db,
                multiplex
            )

            for sala in salas:

                create_sillas_if_needed(
                    db,
                    sala,
                    tipo_general,
                    tipo_preferencial
                )

        validate_integrity(db)

        print("\n✅ Seed completado correctamente\n")

    except Exception as e:

        db.rollback()

        print(f"\n❌ Error ejecutando seed:\n{e}")

        raise e

    finally:

        db.close()


if __name__ == "__main__":

    run()