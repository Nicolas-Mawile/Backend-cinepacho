from operator import or_

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased, aliased

from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.empleado import Empleado


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def buscarPorCorreo(self, correo: str):
        stmt = (select(Usuario).join(Persona).where(Persona.correo == correo))
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def crear(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def buscarPorId(self, id: int) -> Usuario:
        stmt = select(Usuario).where(Usuario.id == id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def buscarPorCorreoLogin(self, correo: str) -> Usuario | None:
        EmpleadoAlias = aliased(Empleado)
        stmt = (select(Usuario).join(Persona, Usuario.personaId == Persona.id)
            .outerjoin(EmpleadoAlias, EmpleadoAlias.id == Persona.id)
            .where(or_(Persona.correo == correo, EmpleadoAlias.correoLaboral == correo)))
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()