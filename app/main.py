"""FastAPI application entry point."""
import sys
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, engine
from app.api.router import router

sys.path.insert(0, str(Path(__file__).parent.parent))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja eventos de startup y shutdown de la aplicación."""
    # Startup
    print("Inicializando Cinepacho Backend...")
    init_db()
    print("Base de datos inicializada")
    
    # Ejecutar seeds (con try-except para evitar fallos en tests)
    try:
        from seeds.multiplex import run as seed_multiplex
        from seeds.configuracion import run as seed_config
        seed_multiplex()
        seed_config()
    except Exception as e:
        print(f"Error al ejecutar seeds: {e}")
    
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
corsOrigins = []
try:
    corsOrigins = json.loads(settings.cors_origins)
except (json.JSONDecodeError, TypeError):
    corsOrigins = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=corsOrigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def healthCheck():
    """Endpoint de verificación del estado del servicio."""
    return {"status": "ok", "app": settings.app_name}

@app.get("/")
def root():
    """Entrada principal de la API con enlaces a documentación."""
    return {
        "message": "Bienvenido a Cinepacho Backend",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }
