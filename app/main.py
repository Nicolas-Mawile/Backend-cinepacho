"""FastAPI application entry point."""

import sys

from fastapi import FastAPI
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db, engine
from .api.router import router

sys.path.insert(0, str(Path(__file__).parent.parent))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja eventos de startup y shutdown de la aplicación.
    """
    # Startup
    print("Inicializando Cinepacho Backend...")
    init_db()
    print("Base de datos inicializada")
    
    # Ejecutar seeds
    from seeds.multiplex import run as seed_multiplex
    from seeds.configuracion import run as seed_config
    seed_multiplex()
    seed_config()
    
    yield
    
    # Shutdown
    print("Cerrando conexiones...")
    engine.dispose()
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
def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.get("/")
def root():
    return {
        "message": "Bienvenido a Cinepacho Backend",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }