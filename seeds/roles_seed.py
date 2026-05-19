from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.rol import Rol

ROLES = [
    "CLIENTE",
    "EMPLEADO-CAJERO",
    "EMPLEADO-OTRO",
    "ADMIN-MULTIPLEX",
    "ADMIN-GENERAL"
]

def run():
    db = SessionLocal()
    try:
        for roleName in ROLES:
            stmt = select(Rol).where(Rol.nombre == roleName)
            exists = (db.execute(stmt).scalar_one_or_none())
            if exists:
                print(f"✓ Rol ya existe: {roleName}")
                continue
            rol = Rol(nombre=roleName)
            db.add(rol)
            print(f"✓ Rol creado: {roleName}")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run()