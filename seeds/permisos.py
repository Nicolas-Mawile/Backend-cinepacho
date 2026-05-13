from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.permiso import Permiso

PERMISOS = [
    # =====================================================
    # CLIENTE
    # =====================================================
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
    "calificar",

    # =====================================================
    # EMPLEADOS
    # =====================================================
    "crear-empleado",
    "actualizar-empleado",
    "cambiar-estado-empleado",
    "ver-listado-empleados",
    "ver-detalle-empleado",
    "ver-hoja-vida",

    # =====================================================
    # CLIENTES ADMIN
    # =====================================================
    "ver-listado-clientes",
    "ver-detalle-cliente",
    "deshabilitar-cliente",

    # =====================================================
    # MULTIPLEX
    # =====================================================
    "crear-multiplex",
    "actualizar-multiplex",
    "cambiar-estado-multiplex",
    "ver-listado-multiplex",
    "ver-detalle-multiplex",
    "ver-salas-multiplex",

    # =====================================================
    # SALAS
    # =====================================================
    "crear-sala",
    "actualizar-sala",
    "cambiar-estado-sala",
    "ver-listado-salas",
    "ver-detalle-sala",

    # =====================================================
    # PELÍCULAS
    # =====================================================
    "crear-pelicula",
    "actualizar-pelicula",
    "cambiar-estado-pelicula",
    "ver-listado-peliculas",
    "ver-detalle-pelicula",

    # =====================================================
    # SNACKS
    # =====================================================
    "crear-snack",
    "actualizar-snack",
    "cambiar-estado-snack",
    "ver-listado-snacks",
    "ver-detalle-snack",

    # =====================================================
    # FUNCIONES
    # =====================================================
    "crear-funcion",
    "actualizar-funcion",
    "cambiar-estado-funcion",
    "ver-listado-funciones-multiplex",
    "ver-detalle-funcion",

    # =====================================================
    # REPORTES
    # =====================================================
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