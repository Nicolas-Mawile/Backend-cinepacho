"""Admin empleado endpoints."""

from fastapi import (APIRouter, Depends, HTTPException, Query)
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import (get_current_admin_general)
from app.api.schemas.empleado import (EmpleadoCrearRequest, EmpleadoDetalle, EmpleadoListElement)
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.domain.services.empleado_service import (EmpleadoService)

router = APIRouter(prefix="/admin/empleados", tags=["Admin - Empleados"])

def get_repository(db: Session = Depends(get_db)):
    return EmpleadoRepository(db)

@router.post("/", response_model=EmpleadoDetalle, status_code=201)
def crear_empleado(datos: EmpleadoCrearRequest, repo: EmpleadoRepository = Depends(get_repository), _: dict = Depends(get_current_admin_general)):

    service = EmpleadoService(repo.db)
    try:
        empleado = service.crearEmpleado(repo,datos.model_dump())
        return empleado

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/",response_model=list[EmpleadoListElement])
def listar_empleados(pagina: int = Query(1, ge=1), limite: int = Query(10, ge=1, le=100), repo: EmpleadoRepository = Depends(get_repository), 
                     _: dict = Depends(get_current_admin_general)):

    empleados = repo.listar(pagina=pagina, limite=limite)
    return empleados

@router.get("/{id}",response_model=EmpleadoDetalle)
def obtener_empleado(id: int, repo: EmpleadoRepository = Depends(get_repository), _: dict = Depends(get_current_admin_general)):

    empleado = repo.buscar_por_id(id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@router.patch("/{id}/deshabilitar")
def deshabilitar_empleado(id: int, repo: EmpleadoRepository = Depends(get_repository),_: dict = Depends(get_current_admin_general)):

    empleado = repo.buscar_por_id(id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    repo.desactivar(id)
    return {"message": "Empleado deshabilitado correctamente"}