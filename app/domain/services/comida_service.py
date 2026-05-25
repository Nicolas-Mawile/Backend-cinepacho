from fastapi import HTTPException, status

from app.infrastructure.repositories.comida_repository import (
    ComidaRepository
)

from app.api.schemas.comida import (
    ComidaCreate,
    ComidaUpdate
)


class ComidaService:

    def __init__(
        self,
        repository: ComidaRepository
    ):
        self.repository = repository

    # --------------------------------
    # CREATE
    # --------------------------------

    def create_comida(
        self,
        data: ComidaCreate
    ):

        existing = self.repository.get_by_nombre(
            data.nombre
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La comida ya existe"
            )

        return self.repository.create(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio=data.precio,
            imagenUrl=data.imagenUrl
        )

    # --------------------------------
    # GET ALL
    # --------------------------------

    def get_all_comidas(self):

        return self.repository.get_all()

    # --------------------------------
    # GET BY ID
    # --------------------------------

    def get_comida_by_id(
        self,
        comida_id: int
    ):

        comida = self.repository.get_by_id(
            comida_id
        )

        if not comida:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comida no encontrada"
            )

        return comida

    # --------------------------------
    # UPDATE
    # --------------------------------

    def update_comida(
        self,
        comida_id: int,
        data: ComidaUpdate
    ):

        comida = self.repository.get_by_id(
            comida_id
        )

        if not comida:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comida no encontrada"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "nombre" in update_data:

            existing = self.repository.get_by_nombre(
                update_data["nombre"]
            )

            if existing and existing.id != comida.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una comida con ese nombre"
                )

        return self.repository.update(
            comida,
            update_data
        )

    # --------------------------------
    # DELETE
    # --------------------------------

    def update_comida(
        self,
        comida_id: int,
        data: ComidaUpdate
    ):

        comida = self.repository.get_by_id(
            comida_id
        )

        if not comida:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comida no encontrada"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "nombre" in update_data:

            existing = self.repository.get_by_nombre(
                update_data["nombre"]
            )

            if existing and existing.id != comida.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una comida con ese nombre"
                )

        return self.repository.update(
            comida,
            update_data
        )

    # --------------------------------
    # DELETE
    # --------------------------------

    def delete_comida(
        self,
        comida_id: int
    ):

        comida = self.repository.get_by_id(
            comida_id
        )

        if not comida:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comida no encontrada"
            )

        self.repository.delete(comida)
    def change_estado(
        self,
        comida_id: int
    ):

        comida = self.repository.get_by_id(
            comida_id
        )

        if not comida:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comida no encontrada"
            )

        comida.estaActiva = (
            not comida.estaActiva
        )

        return self.repository.update(
            comida,
            {
                "estaActiva": comida.estaActiva
            }
        )