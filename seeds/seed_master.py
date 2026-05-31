"""
Seed maestro del sistema.
Ejecuta todos los seeds en el orden correcto.
"""
from seeds.permisos_seed import run as permisos_seed
from seeds.roles_seed import run as roles_seed
from seeds.roles_permisos_seed import run as roles_permisos_seed
from seeds.tipo_silla_seed import run as tipo_silla_seed
from seeds.multiplex_seed import run as multiplex_seed
from seeds.salas import run as salas_seed
from seeds.peliculas_seed import run as pelicula_seed
from seeds.multiplex_cartelera_seed import run as multiplex_cartelera_seed
from seeds.funciones_seed import run as funcion_seed
from seeds.comidas_seed import run as comidas_seed
from seeds.clientes_seed import run as clientes_seed
from seeds.empleados_seed import run as empleados_seed
from seeds.admin_seed import run as admin_seed
from seeds.servicios_seed import run as servicios_seed
from seeds.evaluacion_seed import run as evaluacion_seed
from seeds.compra_seed import run as compra_seed
from seeds.reporte_seed import run as reporte_seed


def run():
    seeds = [
        ("permisos",            permisos_seed),
        ("roles",               roles_seed),
        ("roles_permisos",      roles_permisos_seed),
        ("tipo_silla",          tipo_silla_seed),
        ("multiplex",           multiplex_seed),
        ("salas",               salas_seed),
        ("peliculas",           pelicula_seed),
        ("multiplex_cartelera", multiplex_cartelera_seed),
        ("funciones",           funcion_seed),
        ("comidas",             comidas_seed),
        ("clientes",            clientes_seed),
        ("empleados",           empleados_seed),
        ("admin",               admin_seed),
        ("servicios",           servicios_seed),
        ("evaluacion",          evaluacion_seed),
        ("compras",             compra_seed),
        ("reporte",             reporte_seed),
    ]
    for nombre, fn in seeds:
        try:
            fn()
        except Exception as e:
            print(f"⚠️  seed '{nombre}' falló: {e}")

if __name__ == "__main__":
    run()
