from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.rol import Rol
from app.infrastructure.models.permiso import (Permiso)

ROLE_PERMISSIONS = {
    # =====================================================
    # CLIENTE
    # =====================================================
    "CLIENTE": [
        "ver-cartelera-general",
        "ver-listado-multiplex",
        "ver-detalle-multiplex",
        "ver-catalogo-comidas",
        "ver-detalle-snack",
        "ver-detalle-pelicula",
        "ver-listado-funciones",
        "ver-detalle-funcion",
        "ver-sala-funcion-multiplex",
        "compra-boletas",
        "compra-snacks",
        "pagar-orden",
        "ver-listado-resenias-propias",
        "calificar"
    ],

    # =====================================================
    # EMPLEADO OTRO
    # =====================================================
    "EMPLEADO-OTRO": [
        "ver-hoja-vida"
    ],

    # =====================================================
    # EMPLEADO CAJERO
    # =====================================================
    "EMPLEADO-CAJERO": [
        "ver-cartelera-general",
        "ver-listado-multiplex",
        "ver-detalle-multiplex",
        "ver-catalogo-comidas",
        "ver-detalle-snack",
        "ver-detalle-pelicula",
        "ver-listado-funciones",
        "ver-detalle-funcion",
        "ver-sala-funcion-multiplex",
        "compra-boletas",
        "compra-snacks",
        "pagar-orden",
        "ver-hoja-vida"
    ],

    # =====================================================
    # ADMIN MULTIPLEX
    # =====================================================
    "ADMIN-MULTIPLEX": [
        "crear-funcion",
        "actualizar-funcion",
        "ver-listado-funciones-multiplex",
        "ver-detalle-funcion",
        "ver-listado-empleados",
        "ver-detalle-empleado",
        "ver-hoja-vida"
    ],

    # =====================================================
    # ADMIN GENERAL
    # =====================================================
    "ADMIN-GENERAL": [
        # EMPLEADOS
        "crear-empleado",
        "actualizar-empleado",
        "deshabilitar-empleado",
        "ver-listado-empleados",
        "ver-detalle-empleado",
        "ver-hoja-vida",
        # CLIENTES
        "ver-listado-clientes",
        "ver-detalle-cliente",
        "deshabilitar-cliente",
        # MULTIPLEX
        "crear-multiplex",
        "actualizar-multiplex",
        "deshabilitar-multiplex",
        "ver-listado-multiplex",
        "ver-detalle-multiplex",
        # SALAS
        "crear-sala",
        "actualizar-sala",
        "deshabilitar-sala",
        "ver-listado-salas",
        "ver-detalle-sala",
        # PELÍCULAS
        "crear-pelicula",
        "actualizar-pelicula",
        "deshabilitar-pelicula",
        "habilitar-pelicula",
        "ver-listado-peliculas",
        "ver-detalle-pelicula",
        # SNACKS
        "crear-snack",
        "actualizar-snack",
        "deshabilitar-snack",
        "ver-listado-snacks",
        "ver-detalle-snack",
        # FUNCIONES
        "crear-funcion",
        "actualizar-funcion",
        "deshabilitar-funcion",
        "ver-listado-funciones-multiplex",
        "ver-detalle-funcion",
        # REPORTES
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