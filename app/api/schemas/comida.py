from pydantic import BaseModel, Field


class ComidaBase(BaseModel):

    nombre: str = Field(
        min_length=2,
        max_length=100
    )

    descripcion: str | None = None

    precio: float = Field(gt=0)

    imagenUrl: str | None = None


class ComidaCreate(ComidaBase):
    pass


class ComidaUpdate(BaseModel):

    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    descripcion: str | None = None

    precio: float | None = Field(
        default=None,
        gt=0
    )

    imagenUrl: str | None = None


class ComidaResponse(ComidaBase):

    id: int
    estaActiva: bool

    class Config:
        from_attributes = True