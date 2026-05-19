from sqlalchemy.orm import Session

from app.infrastructure.models.funcion import Funcion


class FuncionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        funcion_id: int
    ):

        return (
            self.db.query(Funcion)
            .filter(Funcion.id == funcion_id)
            .first()
        )