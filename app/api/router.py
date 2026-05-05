"""Central API router registration."""

from fastapi import APIRouter

# Importar routers directamente (NO módulos completos)
from app.api.v1.multiplex.multiplex import router as multiplex_router
from app.api.v1.salas import router as salas_router
from app.api.v1.auth.auth import router as auth_router
from app.api.v1.empleados.empleados import router as empleados_router

# Router principal
router = APIRouter()

# Registrar routers (SIN repetir prefix)
router.include_router(auth_router)
router.include_router(empleados_router)
router.include_router(multiplex_router)
router.include_router(salas_router)