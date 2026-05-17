"""Seed de empleados."""
from sqlalchemy import select
from app.database import SessionLocal
from app.domain.services.empleado_service import (EmpleadoService)
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.cargoEnum import CargoEnum

EMPLEADOS = [
    {
        "nombres": "Carlos",
        "apellidos": "Ramírez",
        "correo": "carlos@gmail.com",
        "telefono": "3001112233",
        "password": "Password123",
        "cargo": CargoEnum.director,
        "salario": 8000000,
        "multiplexId": 1
    },
    {
        "nombres": "Laura",
        "apellidos": "Martínez",
        "correo": "lauraramirez@gmail.com",
        "telefono": "3002223344",
        "password": "Password123",
        "cargo": CargoEnum.administrador,
        "salario": 5000000,
        "multiplexId": 1
    },
    {
        "nombres": "Pedro",
        "apellidos": "Gómez",
        "correo": "pedro@gmail.com",
        "telefono": "3003334455",
        "password": "Password123",
        "cargo": CargoEnum.cajero,
        "salario": 1800000,
        "multiplexId": 2
    },
    {
        "nombres": "Ana",
        "apellidos": "López",
        "correo": "ana@gmail.com",
        "telefono": "3004445566",
        "password": "Password123",
        "cargo": CargoEnum.despachador_comida,
        "salario": 1600000,
        "multiplexId": 2
    }
]


def run():
    db = SessionLocal()
    repo = EmpleadoRepository(db)
    service = EmpleadoService(db)
    try:
        for data in EMPLEADOS:
            # ==================================
            # VALIDAR EXISTENCIA
            # ==================================
            existing = (db.execute(select(Empleado).where(Empleado.correo == data["correo"])).scalar_one_or_none())
            if existing:
                print(f"✓ Empleado ya existe: {existing.correoLaboral}")
                continue
            # ==================================
            # CREAR EMPLEADO
            # ==================================
            resultado = service.crearEmpleado(repo, data)
            print(f"✓ Empleado creado: {resultado['empleado']['correoLaboral']}")

        print("✓ Seed empleados completado.")

    except Exception as e:
        db.rollback()
        print(f"✗ Error seed empleados: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()