"""Central API router registration."""
from fastapi import APIRouter
from app.api.routers.multiplex_router import router as multiplex_router
from app.api.routers.salas_router import router as salas_router
from app.api.routers.peliculas_router import router as peliculas_router
from app.api.routers.funciones_router import router as funciones_router
from app.api.routers.cartelera_router import router as cartelera_router
from app.api.routers.auth_router import router as auth_router
from app.api.routers.empleados_router import router as empleados_router
from app.api.routers.compras_router import router as compras_router
from app.api.routers.comida_router import router as comidas_router
# Router principal
router = APIRouter()

router.include_router(multiplex_router)
router.include_router(salas_router)
router.include_router(compras_router)
router.include_router(peliculas_router)
router.include_router(funciones_router)
router.include_router(cartelera_router)
router.include_router(auth_router)
router.include_router(empleados_router)
router.include_router(comidas_router)
