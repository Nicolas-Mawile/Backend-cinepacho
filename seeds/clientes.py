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
        "password": "Password123"
    },
    {
        "nombres": "Laura",
        "apellidos": "Ramírez",
        "correo": "laura@gmail.com",
        "telefono": "3000002222",
        "password": "Password123"
    }
]

def run():
    db = SessionLocal()
    authService = AuthService()

    try:
        rolCliente = db.execute(select(Rol).where(Rol.nombre == "CLIENTE")).scalar_one()

        for data in CLIENTES:
            existing = db.execute(select(Cliente).where(Cliente.correo ==data["correo"])).scalar_one_or_none()

            if existing:
                print(f"✓ Cliente ya existe: "
                    f"{data['correo']}")
                continue
            # ======================================
            # CREAR CLIENTE
            # ======================================

            cliente = Cliente(
                nombres=data["nombres"],
                apellidos=data["apellidos"],
                correo=data["correo"],
                telefono=data["telefono"],
                activo=True,
                usuarioId=None)

            db.add(cliente)
            db.flush()

            # ======================================
            # CREAR USUARIO
            # ======================================

            usuario = Usuario(passwordHash=authService.hashPassword(data["password"]),
                              personaId=cliente.id,
                              rolId=rolCliente.id)

            db.add(usuario)
            db.flush()

            # ======================================
            # ASOCIAR USUARIO
            # ======================================

            cliente.usuarioId = usuario.id

            # ======================================
            # COMMIT FINAL
            # ======================================

            db.commit()
            print(f"✓ Cliente creado: "
                f"{cliente.nombres} "
                f"{cliente.apellidos}")

        print("✓ Seed clientes completado.")

    except Exception as e:
        db.rollback()
        print(f"✗ Error seed clientes: {e}")
        raise

    finally:
        db.close()

if __name__ == "__main__":
    run()