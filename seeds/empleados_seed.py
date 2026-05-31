"""Seed de empleados."""
from sqlalchemy import select
from app.database import SessionLocal
from app.domain.services.empleado_service import (EmpleadoService)
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.cargoEnum import CargoEnum

EMPLEADOS = [
    # ── Multiplex 1 ─ Titán Plaza ──────────────────────────
    {
        "nombres": "Carlos",
        "apellidos": "Ramírez",
        "correo": "carlos@gmail.com",
        "telefono": "3001112233",
        "password": "Password123",
        "cargo": CargoEnum.director,
        "salario": 8000000,
        "multiplexId": 1,
    },
    {
        "nombres": "Laura",
        "apellidos": "Martínez",
        "correo": "lauraramirez@gmail.com",
        "telefono": "3002223344",
        "password": "Password123",
        "cargo": CargoEnum.administrador,
        "salario": 5000000,
        "multiplexId": 1,
    },
    # ── Multiplex 2 ─ Unicentro ────────────────────────────
    {
        "nombres": "Pedro",
        "apellidos": "Gómez",
        "correo": "pedro@gmail.com",
        "telefono": "3003334455",
        "password": "Password123",
        "cargo": CargoEnum.cajero,
        "salario": 1800000,
        "multiplexId": 2,
    },
    {
        "nombres": "Ana",
        "apellidos": "López",
        "correo": "ana@gmail.com",
        "telefono": "3004445566",
        "password": "Password123",
        "cargo": CargoEnum.despachador_comida,
        "salario": 1600000,
        "multiplexId": 2,
    },
    # ── Multiplex 3 ─ Plaza Central ────────────────────────
    {
        "nombres": "Sofía",
        "apellidos": "Torres",
        "correo": "sofia.emp@gmail.com",
        "telefono": "3005001122",
        "password": "Password123",
        "cargo": CargoEnum.cajero,
        "salario": 1900000,
        "multiplexId": 3,
    },
    {
        "nombres": "Diego",
        "apellidos": "Morales",
        "correo": "diego.emp@gmail.com",
        "telefono": "3005002233",
        "password": "Password123",
        "cargo": CargoEnum.director,
        "salario": 7500000,
        "multiplexId": 3,
    },
    # ── Multiplex 4 ─ Gran Estación ────────────────────────
    {
        "nombres": "Valentina",
        "apellidos": "Cruz",
        "correo": "valentina.emp@gmail.com",
        "telefono": "3005003344",
        "password": "Password123",
        "cargo": CargoEnum.administrador,
        "salario": 4800000,
        "multiplexId": 4,
    },
    {
        "nombres": "Santiago",
        "apellidos": "Roa",
        "correo": "santiago.emp@gmail.com",
        "telefono": "3005004455",
        "password": "Password123",
        "cargo": CargoEnum.despachador_comida,
        "salario": 1700000,
        "multiplexId": 4,
    },
    # ── Multiplex 5 ─ Embajador ────────────────────────────
    {
        "nombres": "Camila",
        "apellidos": "Vargas",
        "correo": "camila.emp@gmail.com",
        "telefono": "3005005566",
        "password": "Password123",
        "cargo": CargoEnum.cajero,
        "salario": 2000000,
        "multiplexId": 5,
    },
    {
        "nombres": "Andrés",
        "apellidos": "Pardo",
        "correo": "andres.emp@gmail.com",
        "telefono": "3005006677",
        "password": "Password123",
        "cargo": CargoEnum.aseador,
        "salario": 1500000,
        "multiplexId": 5,
    },
    # ── Multiplex 6 ─ Las Américas ─────────────────────────
    {
        "nombres": "Isabella",
        "apellidos": "Medina",
        "correo": "isabella.emp@gmail.com",
        "telefono": "3005007788",
        "password": "Password123",
        "cargo": CargoEnum.cajero,
        "salario": 1850000,
        "multiplexId": 6,
    },
    {
        "nombres": "Felipe",
        "apellidos": "Herrera",
        "correo": "felipe.emp@gmail.com",
        "telefono": "3005008899",
        "password": "Password123",
        "cargo": CargoEnum.encargadoSala,
        "salario": 2200000,
        "multiplexId": 6,
    },
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
                continue
            # ==================================
            # CREAR EMPLEADO
            # ==================================
            resultado = service.crearEmpleado(repo, data)

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()