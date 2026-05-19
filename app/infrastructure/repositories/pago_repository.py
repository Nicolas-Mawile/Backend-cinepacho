"""Pago repository."""

from app.infrastructure.models.pago import (
    Pago
)

from ..base_repository import (
    AbstractRepository
)


class PagoRepository(
    AbstractRepository[Pago]
):

    def __init__(self, db):

        super().__init__(db)

    # =====================================================
    # CRUD ABSTRACT METHODS
    # =====================================================

    def add(
        self,
        entity: Pago
    ) -> Pago:

        self.db.add(entity)

        self.db.flush()

        self.db.refresh(entity)

        return entity

    def get(
        self,
        entity_id: int
    ):

        return (
            self.db.query(Pago)
            .filter(
                Pago.id == entity_id
            )
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10
    ):

        return (
            self.db.query(Pago)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        entity_id: int,
        data: dict
    ):

        pago = self.get(entity_id)

        if not pago:

            return None

        for key, value in data.items():

            setattr(
                pago,
                key,
                value
            )

        self.db.flush()

        self.db.refresh(pago)

        return pago

    def delete(
        self,
        entity_id: int
    ) -> bool:

        pago = self.get(entity_id)

        if not pago:

            return False

        self.db.delete(pago)

        return True

    def exists(
        self,
        entity_id: int
    ) -> bool:

        return (
            self.db.query(Pago)
            .filter(
                Pago.id == entity_id
            )
            .first()
            is not None
        )