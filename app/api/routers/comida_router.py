from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.infrastructure.repositories.comida_repository import (
    ComidaRepository
)

from app.domain.services.comida_service import (
    ComidaService
)

from app.api.schemas.comida import (
    ComidaCreate,
    ComidaUpdate,
    ComidaResponse
)

from app.api.dependencies import (
    requirePermission
)


router = APIRouter(
    prefix="/comidas",
    tags=["Comidas"]
)


# --------------------------------------
# DEPENDENCY
# --------------------------------------


def get_comida_service(
    db: Session = Depends(get_db)
):

    repository = ComidaRepository(db)

    return ComidaService(repository)


# --------------------------------------
# CREATE
# --------------------------------------


@router.post(
    "/",
    response_model=ComidaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            requirePermission(
                "crear-snack"
            )
        )
    ]
)
def create_comida(
    data: ComidaCreate,
    service: ComidaService = Depends(
        get_comida_service
    )
):

    return service.create_comida(data)


# --------------------------------------
# GET ALL
# --------------------------------------


@router.get(
    "/",
    response_model=list[ComidaResponse],
)
def get_all_comidas(
    service: ComidaService = Depends(
        get_comida_service
    )
):

    return service.get_all_comidas()


# --------------------------------------
# GET BY ID
# --------------------------------------


@router.get(
    "/{comida_id}",
    response_model=ComidaResponse,
)
def get_comida_by_id(
    comida_id: int,
    service: ComidaService = Depends(
        get_comida_service
    )
):

    return service.get_comida_by_id(
        comida_id
    )


# --------------------------------------
# UPDATE
# --------------------------------------


@router.patch(
    "/{comida_id}",
    response_model=ComidaResponse,
    dependencies=[
        Depends(
            requirePermission(
                "actualizar-snack"
            )
        )
    ]
)
def update_comida(
    comida_id: int,
    data: ComidaUpdate,
    service: ComidaService = Depends(
        get_comida_service
    )
):

    return service.update_comida(
        comida_id,
        data
    )


# --------------------------------------
# CHANGE STATUS
# --------------------------------------


@router.patch(
    "/{comida_id}/estado",
    response_model=ComidaResponse,
    dependencies=[
        Depends(
            requirePermission(
                "cambiar-estado-snack"
            )
        )
    ]
)
def change_estado_comida(
    comida_id: int,
    service: ComidaService = Depends(
        get_comida_service
    )
):

    return service.change_estado(
        comida_id
    )