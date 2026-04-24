from sqlalchemy.orm import Session
from app.infrastructure.repositories.multiplex_repository import MultiplexRepository

async def generar_codigo(nombre: str, repo: MultiplexRepository) -> str:
    """
    Genera código de 3 letras a partir del nombre.
    Si ya existe, agrega un número: TIT → TIT2 → TIT3
    """
    base = nombre[:3].upper().replace(" ", "")
    codigo = base
    sufijo = 2
    while await repo.buscar_por_codigo(codigo) is not None:
        codigo = f"{base}{sufijo}"
        sufijo += 1
    return codigo