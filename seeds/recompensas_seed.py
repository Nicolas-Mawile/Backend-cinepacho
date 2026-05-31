"""Seed de recompensas — crea RecompensaBoleta para clientes del seed con 100 puntos."""
from datetime import datetime, timedelta
from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.recompensaBoleta import RecompensaBoleta

CORREOS_SEED = {"juan@gmail.com", "laura@gmail.com", "nicolascr333@gmail.com"}


def run():
    with SessionLocal() as db:
        try:
            clientes = db.execute(
                select(Cliente).where(
                    Cliente.correo.in_(CORREOS_SEED),
                    Cliente.puntosAcumulados >= 100,
                )
            ).scalars().all()

            creadas = 0
            for cliente in clientes:
                ya_tiene = db.execute(
                    select(RecompensaBoleta).where(
                        RecompensaBoleta.clienteId == cliente.id,
                        RecompensaBoleta.utilizada == False,
                    )
                ).scalar_one_or_none()

                if ya_tiene:
                    continue

                ahora = datetime.now()
                recompensa = RecompensaBoleta(
                    clienteId=cliente.id,
                    fechaOtorgamiento=ahora,
                    fechaVencimiento=ahora + timedelta(days=180),
                    utilizada=False,
                )
                db.add(recompensa)
                creadas += 1

            db.commit()
            print(f"✅ recompensas_seed completado ({creadas} recompensas creadas)")

        except Exception as e:
            db.rollback()
            raise
