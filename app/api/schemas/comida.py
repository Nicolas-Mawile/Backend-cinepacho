from pydantic import BaseModel, Field


class ComidaBase(BaseModel):

    nombre: str = Field(
        min_length=2,
        max_length=100
    )

    precio: float = Field(gt=0)


class ComidaCreate(ComidaBase):
    pass


class ComidaUpdate(BaseModel):

    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    precio: float | None = Field(
        default=None,
        gt=0
    )


class ComidaResponse(ComidaBase):

    id: int
    estaActiva: bool

    class Config:
        from_attributes = True