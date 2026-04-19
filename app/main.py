"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(title="Cinepacho Backend")


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    pass
