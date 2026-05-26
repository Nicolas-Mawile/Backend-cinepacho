"""
Ejecuta todas las seeds en orden.

Uso:
    cd cinepachobackend
    python -m seeds.run_all
"""

import sys
import traceback

from seeds import (
    roles_seed,
    permisos_seed,
    roles_permisos_seed,
    tipo_silla_seed,
    multiplex_seed,
    salas,
    admin_seed,
    empleados_seed,
    clientes_seed,
    peliculas_seed,
    multiplex_cartelera_seed,
    funciones_seed,
    comidas_seed,
    servicios_seed,
    compra_seed,
    configuracion,
)

SEEDS = [
    # ── Roles y permisos ──────────────────────────────
    ("roles",               roles_seed),
    ("permisos",            permisos_seed),
    ("roles_permisos",      roles_permisos_seed),
    # ── Infraestructura ──────────────────────────────
    ("tipo_silla",          tipo_silla_seed),           # tipos de silla antes del multiplex
    ("multiplex",           multiplex_seed),            # crea multiplex + salas + sillas
    ("salas",               salas),                     # requiere multiplex + tipo_silla
    # ── Usuarios ─────────────────────────────────────
    ("admin",               admin_seed),
    ("empleados",           empleados_seed),
    ("clientes",            clientes_seed),
    # ── Contenido ────────────────────────────────────
    ("peliculas",           peliculas_seed),
    ("cartelera",           multiplex_cartelera_seed),  # requiere multiplex + peliculas
    ("funciones",           funciones_seed),            # requiere cartelera + salas
    # ── Productos y servicios ─────────────────────────
    ("comidas",             comidas_seed),
    ("servicios",           servicios_seed),
    # ── Transacciones ────────────────────────────────
    ("compras",             compra_seed),               # requiere clientes + funciones + comidas
    # ── Configuración ────────────────────────────────
    ("configuracion",       configuracion),
]


def main():
    print("=" * 50)
    print("  Iniciando seeds")
    print("=" * 50)

    ok = []
    failed = []

    for name, module in SEEDS:
        print(f"\n[{name}]")
        try:
            module.run()
            ok.append(name)
        except Exception as e:
            print(f"✗ Falló: {e}")
            traceback.print_exc()
            failed.append(name)

    print("\n" + "=" * 50)
    print(f"  Completadas: {len(ok)}/{len(SEEDS)}")
    if failed:
        print(f"  Fallidas:    {', '.join(failed)}")
        print("=" * 50)
        sys.exit(1)
    else:
        print("  Todas las seeds ejecutadas correctamente.")
        print("=" * 50)


if __name__ == "__main__":
    main()
