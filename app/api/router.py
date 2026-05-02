"""Central API router registration."""

from fastapi import APIRouter

# Importar routers directamente (NO módulos completos)
from app.api.v1.multiplex.multiplex import router as multiplex_router
# from app.api.v1.peliculas import router as peliculas_router
# from app.api.v1.salas import router as salas_router
# from app.api.v1.sillas import router as sillas_router
# from app.api.v1.funciones import router as funciones_router
# from app.api.v1.clientes import router as clientes_router
# from app.api.v1.empleados import router as empleados_router
# from app.api.v1.evaluaciones import router as evaluaciones_router
# from app.api.v1.auth import router as auth_router
# from app.api.v1.comidas import router as comidas_router
# from app.api.v1.compra import router as compra_router
# from app.api.v1.reportes import router as reportes_router

# Router principal
router = APIRouter()

# Registrar routers (SIN repetir prefix)
# router.include_router(auth_router)
# router.include_router(clientes_router)
# router.include_router(empleados_router)
router.include_router(multiplex_router)
# router.include_router(salas_router)
# router.include_router(sillas_router)
# router.include_router(funciones_router)
# router.include_router(peliculas_router)
# router.include_router(evaluaciones_router)
# router.include_router(comidas_router)
# router.include_router(compra_router)
# router.include_router(reportes_router)