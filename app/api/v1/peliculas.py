"""Endpoints de gestión de películas."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from app.database import get_db
from app.infrastructure.models.pelicula import Pelicula
from app.api.dependencies import requireRole

router = APIRouter(prefix="/peliculas", tags=["peliculas"])


class PeliculaCreate(BaseModel):
    titulo: str
    duracionMinutos: int
    linkTrailer: Optional[str] = None
    linkPoster: Optional[str] = None
    sinopsis: Optional[str] = None


class PeliculaUpdate(BaseModel):
    titulo: Optional[str] = None
    duracionMinutos: Optional[int] = None
    linkTrailer: Optional[str] = None
    linkPoster: Optional[str] = None
    sinopsis: Optional[str] = None


@router.get("")
def listar_peliculas(db: Session = Depends(get_db)):
    result = db.execute(select(Pelicula))
    return result.scalars().all()


@router.get("/{id}")
def obtener_pelicula(id: int, db: Session = Depends(get_db)):
    pelicula = db.get(Pelicula, id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return pelicula


@router.post("", status_code=201)
def crear_pelicula(
    data: PeliculaCreate,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-GENERAL"]))
):
    pelicula = Pelicula(**data.model_dump(), estaActiva=True)
    db.add(pelicula)
    db.commit()
    db.refresh(pelicula)
    return pelicula


@router.put("/{id}")
def actualizar_pelicula(
    id: int,
    data: PeliculaUpdate,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-GENERAL"]))
):
    pelicula = db.get(Pelicula, id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(pelicula, key, value)
    db.commit()
    db.refresh(pelicula)
    return pelicula


@router.patch("/{id}/desactivar")
def desactivar_pelicula(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(requireRole(["ADMIN-GENERAL"]))
):
    pelicula = db.get(Pelicula, id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    if not pelicula.estaActiva:
        raise HTTPException(status_code=400, detail="La película ya está desactivada")
    pelicula.estaActiva = False
    db.commit()
    return {"mensaje": "Película desactivada correctamente"}
