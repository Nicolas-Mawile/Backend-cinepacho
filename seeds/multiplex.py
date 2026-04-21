"""Seed data for multiplexes."""

import asyncio
import uuid

from app.models.multiplex import Multiplex
from app.models.sala import Sala
from app.models.silla import Silla
from app.database import AsyncSessionLocal 

async def run():
    async with AsyncSessionLocal() as db:

        multiplexes = [
            {
                "id": str(uuid.uuid4()),
                "nombre": "Titán Plaza",
                "codigo": "TITAN",
                "ciudad": "Bogotá",
                "direccion": "Av. Boyacá #80-94",
                "latitud": 4.6940,
                "longitud": -74.0790,
                "activo": True
            },
            {
                "id": str(uuid.uuid4()),
                "nombre": "Unicentro",
                "codigo": "UNICENTRO",
                "ciudad": "Bogotá",
                "direccion": "Cra. 15 #124-30",
                "latitud": 4.7035,
                "longitud": -74.0412,
                "activo": True
            },
            {
                "id": str(uuid.uuid4()),
                "nombre": "Plaza Central",
                "codigo": "PLAZA",
                "ciudad": "Bogotá",
                "direccion": "Av. NQS #38A-26",
                "latitud": 4.6306,
                "longitud": -74.0927,
                "activo": True
            },
            {
                "id": str(uuid.uuid4()),
                "nombre": "Gran Estación",
                "codigo": "GRAN_EST",
                "ciudad": "Bogotá",
                "direccion": "Av. El Dorado #69-63",
                "latitud": 4.6565,
                "longitud": -74.1068,
                "activo": True
            },
            {
                "id": str(uuid.uuid4()),
                "nombre": "Embajador",
                "codigo": "EMBAJADOR",
                "ciudad": "Bogotá",
                "direccion": "Centro",
                "latitud": 4.6097,
                "longitud": -74.0817,
                "activo": True
            },
            {
                "id": str(uuid.uuid4()),
                "nombre": "Las Américas",
                "codigo": "AMERICAS",
                "ciudad": "Bogotá",
                "direccion": "Av. Américas",
                "latitud": 4.6230,
                "longitud": -74.1400,
                "activo": True
            },
        ]

        for m in multiplexes:
            db.add(Multiplex(**m))

        await db.commit()
        print("Seed de multiplex ejecutado correctamente")


if __name__ == "__main__":
    asyncio.run(run())