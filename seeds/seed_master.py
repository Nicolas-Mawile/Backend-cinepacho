"""
Seed maestro del sistema.
Ejecuta todos los seeds
en el orden correcto.
"""

from seeds.permisos_seed import run as permisos_seed
from seeds.roles_seed import run as roles_seed
from seeds.roles_permisos_seed import run as roles_permisos_seed

from seeds.tipo_silla_seed import run as tipo_silla_seed

from seeds.multiplex_seed import run as multiplex_seed
from seeds.pelicula_seed import run as pelicula_seed
from seeds.funcion_seed import run as funcion_seed

from seeds.clientes_seed import run as clientes_seed
from seeds.empleados_seed import run as empleados_seed
from seeds.admin_seed import run as admin_seed


def run():

    print("\n========== INICIANDO SEEDS ==========\n")

    print("→ permisos")
    permisos_seed()

    print("→ roles")
    roles_seed()

    print("→ roles_permisos")
    roles_permisos_seed()

    print("→ tipo_silla")
    tipo_silla_seed()

    print("→ multiplex")
    multiplex_seed()

    print("→ peliculas")
    pelicula_seed()

    print("→ funciones")
    funcion_seed()

    print("→ clientes")
    clientes_seed()

    print("→ empleados")
    empleados_seed()

    print("→ admin")
    admin_seed()

    print("\n========== SEEDS COMPLETADOS ==========\n")


if __name__ == "__main__":
    run()