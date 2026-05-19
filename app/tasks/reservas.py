import asyncio

from app.database import SessionLocal

from app.domain.services.checkout_service import (
    CheckoutService
)


async def limpiar_reservas_expiradas():

    while True:

        db = SessionLocal()

        try:

            service = CheckoutService(db)

            service.cancelar_reservas_expiradas()

        except Exception as e:

            print(
                "Error limpiando reservas:",
                str(e)
            )

        finally:

            db.close()

        # ejecutar cada minuto

        await asyncio.sleep(60)