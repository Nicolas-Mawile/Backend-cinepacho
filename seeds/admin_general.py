from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol
from app.domain.services.auth_service import AuthService

db = SessionLocal()
authService = AuthService()

rolAdmin = db.execute(select(Rol).where(Rol.nombre == "ADMIN-GENERAL")).scalar_one()
persona = db.execute(select(Persona).where(Persona.correo == "admin@cinepacho.com")).scalar_one_or_none()

if not persona:
    persona = Persona(
        nombres="Admin",
        apellidos="General",
        correo="admin@cinepacho.com",
        telefono="3000000000"
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    print("Persona admin creada")

usuario = db.execute(select(Usuario).where(Usuario.personaId == persona.id)).scalar_one_or_none()

if not usuario:
    usuario = Usuario(
        personaId=persona.id,
        rolId=rolAdmin.id,
        passwordHash=authService.hashPassword("Admin123*"))

    db.add(usuario)
    db.commit()
    print("Usuario admin creado")
else:
    print("Usuario admin ya existe")

print("SEED ADMIN FINALIZADO")