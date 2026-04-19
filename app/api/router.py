"""Central API router registration."""

from fastapi import APIRouter

from .v1 import auth, cartelera, reservas, pagos, snacks, puntos, evaluaciones, clientes
from .v1.admin import multiplex, empleados, funciones, precios, reportes, configuracion

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(cartelera.router, prefix="/cartelera", tags=["cartelera"])
router.include_router(reservas.router, prefix="/reservas", tags=["reservas"])
router.include_router(pagos.router, prefix="/pagos", tags=["pagos"])
router.include_router(snacks.router, prefix="/snacks", tags=["snacks"])
router.include_router(puntos.router, prefix="/puntos", tags=["puntos"])
router.include_router(evaluaciones.router, prefix="/evaluaciones", tags=["evaluaciones"])
router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])

admin_router = APIRouter(prefix="/admin", tags=["admin"])
admin_router.include_router(multiplex.router, prefix="/multiplex")
admin_router.include_router(empleados.router, prefix="/empleados")
admin_router.include_router(funciones.router, prefix="/funciones")
admin_router.include_router(precios.router, prefix="/precios")
admin_router.include_router(reportes.router, prefix="/reportes")
admin_router.include_router(configuracion.router, prefix="/configuracion")

router.include_router(admin_router)
