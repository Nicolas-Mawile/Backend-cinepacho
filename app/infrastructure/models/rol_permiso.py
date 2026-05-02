from sqlalchemy import Column, ForeignKey, Table
from cinepachobackend.app.infrastructure.models.base import Base

rol_permiso = Table(
    "rol_permiso",
    Base.metadata,
    Column("rol_id", ForeignKey("rol.id"), primary_key=True),
    Column("permiso_id", ForeignKey("permiso.id"), primary_key=True),
)