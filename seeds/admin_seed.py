"""Seed admin general."""
from sqlalchemy import select
from app.database import SessionLocal
from app.domain.services.empleado_service import (EmpleadoService)
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.cargoEnum import CargoEnum

ADMIN_DATA = {
    "nombres": "Admin",
    "apellidos": "General",
    "correo": "admin@gmail.com",
    "telefono": "3000000000",
    "password": "Admin123*",
    "cargo": CargoEnum.administrador,
    "salario": 10000000,
    "multiplexId": 1
}

def run():
    db = SessionLocal()
    repo = EmpleadoRepository(db)
    service = EmpleadoService(db)

    try:
        existing = (db.execute(select(Empleado).where(Empleado.correo == ADMIN_DATA["correo"])).scalar_one_or_none())
        if existing:
            print("✓ Admin ya existe.")
            return

        resultado = service.crearEmpleado(repo, ADMIN_DATA)
        print("✓ Admin creado:")
        print(resultado)

    except Exception as e:
        db.rollback()
        print(f"✗ Error seed admin: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()