from sqlalchemy import select
from app.infrastructure.models.evaluacion import (Evaluacion)
from app.infrastructure.base_repository import (AbstractRepository)

class EvaluacionRepository(AbstractRepository[Evaluacion]):

    def create(self, evaluacion: Evaluacion):

        self.db.add(evaluacion)

        self.db.commit()

        self.db.refresh(evaluacion)

        return evaluacion

    def get(self, evaluacion_id: int):

        return (
            self.db.query(Evaluacion)
            .filter(Evaluacion.id == evaluacion_id)
            .first()
        )

    def get_all(self):

        return self.db.query(Evaluacion).all()

    def update(self):

        self.db.commit()

    def delete(self, evaluacion: Evaluacion):

        self.db.delete(evaluacion)

        self.db.commit()

    def exists(self, evaluacion_id: int):

        return (
            self.db.query(Evaluacion)
            .filter(Evaluacion.id == evaluacion_id)
            .first()
            is not None
        )

    def add(self, entity: Evaluacion):
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def existe_evaluacion_pelicula(self, cliente_id: int, funcion_id: int, pelicula_id: int):
        stmt = select(Evaluacion).where(
            Evaluacion.cliente_id == cliente_id,
            Evaluacion.funcion_id == funcion_id,
            Evaluacion.pelicula_id == pelicula_id)

        return (self.db.execute(stmt).scalar_one_or_none())


    def existe_evaluacion_servicio(self, cliente_id: int, factura_id: int, servicio_id: int):

        stmt = select(Evaluacion).where(
            Evaluacion.cliente_id == cliente_id,
            Evaluacion.factura_id == factura_id,
            Evaluacion.servicio_id == servicio_id)

        return (self.db.execute(stmt).scalar_one_or_none())