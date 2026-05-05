"""Empleado domain service."""

import random
import string
from sqlalchemy import select
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol
from app.infrastructure.models.persona import Persona
from app.infrastructure.repositories.empleado_repository import EmpleadoRepository
from app.domain.services.auth_service import AuthService

class EmpleadoService:
    """Servicio para la gestión de empleados."""

    @staticmethod
    def generar_correo_laboral(nombre: str, apellido: str) -> str:
        """Genera un correo laboral único."""
        base = f"{nombre.lower().split()[0]}.{apellido.lower().split()[0]}"
        return f"{base}@cinepacho.com"

    @staticmethod
    def generar_codigo_empleado(mx_code: str, seq: int) -> str:
        """Genera un código de empleado (CP-{mx_code}-{seq:04d})."""
        return f"CP-{mx_code}-{seq:04d}"

    def crear_empleado(self, repo: EmpleadoRepository, datos: dict) -> Empleado:
        """Crea un nuevo empleado con código y correo laboral generados."""
        # Obtener código del multiplex
        stmt = select(Multiplex).where(Multiplex.id == datos.get("multiplex_id"))
        multiplex = repo.db.execute(stmt).scalar_one_or_none()
        mx_code = multiplex.codigo if multiplex else "XX"
        
        # Generar código secuencial
        seq = repo.siguiente_numero_secuencia(datos.get("multiplex_id"))
        codigo_empleado = self.generar_codigo_empleado(mx_code, seq)
        
        # Generar correo laboral
        nombre = datos.get("primer_nombre", "")
        apellido = datos.get("primer_apellido", "")
        correo_laboral = self.generar_correo_laboral(nombre, apellido)
        
        # Construir nombre completo
        nombre_completo = f"{datos.get('primer_nombre', '')} {datos.get('segundo_nombre', '')} {datos.get('primer_apellido', '')} {datos.get('segundo_apellido', '')}".replace("  ", " ").strip()
        
        # Mapear datos
        empleado_data = {
            "nombre": datos.get("primer_nombre"),
            "apellido": datos.get("primer_apellido"),
            "email": datos.get("email"),
            "telefono": datos.get("telefono"),
            "cedula": str(datos.get("cedula_ciudadania")),
            "nombre_completo": nombre_completo,
            "codigo_empleado": codigo_empleado,
            "seq": seq,
            "fecha_inicio_contrato": datos.get("fecha_inicio_contrato") or datos.get("fecha_nacimiento"),
            "salario": datos.get("salario"),
            "cargo": datos.get("cargo"),
            "multiplex_id": datos.get("multiplex_id"),
            "correo_laboral": correo_laboral,
            "activo": True
        }
        
        nuevo_empleado = Empleado(**empleado_data)
        repo.add(nuevo_empleado)
        
        # Crear credenciales si es cajero o administrador (director)
        cargo_val = datos.get("cargo")
        if hasattr(cargo_val, "value"):
            cargo_val = cargo_val.value
            
        if cargo_val in ["cajero", "administrador", "director"]:
            self.crear_usuario_para_empleado(repo.db, nuevo_empleado, datos.get("cedula_ciudadania"))
            
        return nuevo_empleado

    def crear_usuario_para_empleado(self, db, empleado: Empleado, password_base: str):
        """Crea un registro de Usuario vinculado al Empleado."""
        # Buscar rol correspondiente
        # Normalizar comparación de cargos para el rol
        cargo_str = empleado.cargo.value if hasattr(empleado.cargo, "value") else str(empleado.cargo)
        
        rol_nombre = "Cajero" if cargo_str == "cajero" else "Administrador Multiplex"
        stmt_rol = select(Rol).where(Rol.nombre == rol_nombre)
        rol = db.execute(stmt_rol).scalar_one_or_none()
        
        if not rol:
            return
            
        auth_service = AuthService()
        hashed_password = auth_service.hash_password(str(password_base))
        
        nuevo_usuario = Usuario(
            password=hashed_password,
            estaActivo=True,
            persona_id=empleado.id,
            rol_id=rol.id
        )
        db.add(nuevo_usuario)
        db.commit()
