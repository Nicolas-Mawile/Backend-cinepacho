"""Empleado endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.api.schemas.empleado import (
    EmpleadoCreate, EmpleadoUpdate, EmpleadoResponse, 
    EmpleadoDetalle, EmpleadoPaginated
)
from app.infrastructure.repositories.empleado_repository import EmpleadoRepository
from app.domain.services.empleado_service import EmpleadoService
from app.database import get_db

router = APIRouter(prefix="/empleados", tags=["Empleados"])

def get_empleado_repository(db: Session = Depends(get_db)):
    return EmpleadoRepository(db)

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_empleado(
    datos: EmpleadoCreate,
    repo: EmpleadoRepository = Depends(get_empleado_repository),
    service: EmpleadoService = Depends()
):
    """Crea un nuevo empleado."""
    # Verificar cédula única
    if repo.buscar_por_cedula(datos.cedula_ciudadania):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La cédula ya está registrada"
        )
    
    nuevo_empleado = service.crear_empleado(repo, datos.model_dump())
    
    return {
        "message": "Empleado creado correctamente",
        "empleado": {
            "id": nuevo_empleado.id,
            "nombre": nuevo_empleado.nombre_completo,
            "email": nuevo_empleado.email,
            "cargo": nuevo_empleado.cargo,
            "multiplex_id": nuevo_empleado.multiplex_id,
            "estado": "activo" if nuevo_empleado.activo else "inactivo",
            "created_at": nuevo_empleado.created_at
        }
    }

@router.get("", response_model=EmpleadoPaginated)
def listar_empleados(
    page: int = Query(1, ge=1),
    limit: int = Query(8, ge=1),
    multiplex_id: Optional[int] = None,
    repo: EmpleadoRepository = Depends(get_empleado_repository)
):
    """Lista empleados con paginación y filtro."""
    skip = (page - 1) * limit
    total = repo.count(multiplex_id=multiplex_id)
    empleados = repo.get_all(skip=skip, limit=limit, multiplex_id=multiplex_id)
    
    # Mapear a formato de lista del contrato
    data = []
    for emp in empleados:
        data.append({
            "id": emp.id,
            "primer_nombre": emp.nombre,
            "primer_apellido": emp.apellido,
            "cargo": emp.cargo,
            "multiplex_id": emp.multiplex_id
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if total > 0 else 0,
        "data": data
    }

@router.get("/{empleado_id}", response_model=dict)
def obtener_empleado(
    empleado_id: int,
    repo: EmpleadoRepository = Depends(get_empleado_repository)
):
    """Obtiene el detalle de un empleado."""
    emp = repo.get(empleado_id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empleado no encontrado"
        )
    
    return {
        "id": emp.id,
        "primer_nombre": emp.nombre,
        "segundo_nombre": None, # No almacenado explícitamente pero requerido por contrato
        "primer_apellido": emp.apellido,
        "segundo_apellido": None,
        "cedula_ciudadania": emp.cedula,
        "fecha_nacimiento": emp.fecha_inicio_contrato, # Fallback
        "telefono": emp.telefono,
        "email": emp.email,
        "cargo": emp.cargo,
        "salario": emp.salario,
        "multiplex_id": emp.multiplex_id,
        "correo_laboral": emp.correo_laboral,
        "estado": "activo" if emp.activo else "inactivo",
        "created_at": emp.created_at
    }

@router.put("/{empleado_id}", response_model=dict)
def actualizar_empleado(
    empleado_id: int,
    datos: EmpleadoUpdate,
    repo: EmpleadoRepository = Depends(get_empleado_repository)
):
    """Actualiza los datos laborales de un empleado."""
    emp = repo.update(empleado_id, datos.model_dump(exclude_unset=True))
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empleado no encontrado"
        )
    
    return {
        "message": "Empleado actualizado correctamente",
        "empleado": {
            "id": emp.id,
            "primer_nombre": emp.nombre,
            "primer_apellido": emp.apellido,
            "email": emp.email,
            "cargo": emp.cargo,
            "salario": emp.salario,
            "multiplex_id": emp.multiplex_id,
            "updated_at": emp.updated_at
        }
    }

@router.delete("/{empleado_id}")
def eliminar_empleado(
    empleado_id: int,
    repo: EmpleadoRepository = Depends(get_empleado_repository)
):
    """Deshabilita un empleado."""
    if not repo.delete(empleado_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empleado no encontrado"
        )
    return {"message": "ok"}
