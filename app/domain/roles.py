"""Definición de roles y permisos del sistema."""

PERMISOS = {
    "CLIENTE": [
        "ver-cartelera-general",
        "ver-cartelera-multiplex",
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
    ],
    "EMPLEADO-OTRO": [
        "ver-hoja-vida",
    ],
    "EMPLEADO-CAJERO": [
        "ver-cartelera-general",
        "ver-cartelera-multiplex",
        "ver-multiplex-particular",
        "ver-catalogo-comidas",
        "ver-detalle-pelicula",
        "ver-listado-funciones",
        "ver-listado-funciones-multiplex",
        "ver-detalle-funcion",
        "ver-sala-funcion-multiplex",
        "compra-boletas",
        "compra-snacks",
        "pagar-orden",
        "ver-hoja-vida",
    ],
    "ADMIN-MULTIPLEX": [
        "crear-funcion",
        "actualizar-funcion",
        "cambiar-estado-funcion",
        "ver-listado-funciones-multiplex",
        "ver-detalle-funcion",
        "ver-cartelera-multiplex",
        "administrar-cartelera-multiplex",
        "ver-listado-empleados",
        "ver-hoja-vida",
    ],
    "ADMIN-GENERAL": [
        "crear-multiplex", "actualizar-multiplex", "deshabilitar-multiplex", "ver-listado-multiplex",
        "crear-sala", "deshabilitar-sala", "actualizar-sala", "ver-listado-salas",
        "crear-empleado", "actualizar-empleado", "ver-listado-empleados", "deshabilitar-empleados",
        "ver-hoja-vida",
        "crear-pelicula", "actualizar-pelicula", "deshabilitar-pelicula", "habilitar-pelicula", "ver-listado-peliculas",
        "ver-cartelera-general", "ver-cartelera-multiplex", "administrar-cartelera-general", "administrar-cartelera-multiplex",
        "ver-listado-funciones", "ver-listado-funciones-multiplex", "ver-detalle-funcion", "crear-funcion", "actualizar-funcion", "cambiar-estado-funcion",
        "crear-snack", "actualizar-snack", "deshabilitar-snack", "ver-listado-snacks",
        "ver-reportes",
    ],
}

def get_permisos(rol: str) -> list[str]:
    return PERMISOS.get(rol, [])