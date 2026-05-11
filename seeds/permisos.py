from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.permiso import Permiso

PERMISOS = [
    "crear-empleado",
    "editar-empleado",
    "deshabilitar-empleado",
    "crear-multiplex",
    "editar-multiplex",
    "crear-sala",
    "editar-sala",
    "crear-funcion",
    "editar-funcion"
]


def run():
    db = SessionLocal()
    try:
        for permisoName in PERMISOS:
            stmt = select(Permiso).where(Permiso.nombre == permisoName)
            exists = (db.execute(stmt).scalar_one_or_none())

            if exists:
                continue

            permiso = Permiso(nombre=permisoName)
            db.add(permiso)
        db.commit()
    finally:
        db.close()