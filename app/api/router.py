"""Central API router registration."""
from fastapi import APIRouter
from app.api.multiplex.multiplex import router as multiplex_router
from app.api.salas import router as salas_router
from app.api.peliculas import router as peliculas_router
from app.api.funciones import router as funciones_router
from app.api.cartelera import router as cartelera_router
from app.api.auth.auth import router as auth_router
from app.api.empleados.empleados import router as empleados_router

router = APIRouter()

router.include_router(multiplex_router)
router.include_router(salas_router)
router.include_router(peliculas_router)
router.include_router(funciones_router)
router.include_router(cartelera_router)
router.include_router(auth_router)
router.include_router(empleados_router)