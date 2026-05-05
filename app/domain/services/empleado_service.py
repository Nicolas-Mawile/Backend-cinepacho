"""Empleado domain service."""

import random
import string
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.repositories.empleado_repository import EmpleadoRepository

class EmpleadoService:
    """Servicio para la gestión de empleados."""

    @staticmethod
    def generar_correo_laboral(nombre: str, apellido: str) -> str:
        """Genera un correo laboral único."""
        # Lógica simple: nombre.apellido@cinepacho.com + sufijo aleatorio si es necesario
        base = f"{nombre.lower().split()[0]}.{apellido.lower().split()[0]}"
        # Limpiar caracteres especiales si fuera necesario
        return f"{base}@cinepacho.com"

    def crear_empleado(self, repo: EmpleadoRepository, datos: dict) -> Empleado:
        """Crea un nuevo empleado con correo laboral generado."""
        nombre = datos.get("primer_nombre", "")
        apellido = datos.get("primer_apellido", "")
        
        # Generar correo laboral
        correo_laboral = self.generar_correo_laboral(nombre, apellido)
        
        # Construir nombre completo
        nombre_completo = f"{datos.get('primer_nombre', '')} {datos.get('segundo_nombre', '')} {datos.get('primer_apellido', '')} {datos.get('segundo_apellido', '')}".replace("  ", " ").strip()
        
        # Mapear datos para el modelo Empleado/Persona
        empleado_data = {
            "nombre": datos.get("primer_nombre"),
            "apellido": datos.get("primer_apellido"),
            "email": datos.get("email"),
            "telefono": datos.get("telefono"),
            "cedula": str(datos.get("cedula_ciudadania")),
            "nombre_completo": nombre_completo,
            "fecha_inicio_contrato": datos.get("fecha_inicio_contrato") or datos.get("fecha_nacimiento"), # Fallback
            "salario": datos.get("salario"),
            "cargo": datos.get("cargo"),
            "multiplex_id": datos.get("multiplex_id"),
            "correo_laboral": correo_laboral,
            "activo": True
        }
        
        # Nota: El contrato tiene campos que no están en el modelo de la tarea, 
        # pero los mapeamos lo mejor posible.
        
        nuevo_empleado = Empleado(**empleado_data)
        return repo.add(nuevo_empleado)
