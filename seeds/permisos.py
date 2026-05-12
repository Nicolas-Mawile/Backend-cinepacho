from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.permiso import Permiso

PERMISOS = [

    # =========================================================
    # CLIENTE
    # =========================================================
    "ver-cartelera-general",
    "ver-listado-multiplex",
    "ver-catalogo-comidas",
    "ver-detalle-pelicula",
    "ver-listado-funciones",
    "ver-sala-funcion-multiplex",
    "compra-boletas",
    "compra-snacks",
    "pagar-orden",
    "ver-listado-resenias-propias",
    "calificar",

    # =========================================================
    # EMPLEADO
    # =========================================================
    "ver-hoja-vida",
    "ver-cartelera-multiplex",
    "ver-multiplex-particular",
    "ver-listado-funciones-multiplex",

    # =========================================================
    # ADMIN MULTIPLEX
    # =========================================================
    "crear-funcion",
    "actualizar-funcion",

    # =========================================================
    # EMPLEADOS
    # =========================================================
    "crear-empleado",
    "actualizar-empleado",
    "ver-listado-empleados",
    "deshabilitar-empleados",

    # =========================================================
    # MULTIPLEX
    # =========================================================
    "crear-multiplex",
    "actualizar-multiplex",
    "deshabilitar-multiplex",

    # =========================================================
    # SALAS
    # =========================================================
    "crear-sala",
    "deshabilitar-sala",
    "actualizar-sala",
    "ver-listado-salas",

    # =========================================================
    # PELICULAS
    # =========================================================
    "crear-pelicula",
    "actualizar-pelicula",
    "deshabilitar-pelicula",
    "habilitar-pelicula",
    "ver-listado-peliculas",

    # =========================================================
    # SNACKS
    # =========================================================
    "crear-snack",
    "actualizar-snack",
    "deshabilitar-snack",
    "ver-listado-snacks",

    # =========================================================
    # REPORTES
    # =========================================================
    "ver-reportes"
]


def run():
    db = SessionLocal()
    try:
        for permisoName in PERMISOS:
            exists = db.execute(select(Permiso).where(Permiso.nombre == permisoName)).scalar_one_or_none()
            
            if exists:
                print(f"Permiso ya existe: {permisoName}")
                continue

            permiso = Permiso(nombre=permisoName)
            db.add(permiso)
            print(f"Permiso creado: {permisoName}")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run()