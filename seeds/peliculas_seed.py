"""Seed data for peliculas."""

from sqlalchemy import select

from app.database import SessionLocal
from app.infrastructure.models.pelicula import Pelicula


PELICULAS_DATA = [
    {
        "titulo": "Avengers: Doomsday",
        "duracionMinutos": 149,
        "linkTrailer": "https://www.youtube.com/watch?v=TcMBFSGVi1c",
        "linkPoster": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg",
        "sinopsis": (
            "Los Vengadores enfrentan su mayor amenaza "
            "cuando el Doctor Doom reúne un ejército "
            "para dominar el mundo."
        ),
        "estaActiva": True,
    },
    {
        "titulo": "Misión Imposible: Sentencia Final",
        "duracionMinutos": 163,
        "linkTrailer": "https://www.youtube.com/watch?v=avz06PDqDbM",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder2.jpg",
        "sinopsis": (
            "Ethan Hunt regresa en su misión más peligrosa "
            "para detener una inteligencia artificial "
            "fuera de control."
        ),
        "estaActiva": True,
    },
    {
        "titulo": "El Señor de los Anillos: La Guerra de los Rohirrim",
        "duracionMinutos": 134,
        "linkTrailer": "https://www.youtube.com/watch?v=gCUg6Td5fgQ",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder3.jpg",
        "sinopsis": (
            "La historia épica del rey Helm Hammerhand "
            "y la fundación del Abismo de Helm."
        ),
        "estaActiva": True,
    },
    {
        "titulo": "Sonic 3: La Película",
        "duracionMinutos": 110,
        "linkTrailer": "https://www.youtube.com/watch?v=qSu6i2iFMO0",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder4.jpg",
        "sinopsis": (
            "Sonic, Tails y Knuckles se unen para "
            "enfrentar a Shadow."
        ),
        "estaActiva": True,
    },
    {
        "titulo": "Paddington en Perú",
        "duracionMinutos": 106,
        "linkTrailer": "https://www.youtube.com/watch?v=lKgitu25ZAg",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder5.jpg",
        "sinopsis": (
            "Paddington viaja a Perú para visitar "
            "a su querida tía Lucy."
        ),
        "estaActiva": True,
    },
]


def validate_pelicula_data(data: dict):

    if not data["titulo"].strip():
        raise ValueError("El título no puede estar vacío")

    if data["duracionMinutos"] <= 0:
        raise ValueError(
            f"Duración inválida para "
            f"{data['titulo']}"
        )

    if len(data["titulo"]) > 255:
        raise ValueError(
            f"Título demasiado largo: "
            f"{data['titulo']}"
        )


def create_or_update_pelicula(
    db,
    data: dict
):

    pelicula = db.execute(
        select(Pelicula).where(
            Pelicula.titulo == data["titulo"]
        )
    ).scalar_one_or_none()

    if pelicula:

        pelicula.duracionMinutos = data["duracionMinutos"]
        pelicula.linkTrailer = data["linkTrailer"]
        pelicula.linkPoster = data["linkPoster"]
        pelicula.sinopsis = data["sinopsis"]
        pelicula.estaActiva = data["estaActiva"]

        print(
            f"🔄 Película actualizada: "
            f"{pelicula.titulo}"
        )

        return

    pelicula = Pelicula(**data)

    db.add(pelicula)

    print(
        f"✅ Película creada: "
        f"{pelicula.titulo}"
    )


def validate_integrity(db):

    peliculas = db.execute(
        select(Pelicula)
    ).scalars().all()

    titulos = set()

    for pelicula in peliculas:

        if pelicula.titulo in titulos:

            raise Exception(
                f"Película duplicada: "
                f"{pelicula.titulo}"
            )

        titulos.add(pelicula.titulo)

        if pelicula.duracionMinutos <= 0:

            raise Exception(
                f"Duración inválida: "
                f"{pelicula.titulo}"
            )

    print("✅ Validación de películas completada")


def run():

    with SessionLocal() as db:

        try:

            print("\n🎬 Iniciando seed películas...\n")

            for data in PELICULAS_DATA:

                validate_pelicula_data(data)

                create_or_update_pelicula(
                    db,
                    data
                )

            db.commit()

            validate_integrity(db)

            print(
                f"\n✅ Seed películas completado "
                f"({len(PELICULAS_DATA)} películas)\n"
            )

        except Exception as e:

            db.rollback()

            print(
                f"\n❌ Error en seed películas:\n{e}"
            )

            raise e


if __name__ == "__main__":

    run()