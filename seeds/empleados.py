"""Seed de empleados por rol."""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

empleados_seed = [
    {
        "codigo_empleado": "EMP-001",
        "nombre": "Juan Cajero",
        "correo": "cajero@cinepacho.com",
        "password_hash": pwd_context.hash("Cajero123!"),
        "cargo": "cajero",
        "multiplex_id": 1,
        "activo": True,
    },
    {
        "codigo_empleado": "EMP-002",
        "nombre": "Maria Admin MX",
        "correo": "adminmx@cinepacho.com",
        "password_hash": pwd_context.hash("AdminMx123!"),
        "cargo": "admin_multiplex",
        "multiplex_id": 1,
        "activo": True,
    },
    {
        "codigo_empleado": "EMP-003",
        "nombre": "Carlos Admin General",
        "correo": "admin@cinepacho.com",
        "password_hash": pwd_context.hash("AdminGen123!"),
        "cargo": "admin_general",
        "multiplex_id": None,
        "activo": True,
    },
]