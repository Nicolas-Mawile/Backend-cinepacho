from pydantic import BaseModel
from typing import Optional

# =====================================
# PELÍCULA
# =====================================

class EvaluarPeliculaRequest(BaseModel):
    funcionId: int
    peliculaId: int
    puntuacion: int
    comentario: str

# =====================================
# SERVICIO
# =====================================
class EvaluarServicioRequest(BaseModel):
    facturaId: int
    servicioId: int
    puntuacion: int
    comentario: str

# =====================================
# RESPONSE
# =====================================
class EvaluacionResponse(BaseModel):
    id: int
    puntuacion: int
    comentario: str
    model_config = {"from_attributes": True}