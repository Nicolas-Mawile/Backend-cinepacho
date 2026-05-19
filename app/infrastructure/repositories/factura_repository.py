from datetime import datetime

from sqlalchemy.orm import Session

from app.infrastructure.models.factura import Factura
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum


class FacturaRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, factura: Factura):

        self.db.add(factura)
        self.db.flush()
        self.db.refresh(factura)

        return factura

    def get_by_id(
        self,
        factura_id: int
    ):

        return (
            self.db.query(Factura)
            .filter(Factura.id == factura_id)
            .first()
        )

    def get_expired_reservas(self):

        return (
            self.db.query(Factura)
            .filter(
                Factura.estadoFactura == EstadoFacturaEnum.RESERVADA,
                Factura.fechaExpiracionReserva < datetime.utcnow()
            )
            .all()
        )