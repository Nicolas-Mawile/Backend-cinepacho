"""Admin empleado endpoints."""

from fastapi import (APIRouter, Depends, HTTPException, Query)
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import (requirePermission)
from app.api.schemas.empleado import (CambiarEstadoEmpleadoRequest, EmpleadoCrearRequest, EmpleadoDetalle, EmpleadoListElement)
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.domain.services.empleado_service import (EmpleadoService)
from app.infrastructure.models.usuario import Usuario

router = APIRouter(prefix="/admin/empleados", tags=["Admin - Empleados"])

def get_repository(db: Session = Depends(get_db)):
    return EmpleadoRepository(db)

@router.post("/", response_model=EmpleadoDetalle, status_code=201)
def crear_empleado(datos: EmpleadoCrearRequest, repo: EmpleadoRepository = Depends(get_repository), _: Usuario = Depends(requirePermission("crear-empleado"))):

    service = EmpleadoService(repo.db)
    try:
        empleado = service.crearEmpleado(repo,datos.model_dump())
        return empleado

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/",response_model=list[EmpleadoListElement])
def listar_empleados(pagina: int = Query(1, ge=1), limite: int = Query(10, ge=1, le=100), repo: EmpleadoRepository = Depends(get_repository), 
                     _: Usuario = Depends(requirePermission("ver-listado-empleados"))):

    empleados = repo.listar(pagina=pagina, limite=limite)
    response = []

    for empleado in empleados:
        response.append({
            "id": empleado.id,
            "nombres": empleado.nombres,
            "apellidos": empleado.apellidos,
            "cargoActual": empleado.cargoActual,
            "multiplexActual": empleado.multiplexActual,
        })

    return response

@router.get("/{id}",response_model=EmpleadoDetalle)
def obtener_empleado(id: int, repo: EmpleadoRepository = Depends(get_repository), _: Usuario = Depends(requirePermission("ver-detalle-empleado"))):

    empleado = repo.buscar_por_id(id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@router.patch("/{id}/estado", summary="Cambiar estado de un empleado", 
              responses={200: {"description": "Estado actualizado correctamente"}, 404: {"description": "Empleado no encontrado"}})
def cambiar_estado_empleado(id: int, activo: bool, repo: EmpleadoRepository = Depends(get_repository), _: Usuario = Depends(requirePermission("cambiar-estado-empleado"))):
    empleado = repo.cambiarEstado(id, activo)

    if not empleado:
        raise HTTPException(status_code=404,detail="Empleado no encontrado")

    return {"message": ("Empleado activado correctamente" if empleado.activo else "Empleado deshabilitado correctamente"),
        "empleado": {
            "id": empleado.id,
            "nombres": empleado.nombres,
            "apellidos": empleado.apellidos,
            "activo": empleado.activo
        }
    }