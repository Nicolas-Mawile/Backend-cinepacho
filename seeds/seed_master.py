"""
Seed maestro del sistema.
Ejecuta todos los seeds en el orden correcto.
"""
from seeds.permisos_seed import run as permisos_seed
from seeds.roles_seed import run as roles_seed
from seeds.roles_permisos_seed import run as roles_permisos_seed
from seeds.tipo_silla_seed import run as tipo_silla_seed
from seeds.multiplex_seed import run as multiplex_seed
from seeds.salas import run as salas_seed               # ← AGREGADO
from seeds.peliculas_seed import run as pelicula_seed
from seeds.multiplex_cartelera_seed import run as multiplex_cartelera_seed  # ← AGREGADO
from seeds.funciones_seed import run as funcion_seed
from seeds.comidas_seed import run as comidas_seed      # ← AGREGADO
from seeds.clientes_seed import run as clientes_seed
from seeds.empleados_seed import run as empleados_seed
from seeds.admin_seed import run as admin_seed
from seeds.servicios_seed import run as servicios_seed
from seeds.evaluacion_seed import run as evaluacion_seed


def run():
    permisos_seed()
    roles_seed()
    roles_permisos_seed()
    tipo_silla_seed()
    multiplex_seed()
    salas_seed()
    pelicula_seed()
    multiplex_cartelera_seed()
    funcion_seed()
    comidas_seed()
    clientes_seed()
    empleados_seed()
    admin_seed()
    servicios_seed()
    evaluacion_seed()

if __name__ == "__main__":
    run()
