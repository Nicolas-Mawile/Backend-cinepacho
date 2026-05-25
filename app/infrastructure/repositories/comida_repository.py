from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.comida import Comida


class ComidaRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # CREATE
    # -----------------------------

    def create(
        self,
        nombre: str,
        precio: float,
        imagenUrl: str | None = None
    ) -> Comida:

        comida = Comida(
            nombre=nombre,
            precio=precio,
            imagenUrl=imagenUrl
        )

        self.db.add(comida)
        self.db.commit()
        self.db.refresh(comida)

        return comida

    # -----------------------------
    # GET ALL
    # -----------------------------

    def get_all(self) -> list[Comida]:

        return self.db.execute(
            select(Comida)
            .order_by(Comida.nombre)
        ).scalars().all()

    # -----------------------------
    # GET BY ID
    # -----------------------------

    def get_by_id(
        self,
        comida_id: int
    ) -> Comida | None:

        return self.db.execute(
            select(Comida).where(
                Comida.id == comida_id
            )
        ).scalar_one_or_none()

    # -----------------------------
    # GET BY NAME
    # -----------------------------

    def get_by_nombre(
        self,
        nombre: str
    ) -> Comida | None:

        return self.db.execute(
            select(Comida).where(
                Comida.nombre == nombre
            )
        ).scalar_one_or_none()

    # -----------------------------
    # UPDATE
    # -----------------------------

    def update(
        self,
        comida: Comida,
        data: dict
    ) -> Comida:

        for key, value in data.items():
            setattr(comida, key, value)

        self.db.commit()
        self.db.refresh(comida)

        return comida

    # -----------------------------
    # DELETE
    # -----------------------------

    def delete(
        self,
        comida: Comida
    ) -> None:

        self.db.delete(comida)
        self.db.commit()