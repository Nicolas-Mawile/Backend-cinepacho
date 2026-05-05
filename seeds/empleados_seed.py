"""Script to seed employees and users using existing services."""

import sys
import os
from datetime import date
from decimal import Decimal

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.infrastructure.repositories.empleado_repository import EmpleadoRepository
from app.domain.services.empleado_service import EmpleadoService
from app.infrastructure.models.cargoEnum import CargoEnum
from app.infrastructure.models.rol import Rol
from sqlalchemy import select

def seed_roles_if_needed(db):
    """Ensure basic roles exist."""
    roles = ["Cajero", "Administrador Multiplex", "Cliente"]
    for role_name in roles:
        stmt = select(Rol).where(Rol.nombre == role_name)
        existing = db.execute(stmt).scalar_one_or_none()
        if not existing:
            print(f"Creando rol: {role_name}")
            new_role = Rol(nombre=role_name)
            db.add(new_role)
    db.commit()

def run_seed():
    print("Iniciando semilla de empleados y usuarios...")
    db = SessionLocal()
    try:
        # 1. Asegurar roles
        seed_roles_if_needed(db)
        
        # 2. Instanciar repo y servicio
        repo = EmpleadoRepository(db)
        service = EmpleadoService()
        
        # 3. Datos de prueba
        empleados_data = [
            {
                "primer_nombre": "Carlos",
                "segundo_nombre": "Alberto",
                "primer_apellido": "Pérez",
                "segundo_apellido": "Gómez",
                "cedula_ciudadania": 10102020,
                "fecha_nacimiento": date(1985, 5, 20),
                "telefono": 3001234567,
                "email": "carlos.perez@example.com",
                "cargo": CargoEnum.cajero,
                "salario": 1200000,
                "multiplex_id": 1
            },
            {
                "primer_nombre": "Ana",
                "segundo_nombre": "María",
                "primer_apellido": "Rodríguez",
                "segundo_apellido": "López",
                "cedula_ciudadania": 20203030,
                "fecha_nacimiento": date(1992, 10, 15),
                "telefono": 3109876543,
                "email": "ana.rodriguez@example.com",
                "cargo": CargoEnum.director,
                "salario": 2500000,
                "multiplex_id": 1
            },
            {
                "primer_nombre": "Luis",
                "segundo_nombre": "",
                "primer_apellido": "Martínez",
                "segundo_apellido": "Ruiz",
                "cedula_ciudadania": 30304040,
                "fecha_nacimiento": date(1990, 3, 5),
                "telefono": 3201112233,
                "email": "luis.martinez@example.com",
                "cargo": CargoEnum.aseador,
                "salario": 1000000,
                "multiplex_id": 2
            }
        ]
        
        for data in empleados_data:
            # Verificar si ya existe por cédula
            existing = repo.buscar_por_cedula(str(data["cedula_ciudadania"]))
            if existing:
                print(f"Omitiendo empleado {data['primer_nombre']} (ya existe)")
                continue
            
            print(f"Creando empleado: {data['primer_nombre']} {data['primer_apellido']}...")
            service.crear_empleado(repo, data)
            
        print("✓ Semilla completada con éxito.")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error durante la semilla: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
