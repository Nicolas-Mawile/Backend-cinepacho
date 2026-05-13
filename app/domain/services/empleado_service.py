"""Empleado domain service."""
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol
from app.infrastructure.models.contrato import Contrato
from app.infrastructure.models.cargoEnum import CargoEnum
from app.domain.constants.roles import RoleEnum
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.domain.services.auth_service import AuthService


class EmpleadoService:
    def __init__(self, db: Session):
        self.db = db
        self.authService = AuthService()

    @staticmethod
    def generarCorreoLaboral(nombres: str, apellidos: str) -> str:
        primerNombre = nombres.lower().split()[0]
        primerApellido = apellidos.lower().split()[0]
        return f"{primerNombre}.{primerApellido}@cinepacho.com"

    @staticmethod
    def generarCodigoEmpleado(multiplexCodigo: str, secuencia: int) -> str:
        return f"CP-{multiplexCodigo}-{secuencia:04d}"

    def obtenerRol(self, cargo: CargoEnum) -> Rol:
        roleName = ("ADMIN_MULTIPLEX" if cargo == CargoEnum.director else "CAJERO")
        stmt = select(Rol).where(Rol.nombre == roleName)
        rol = self.db.execute(stmt).scalar_one_or_none()
        if not rol:
            raise ValueError("Rol no encontrado")
        return rol

    def crearEmpleado(self, repo: EmpleadoRepository, datos: dict) -> Empleado:

        # ======================================
        # VALIDAR EMPLEADO EXISTENTE
        # ======================================

        empleadoExistente = repo.buscarPorCorreo(datos.get("correo"))

        if empleadoExistente:
            raise ValueError("Empleado ya existe")

        # ======================================
        # BUSCAR MULTIPLEX
        # ======================================

        stmt = select(Multiplex).where(Multiplex.id == datos.get("multiplexId"))
        multiplex = self.db.execute(stmt).scalar_one_or_none()

        if not multiplex:
            raise ValueError("Multiplex no encontrado")

        # ======================================
        # GENERAR SECUENCIA
        # ======================================
        secuencia = repo.siguiente_numero_secuencia(datos.get("multiplexId"))

        # ======================================
        # GENERAR CODIGO
        # ======================================
        codigoEmpleado = self.generarCodigoEmpleado(multiplex.codigo, secuencia)

        # ======================================
        # GENERAR CORREO LABORAL
        # ======================================
        correoLaboral = self.generarCorreoLaboral(datos.get("nombres"), datos.get("apellidos"))

        # ======================================
        # VALIDAR CORREO LABORAL
        # ======================================
        correoExiste = repo.buscarPorCorreoLaboral(correoLaboral)

        if correoExiste:
            raise ValueError("Correo laboral ya generado anteriormente")

        # ======================================
        # OBTENER ROL
        # ======================================
        rol = self.obtenerRol(datos.get("cargo"))

        # ======================================
        # CREAR EMPLEADO
        # ======================================
        empleado = Empleado(
            nombres=datos.get("nombres"),
            apellidos=datos.get("apellidos"),
            correo=datos.get("correo"),
            telefono=datos.get("telefono"),
            codigoEmpleado=codigoEmpleado,
            correoLaboral=correoLaboral)
        self.db.add(empleado)
        self.db.flush()

        # ======================================
        # CREAR USUARIO
        # ======================================
        usuario = Usuario(passwordHash=self.authService.hashPassword(datos.get("password")), personaId=empleado.id, rolId=rol.id)
        self.db.add(usuario)
        self.db.flush()

        # ======================================
        # ASOCIAR USUARIO
        # ======================================
        empleado.usuarioId = usuario.id

        # ======================================
        # CREAR CONTRATO
        # ======================================
        contrato = Contrato(
            empleadoId=empleado.id,
            multiplexId=datos.get("multiplexId"),
            salario=datos.get("salario"),
            cargo=datos.get("cargo"),
            fechaInicio=date.today(),
            activo=True)

        self.db.add(contrato)
        # ======================================
        # COMMIT
        # ======================================
        self.db.commit()
        self.db.refresh(empleado)
        return empleado
    
    def obtenerRolSegunCargo(self, cargo: CargoEnum) -> Rol:
        if cargo == CargoEnum.cajero:
            roleName = RoleEnum.EMPLEADO_CAJERO.value

        elif cargo in [CargoEnum.aseador, CargoEnum.despachador]:
            roleName = RoleEnum.EMPLEADO_OTRO.value

        elif cargo == CargoEnum.administrador:
            roleName = RoleEnum.ADMIN_MULTIPLEX.value

        elif cargo == CargoEnum.director:
            roleName = RoleEnum.ADMIN_GENERAL.value

        else:
            raise ValueError("Cargo inválido")

        stmt = select(Rol).where(Rol.nombre == roleName)
        rol = (self.db.execute(stmt).scalar_one_or_none())

        if not rol:
            raise ValueError(f"Rol {roleName} no existe")
        return rol