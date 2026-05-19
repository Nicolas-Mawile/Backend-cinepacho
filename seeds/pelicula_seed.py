"""Seed de películas."""

from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.pelicula import (
    Pelicula
)


PELICULAS = [
    {
        "titulo": "Avengers: Endgame",
        "duracionMinutos": 181,
        "linkTrailer": (
            "https://youtube.com/watch?v=TcMBFSGVi1c"
        ),
        "linkPoster": (
            "https://image.tmdb.org/t/p/endgame.jpg"
        ),
        "sinopsis": (
            "Los Vengadores enfrentan "
            "su batalla final contra Thanos."
        )
    },
    {
        "titulo": "Interstellar",
        "duracionMinutos": 169,
        "linkTrailer": (
            "https://youtube.com/watch?v=zSWdZVtXT7E"
        ),
        "linkPoster": (
            "https://image.tmdb.org/t/p/interstellar.jpg"
        ),
        "sinopsis": (
            "Un grupo de astronautas "
            "viaja a través de un agujero "
            "de gusano para salvar la humanidad."
        )
    },
    {
        "titulo": "The Batman",
        "duracionMinutos": 176,
        "linkTrailer": (
            "https://youtube.com/watch?v=mqqft2x_Aa4"
        ),
        "linkPoster": (
            "https://image.tmdb.org/t/p/batman.jpg"
        ),
        "sinopsis": (
            "Batman investiga una serie "
            "de asesinatos en Gotham."
        )
    },
    {
        "titulo": "Spider-Man: No Way Home",
        "duracionMinutos": 148,
        "linkTrailer": (
            "https://youtube.com/watch?v=JfVOs4VSpmA"
        ),
        "linkPoster": (
            "https://image.tmdb.org/t/p/spiderman.jpg"
        ),
        "sinopsis": (
            "Peter Parker enfrenta "
            "el multiverso."
        )
    }
]


def run():

    db = SessionLocal()

    try:

        for data in PELICULAS:

            existing = (
                db.execute(
                    select(Pelicula).where(
                        Pelicula.titulo
                        == data["titulo"]
                    )
                )
                .scalar_one_or_none()
            )

            if existing:

                print(
                    f"✓ Película ya existe: "
                    f"{data['titulo']}"
                )

                continue

            pelicula = Pelicula(
                titulo=data["titulo"],
                duracionMinutos=data[
                    "duracionMinutos"
                ],
                linkTrailer=data[
                    "linkTrailer"
                ],
                linkPoster=data[
                    "linkPoster"
                ],
                sinopsis=data[
                    "sinopsis"
                ]
            )

            db.add(pelicula)

            print(
                f"✓ Película creada: "
                f"{pelicula.titulo}"
            )

        db.commit()

        print(
            "✓ Seed películas completado."
        )

    except Exception as e:

        db.rollback()

        print(
            f"✗ Error seed películas: {e}"
        )

        raise

    finally:

        db.close()


if __name__ == "__main__":

    run()