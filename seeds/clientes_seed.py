"""Seed de clientes."""
from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.usuario import (Usuario)
from app.infrastructure.models.cliente import (Cliente)
from app.infrastructure.models.rol import (Rol)
from app.domain.services.auth_service import (AuthService)

CLIENTES = [
    {
        "nombres": "Juan",
        "apellidos": "Gómez",
        "correo": "juan@gmail.com",
        "telefono": "3000001111",
        "password": "Password123",
        "puntosAcumulados": 0,
    },
    {
        "nombres": "Laura",
        "apellidos": "Ramírez",
        "correo": "laura@gmail.com",
        "telefono": "3000002222",
        "password": "Password123",
        "puntosAcumulados": 0,
    },
    {
        "nombres": "Nicolas",
        "apellidos": "Castro Rivera",
        "correo": "nicolascr333@gmail.com",
        "telefono": "3100001111",
        "password": "Password123",
        "puntosAcumulados": 80,
    },
]

def run():
    db = SessionLocal()
    authService = AuthService()
    try:
        rolCliente = (db.execute(select(Rol).where( Rol.nombre == "CLIENTE")).scalar_one())
        for data in CLIENTES:
            existing = (db.execute(select(Cliente).where(Cliente.correo == data["correo"])).scalar_one_or_none())
            if existing:
                continue
            # ==================================
            # CLIENTE
            # ==================================
            cliente = Cliente(
                nombres=data["nombres"],
                apellidos=data["apellidos"],
                correo=data["correo"],
                telefono=data["telefono"],
                activo=True,
                puntosAcumulados=data.get("puntosAcumulados", 0),
            )
            db.add(cliente)
            db.flush()

            # ==================================
            # USUARIO
            # ==================================
            usuario = Usuario(clienteId=cliente.id, rolId=rolCliente.id, 
                              passwordHash=(authService.hashPassword(data["password"])))

            db.add(usuario)
            db.commit()

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()