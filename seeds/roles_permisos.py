from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.rol import Rol

from app.infrastructure.models.permiso import Permiso


ROLE_PERMISSIONS = {
    # =========================================================
    # CLIENTE
    # =========================================================
    "CLIENTE": [
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
        "calificar"
    ],

    # =========================================================
    # EMPLEADO OTRO
    # =========================================================
    "EMPLEADO-OTRO": [
        "ver-hoja-vida"
    ],

    # =========================================================
    # EMPLEADO CAJERO
    # =========================================================
    "EMPLEADO-CAJERO": [
        "ver-cartelera-multiplex",
        "ver-multiplex-particular",
        "ver-catalogo-comidas",
        "ver-detalle-pelicula",
        "ver-listado-funciones-multiplex",
        "ver-sala-funcion-multiplex",
        "compra-boletas",
        "compra-snacks",
        "pagar-orden",
        "ver-hoja-vida"
    ],

    # =========================================================
    # ADMIN MULTIPLEX
    # =========================================================
    "ADMIN-MULTIPLEX": [
        "crear-funcion",
        "actualizar-funcion",
        "ver-listado-funciones-multiplex",
        "ver-listado-empleados",
        "ver-hoja-vida"
    ],

    # =========================================================
    # ADMIN GENERAL
    # =========================================================

    "ADMIN-GENERAL": [
        "crear-multiplex",
        "actualizar-multiplex",
        "deshabilitar-multiplex",
        "ver-listado-multiplex",
        "crear-sala",
        "deshabilitar-sala",
        "actualizar-sala",
        "ver-listado-salas",
        "crear-empleado",
        "actualizar-empleado",
        "ver-listado-empleados",
        "deshabilitar-empleados",
        "ver-hoja-vida",
        "crear-pelicula",
        "actualizar-pelicula",
        "deshabilitar-pelicula",
        "habilitar-pelicula",
        "ver-listado-peliculas",
        "crear-snack",
        "actualizar-snack",
        "deshabilitar-snack",
        "ver-listado-snacks",
        "ver-reportes"
    ]
}


def run():
    db = SessionLocal()
    try:
        for roleName, permisosNames in ROLE_PERMISSIONS.items():
            rol = db.execute(select(Rol).where(Rol.nombre == roleName)).scalar_one()
            permisos = db.execute(select(Permiso).where(Permiso.nombre.in_(permisosNames))).scalars().all()
            rol.permisos = permisos
            print(f"Permisos asignados a {roleName}")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run()