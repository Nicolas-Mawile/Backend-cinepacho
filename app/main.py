"""FastAPI application entry point."""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.auth import router as auth_router
from app.api.router import router

sys.path.insert(0, str(Path(__file__).parent.parent))

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando Cinepacho Backend...")
    try:
        from seeds.multiplex import run as seed_multiplex
        from seeds.configuracion import run as seed_config
        seed_multiplex()
        seed_config()
    except Exception:
        pass
    yield
    print("Cerrando conexiones...")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend para sistema de cines Cinepacho",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
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