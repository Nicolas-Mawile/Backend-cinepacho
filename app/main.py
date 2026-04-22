"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db, engine
from .api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja eventos de startup y shutdown de la aplicación.
    """
    # Startup
    print("Inicializando Cinepacho Backend...")
    await init_db()
    print("Base de datos inicializada")
    
    # Ejecutar seeds
    from seeds.multiplex import run as seed_multiplex
    from seeds.configuracion import run as seed_config
    await seed_multiplex()
    await seed_config()
    
    yield
    
    # Shutdown
    print("Cerrando conexiones...")
    await engine.dispose()
    print("Aplicación cerrada")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend para sistema de cines Cinepacho",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Endpoint para verificar que el servidor está en línea."""
    return {"status": "ok", "app": settings.app_name}


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": "Bienvenido a Cinepacho Backend",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

