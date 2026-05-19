"""Boleta repository."""

from sqlalchemy.orm import joinedload

from app.infrastructure.models.boleta import (
    Boleta
)

from app.infrastructure.models.factura import (
    Factura
)

from app.infrastructure.models.detalleFactura import (
    DetalleFactura
)

from app.infrastructure.models.EstadoFacturaEnum import (
    EstadoFacturaEnum
)

from ..base_repository import (
    AbstractRepository
)


class BoletaRepository(
    AbstractRepository[Boleta]
):

    def __init__(self, db):

        super().__init__(db)

    # =====================================================
    # CRUD ABSTRACT METHODS
    # =====================================================

    def add(
        self,
        entity: Boleta
    ) -> Boleta:

        self.db.add(entity)

        self.db.flush()

        self.db.refresh(entity)

        return entity

    def get(
        self,
        entity_id: int
    ):

        return (
            self.db.query(Boleta)
            .filter(
                Boleta.id == entity_id
            )
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10
    ):

        return (
            self.db.query(Boleta)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        entity_id: int,
        data: dict
    ):

        boleta = self.get(entity_id)

        if not boleta:

            return None

        for key, value in data.items():

            setattr(
                boleta,
                key,
                value
            )

        self.db.flush()

        self.db.refresh(boleta)

        return boleta

    def delete(
        self,
        entity_id: int
    ) -> bool:

        boleta = self.get(entity_id)

        if not boleta:

            return False

        self.db.delete(boleta)

        return True

    def exists(
        self,
        entity_id: int
    ) -> bool:

        return (
            self.db.query(Boleta)
            .filter(
                Boleta.id == entity_id
            )
            .first()
            is not None
        )

    # =====================================================
    # CUSTOM METHODS
    # =====================================================

    def existe_boleta_activa(
        self,
        funcion_id: int,
        silla_id: int
    ) -> bool:

        boleta = (
            self.db.query(Boleta)
            .join(
                DetalleFactura,
                DetalleFactura.boletaId
                == Boleta.id
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .filter(
                Boleta.funcionId
                == funcion_id,

                Boleta.sillaId
                == silla_id,

                Factura.estadoFactura.in_([
                    EstadoFacturaEnum.RESERVADA,
                    EstadoFacturaEnum.PAGADA
                ])
            )
            .first()
        )

        return boleta is not None

    def get_boletas_activas_funcion(
        self,
        funcion_id: int
    ):

        return (
            self.db.query(Boleta)
            .join(
                DetalleFactura,
                DetalleFactura.boletaId
                == Boleta.id
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .options(
                joinedload(Boleta.silla),
                joinedload(Boleta.funcion)
            )
            .filter(
                Boleta.funcionId
                == funcion_id,

                Factura.estadoFactura.in_([
                    EstadoFacturaEnum.RESERVADA,
                    EstadoFacturaEnum.PAGADA
                ])
            )
            .all()
        )

    def get_sillas_reservadas(
        self,
        funcion_id: int
    ):

        return (
            self.db.query(Boleta)
            .join(
                DetalleFactura,
                DetalleFactura.boletaId
                == Boleta.id
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .filter(
                Boleta.funcionId
                == funcion_id,

                Factura.estadoFactura
                == EstadoFacturaEnum.RESERVADA
            )
            .all()
        )

    def get_sillas_ocupadas(
        self,
        funcion_id: int
    ):

        return (
            self.db.query(Boleta)
            .join(
                DetalleFactura,
                DetalleFactura.boletaId
                == Boleta.id
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .filter(
                Boleta.funcionId
                == funcion_id,

                Factura.estadoFactura
                == EstadoFacturaEnum.PAGADA
            )
            .all()
        )

    def get_boletas_cliente(
        self,
        cliente_id: int
    ):

        return (
            self.db.query(Boleta)
            .join(
                DetalleFactura,
                DetalleFactura.boletaId
                == Boleta.id
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .options(
                joinedload(Boleta.funcion),
                joinedload(Boleta.silla)
            )
            .filter(
                Factura.clienteId
                == cliente_id,

                Factura.estadoFactura
                == EstadoFacturaEnum.PAGADA
            )
            .all()
        )