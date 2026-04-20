"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Cinepacho Backend", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])