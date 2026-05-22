"""Empleado domain service."""
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol
from app.infrastructure.models.contrato import Contrato
from app.infrastructure.models.cargoEnum import CargoEnum
from app.domain.constants.roles import RoleEnum
from app.infrastructure.repositories.empleado_repository import (EmpleadoRepository)
from app.infrastructure.repositories.usuarioRepository import (UsuarioRepository)
from app.domain.services.auth_service import (AuthService)
import unicodedata

class EmpleadoService:

    def __init__(self, db: Session):
        self.db = db
        self.authService = AuthService()

    @staticmethod
    def normalizarTexto(texto: str) -> str:
        texto = unicodedata.normalize("NFKD", texto)
        return "".join(c for c in texto if not unicodedata.combining(c)).lower()

    # ==========================================
    # CORREO LABORAL
    # ==========================================
    @staticmethod
    def generarCorreoLaboral(nombres: str, apellidos: str, repo) -> str:
        primerNombre = (EmpleadoService.normalizarTexto(nombres).split()[0])
        primerApellido = (EmpleadoService.normalizarTexto(apellidos).split()[0])
        baseCorreo = (f"{primerNombre}.{primerApellido}")
        correo = (f"{baseCorreo}@cinepacho.com")
        contador = 1

        while repo.buscarPorCorreoLaboral(correo):
            correo = (f"{baseCorreo}{contador}@cinepacho.com")
            contador += 1
        return correo

    # ==========================================
    # CODIGO EMPLEADO
    # ==========================================
    @staticmethod
    def generarCodigoEmpleado(multiplexCodigo: str, secuencia: int) -> str:
        return (f"CP-{multiplexCodigo}-{secuencia:04d}")

    # ==========================================
    # ROLES
    # ==========================================
    def obtenerRolSegunCargo(self, cargo: CargoEnum) -> Rol:
        if cargo == CargoEnum.cajero:
            roleName = (RoleEnum.EMPLEADO_CAJERO.value)

        elif cargo in [CargoEnum.aseador, CargoEnum.despachador_comida]:
            roleName = (RoleEnum.EMPLEADO_OTRO.value)

        elif cargo == CargoEnum.administrador:
            roleName = (RoleEnum.ADMIN_GENERAL.value)

        elif cargo == CargoEnum.director:
            roleName = (RoleEnum.ADMIN_MULTIPLEX.value)

        else:
            raise ValueError("Cargo inválido")

        stmt = select(Rol).where(Rol.nombre == roleName)
        rol = (self.db.execute(stmt).scalar_one_or_none())

        if not rol:
            raise ValueError(f"Rol {roleName} no existe")
        return rol

    def obtenerRolCliente(self) -> Rol:
        stmt = select(Rol).where(Rol.nombre == RoleEnum.CLIENTE.value)
        rol = (self.db.execute(stmt).scalar_one_or_none())
        if not rol:
            raise ValueError(f"Rol {RoleEnum.CLIENTE.value} no existe")
        return rol

    # ==========================================
    # CREAR EMPLEADO
    # ==========================================
    def crearEmpleado(self, repo: EmpleadoRepository, datos: dict):
        usuarioRepo = UsuarioRepository(self.db)

        # ======================================
        # VALIDAR CORREO PERSONAL
        # ======================================
        if usuarioRepo.buscarPorCorreo(datos.get("correo")):
            raise ValueError("El correo ya está registrado")

        # ======================================
        # BUSCAR MULTIPLEX
        # ======================================
        stmt = select(Multiplex).where(Multiplex.id == datos.get("multiplexId"))
        multiplex = (self.db.execute(stmt).scalar_one_or_none())

        if not multiplex:
            raise ValueError("Multiplex no encontrado")

        # ======================================
        # GENERAR SECUENCIA
        # ======================================
        secuencia = (repo.siguiente_numero_secuencia(multiplex.codigo))

        # ======================================
        # GENERAR CODIGO
        # ======================================
        codigoEmpleado = (self.generarCodigoEmpleado(multiplex.codigo, secuencia))

        # ======================================
        # GENERAR CORREO LABORAL
        # ======================================
        correoLaboral = (self.generarCorreoLaboral(datos.get("nombres"), datos.get("apellidos"), repo))

        # ======================================
        # VALIDAR CORREO LABORAL
        # ======================================
        if usuarioRepo.buscarPorCorreo(correoLaboral):
            raise ValueError("Correo laboral ya registrado")

        # ======================================
        # ROLES
        # ======================================
        rolEmpleado = (self.obtenerRolSegunCargo(datos.get("cargo")))
        rolCliente = (self.obtenerRolCliente())

        # ======================================
        # HASH PASSWORD
        # ======================================
        passwordHash = (self.authService.hashPassword(datos.get("password")))

        # ======================================
        # CLIENTE
        # ======================================
        cliente = Cliente(nombres=datos.get("nombres"), apellidos=datos.get("apellidos"), correo=datos.get("correo"), telefono=datos.get("telefono"))
        self.db.add(cliente)
        self.db.flush()

        # ======================================
        # CREAR EMPLEADO
        # ======================================
        empleado = Empleado(nombres=datos.get("nombres"), apellidos=datos.get("apellidos"), correo=datos.get("correo"), telefono=datos.get("telefono"),
                            codigoEmpleado=codigoEmpleado, correoLaboral=correoLaboral, clienteId=cliente.id)
        self.db.add(empleado)
        self.db.flush()

        # ======================================
        # USUARIO EMPLEADO
        # ======================================
        usuarioEmpleado = Usuario(empleadoId=empleado.id, passwordHash=passwordHash, rolId=rolEmpleado.id)
        self.db.add(usuarioEmpleado)

        # ======================================
        # USUARIO CLIENTE
        # ======================================
        usuarioCliente = Usuario(clienteId=cliente.id, passwordHash=passwordHash,rolId=rolCliente.id)
        self.db.add(usuarioCliente)

        # ======================================
        # CONTRATO
        # ======================================
        contrato = Contrato(empleadoId=empleado.id, multiplexId=datos.get("multiplexId"), salario=datos.get("salario"), 
                            cargo=datos.get("cargo"), fechaInicio=date.today(), activo=True)
        self.db.add(contrato)

        # ======================================
        # COMMIT
        # ======================================
        self.db.commit()
        self.db.refresh(empleado)

        # ======================================
        # RESPUESTA
        # ======================================
        return {

            "empleado": {
                "id": empleado.id,
                "codigoEmpleado": (empleado.codigoEmpleado),
                "correoLaboral": (empleado.correoLaboral),
                "nombres": empleado.nombres,
                "apellidos": (empleado.apellidos),
                "activo": empleado.activo},
            "credencialesEmpleado": {
                "correo": correoLaboral,
                "password": (datos.get("password"))},
            "credencialesCliente": {
                "correo": (datos.get("correo")),
                "password": (datos.get("password"))
            }
        }
    