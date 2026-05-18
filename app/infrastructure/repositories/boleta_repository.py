from datetime import datetime

from sqlalchemy.orm import Session

from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum


class BoletaRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        boleta: Boleta
    ):

        self.db.add(boleta)
        self.db.flush()
        self.db.refresh(boleta)

        return boleta

    def silla_ocupada_o_reservada(
        self,
        funcion_id: int,
        silla_id: int
    ):

        boleta = (
            self.db.query(Boleta)
            .join(
                DetalleFactura,
                DetalleFactura.boletaId == Boleta.id
            )
            .join(
                Factura,
                Factura.id == DetalleFactura.facturaId
            )
            .filter(
                Boleta.funcionId == funcion_id,
                Boleta.sillaId == silla_id,
                (
                    (
                        Factura.estadoFactura
                        == EstadoFacturaEnum.PAGADA
                    )
                    |
                    (
                        (
                            Factura.estadoFactura
                            == EstadoFacturaEnum.RESERVADA
                        )
                        &
                        (
                            Factura.fechaExpiracionReserva
                            > datetime.utcnow()
                        )
                    )
                )
            )
            .first()
        )

        return boleta is not None