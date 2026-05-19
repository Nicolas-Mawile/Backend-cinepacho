"""Seed data for peliculas."""

from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.pelicula import Pelicula


PELICULAS_DATA = [
    {
        "titulo": "Avengers: Doomsday",
        "duracionMinutos": 149,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder1",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder1.jpg",
        "sinopsis": "Los Vengadores enfrentan su mayor amenaza cuando el Doctor Doom reúne un ejército para dominar el mundo.",
        "estaActiva": True,
    },
    {
        "titulo": "Misión Imposible: Sentencia Final",
        "duracionMinutos": 163,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder2",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder2.jpg",
        "sinopsis": "Ethan Hunt regresa en su misión más peligrosa para detener una inteligencia artificial fuera de control.",
        "estaActiva": True,
    },
    {
        "titulo": "El Señor de los Anillos: La Guerra de los Rohirrim",
        "duracionMinutos": 134,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder3",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder3.jpg",
        "sinopsis": "La historia épica del rey Helm Hammerhand y la fundación del Abismo de Helm.",
        "estaActiva": True,
    },
    {
        "titulo": "Sonic 3: La Película",
        "duracionMinutos": 110,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder4",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder4.jpg",
        "sinopsis": "Sonic, Tails y Knuckles se unen para enfrentar a Shadow, el erizo definitivo.",
        "estaActiva": True,
    },
    {
        "titulo": "Paddington en Perú",
        "duracionMinutos": 106,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder5",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder5.jpg",
        "sinopsis": "Paddington viaja a Perú para visitar a su querida tía Lucy en el Hogar de Osos.",
        "estaActiva": True,
    },
    {
        "titulo": "Gladiador II",
        "duracionMinutos": 148,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder6",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder6.jpg",
        "sinopsis": "Años después de la muerte de Máximo, un nuevo guerrero llega a los coliseos de Roma buscando justicia.",
        "estaActiva": True,
    },
    {
        "titulo": "Wicked",
        "duracionMinutos": 160,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder7",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder7.jpg",
        "sinopsis": "La historia de la amistad entre Glinda y Elphaba antes de convertirse en las brujas de Oz.",
        "estaActiva": True,
    },
    {
        "titulo": "Moana 2",
        "duracionMinutos": 100,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder8",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder8.jpg",
        "sinopsis": "Moana emprende un nuevo viaje hacia los mares lejanos de Oceanía en una misión inesperada.",
        "estaActiva": True,
    },
    {
        "titulo": "Kraven el Cazador",
        "duracionMinutos": 127,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder9",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder9.jpg",
        "sinopsis": "El origen del cazador más peligroso del universo Marvel y su código de honor.",
        "estaActiva": False,
    },
    {
        "titulo": "Dune: Parte Dos",
        "duracionMinutos": 166,
        "linkTrailer": "https://www.youtube.com/watch?v=placeholder10",
        "linkPoster": "https://image.tmdb.org/t/p/w500/placeholder10.jpg",
        "sinopsis": "Paul Atreides se une a los Fremen y emprende un viaje de venganza contra los conspiradores que destruyeron a su familia.",
        "estaActiva": False,
    },
]


def run():
    """
    Inserta películas iniciales.
    Idempotente: no duplica registros.
    """
    with SessionLocal() as db:
        try:
            existing = db.execute(select(Pelicula).limit(1)).scalar_one_or_none()
            if existing:
                print("✔ Seed peliculas: ya existen registros, omitiendo.")
                return

            for data in PELICULAS_DATA:
                pelicula = Pelicula(**data)
                db.add(pelicula)

            db.commit()
            print(f"✔ Seed peliculas: {len(PELICULAS_DATA)} películas insertadas.")

        except Exception as e:
            db.rollback()
            print(f"✗ Error en seed peliculas: {e}")
            raise


if __name__ == "__main__":
    run()