from sqlalchemy.orm import Session
from app.infrastructure.models.recompensaBoleta import (RecompensaBoleta)

class RecompensaRepository:

    def __init__(self, db: Session):
        self.db = db

    def crear(self, recompensa):

        self.db.add(recompensa)

        return recompensa

    def obtener_disponibles(
        self,
        cliente_id,
        fecha_actual,
    ):

        return (
            self.db.query(RecompensaBoleta)
            .filter(
                RecompensaBoleta.clienteId == cliente_id,
                RecompensaBoleta.utilizada == False,
                RecompensaBoleta.fechaVencimiento > fecha_actual,
            )
            .all()
        )

    def obtener_primera_disponible(
        self,
        cliente_id,
        fecha_actual,
    ):

        return (
            self.db.query(RecompensaBoleta)
            .filter(
                RecompensaBoleta.clienteId == cliente_id,
                RecompensaBoleta.utilizada == False,
                RecompensaBoleta.fechaVencimiento > fecha_actual,
            )
            .first()
        )