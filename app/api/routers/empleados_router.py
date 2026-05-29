"""Admin empleado endpoints."""

from fastapi import (APIRouter, Depends, HTTPException, Query)
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import (requirePermission)
from app.api.schemas.empleado import (CambiarEstadoEmpleadoRequest, EmpleadoCrearRequest, EmpleadoDetalle, EmpleadoListElement, CambiarCargoEmpleadoRequest, ActualizarEmpleadoRequest)
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.domain.services.empleado_service import (EmpleadoService)
from app.infrastructure.models.usuario import Usuario

router = APIRouter(prefix="/admin/empleados", tags=["Admin - Empleados"])

def get_repository(db: Session = Depends(get_db)):
    return EmpleadoRepository(db)

@router.post("/", status_code=201)
def crear_empleado(datos: EmpleadoCrearRequest, repo: EmpleadoRepository = Depends(get_repository), _: Usuario = Depends(requirePermission("crear-empleado"))):

    service = EmpleadoService(repo.db)
    try:
        resultado = service.crearEmpleado(repo,datos.model_dump())
        return resultado

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
            "codigoEmpleado" : empleado.codigoEmpleado,
            "cargoActual": empleado.cargoActual,
            "multiplexActual": empleado.multiplexActual,
            "activo": empleado.activo
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

@router.patch("/{id}", summary="Actualizar datos de empleado",
              responses={
                  200: {"description": "Empleado actualizado correctamente"},
                  400: {"description": "Datos inválidos o restricción de 3 meses"},
                  404: {"description": "Empleado no encontrado"},
              })
def actualizar_empleado(
    id: int,
    data: ActualizarEmpleadoRequest,
    repo: EmpleadoRepository = Depends(get_repository),
    usuario: Usuario = Depends(requirePermission("actualizar-empleado")),
):
    service = EmpleadoService(repo.db)
    try:
        return service.actualizarDatosEmpleado(
            empleadoId=id,
            datos=data.model_dump(exclude_none=True),
            usuarioAdministradorId=usuario.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{id}/cargo", summary="Cambiar cargo de empleado")
def cambiar_cargo_empleado(id: int, data: CambiarCargoEmpleadoRequest, repo: EmpleadoRepository = Depends(get_repository),
                           usuario: Usuario = Depends(requirePermission("actualizar-empleado"))):

    service = EmpleadoService(repo.db)
    try:
        return service.cambiarCargoEmpleado(empleadoId=id, cargoNuevo=data.cargoNuevo, salarioNuevo=data.salarioNuevo, 
                                            motivo=data.motivo, usuarioAdministradorId=usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))