"""Endpoints de gestion de peliculas."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.infrastructure.models.pelicula import Pelicula
from app.api.dependencies import requireRole
from app.api.schemas.pelicula import PeliculaCreate, PeliculaUpdate

router = APIRouter(prefix="/peliculas", tags=["peliculas"])


@router.get("")
def listar_peliculas(db: Session = Depends(get_db)):
    return db.execute(select(Pelicula)).scalars().all()


@router.get("/{id}")
def obtener_pelicula(id: int, db: Session = Depends(get_db)):
    pelicula = db.get(Pelicula, id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Pelicula no encontrada")
    return pelicula


@router.post("", status_code=201)
def crear_pelicula(data: PeliculaCreate, db: Session = Depends(get_db), _=Depends(requireRole(["ADMIN-GENERAL"]))):
    pelicula = Pelicula(**data.model_dump(), estaActiva=True)
    db.add(pelicula)
    db.commit()
    db.refresh(pelicula)
    return pelicula


@router.put("/{id}")
def actualizar_pelicula(id: int, data: PeliculaUpdate, db: Session = Depends(get_db), _=Depends(requireRole(["ADMIN-GENERAL"]))):
    pelicula = db.get(Pelicula, id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Pelicula no encontrada")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(pelicula, key, value)
    db.commit()
    db.refresh(pelicula)
    return pelicula


@router.patch("/{id}/desactivar")
def desactivar_pelicula(id: int, db: Session = Depends(get_db), _=Depends(requireRole(["ADMIN-GENERAL"]))):
    pelicula = db.get(Pelicula, id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Pelicula no encontrada")
    if not pelicula.estaActiva:
        raise HTTPException(status_code=400, detail="La pelicula ya esta desactivada")
    pelicula.estaActiva = False
    db.commit()
    return {"mensaje": "Pelicula desactivada correctamente"}
