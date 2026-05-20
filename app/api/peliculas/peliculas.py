"""Endpoints de gestión de películas."""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.api.dependencies import (
    requirePermission
)

from app.domain.services.pelicula_service import (
    PeliculaService
)

from app.api.schemas.pelicula import (

    PeliculaCreate,

    PeliculaUpdate,

    PeliculaResponse, CambiarEstadoPeliculaRequest, CambiarEstadoPeliculaResponse
)


router = APIRouter(

    prefix="/peliculas",

    tags=["Películas"]
)


# =========================================================
# DEPENDENCY
# =========================================================

def get_pelicula_service(
    db: Session = Depends(get_db)
):

    return PeliculaService(db)


# =========================================================
# LISTAR
# =========================================================

@router.get(
    "",
    response_model=list[PeliculaResponse]
)
def listar_peliculas(

    service: PeliculaService = Depends(
        get_pelicula_service
    )
):

    try:

        return (
            service.listar_peliculas()
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# OBTENER
# =========================================================

@router.get(
    "/{pelicula_id}",
    response_model=PeliculaResponse
)
def obtener_pelicula(

    pelicula_id: int,

    service: PeliculaService = Depends(
        get_pelicula_service
    )
):

    try:

        return (
            service.obtener_pelicula(
                pelicula_id
            )
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# CREAR
# =========================================================

@router.post(
    "",
    status_code=201,
    response_model=PeliculaResponse
)
def crear_pelicula(

    data: PeliculaCreate,

    service: PeliculaService = Depends(
        get_pelicula_service
    ),

    _ = Depends(
        requirePermission(
            "crear-pelicula"
        )
    )
):

    try:

        return (
            service.crear_pelicula(
                data
            )
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# ACTUALIZAR
# =========================================================

@router.put(
    "/{pelicula_id}",
    response_model=PeliculaResponse
)
def actualizar_pelicula(

    pelicula_id: int,

    data: PeliculaUpdate,

    service: PeliculaService = Depends(
        get_pelicula_service
    ),

    _ = Depends(
        requirePermission(
            "actualizar-pelicula"
        )
    )
):

    try:

        return (
            service.actualizar_pelicula(
                pelicula_id,
                data
            )
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# CAMBIAR ESTADO
# =========================================================

@router.patch(
    "/{pelicula_id}/estado", response_model=CambiarEstadoPeliculaResponse
)
def cambiar_estado_pelicula(

    pelicula_id: int,

    data: CambiarEstadoPeliculaRequest,

    service: PeliculaService = Depends(
        get_pelicula_service
    ),

    _ = Depends(
        requirePermission(
            "cambiar-estado-pelicula"
        )
    )
):

    try:

        return (
            service.cambiar_estado_pelicula(
                pelicula_id,
                data.estaActiva
            )
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )