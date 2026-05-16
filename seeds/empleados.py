"""Seed de empleados."""
import sys
import os
from datetime import date

# Agregar raíz del proyecto al path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from sqlalchemy import select

from app.database import SessionLocal

from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.contrato import Contrato
from app.infrastructure.models.rol import Rol
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.cargoEnum import CargoEnum

from app.domain.services.auth_service import AuthService


EMPLEADOS = [
    {
        "nombres": "Carlos",
        "apellidos": "Pérez",
        "correo": "carlos@cinepacho.com",
        "telefono": "3001234567",
        "password": "Password123",
        "codigoEmpleado": "EMP-001",
        "correoLaboral": "carlos@cinepacho.com",
        "cargo": CargoEnum.cajero,
        "salario": 1500000,
        "multiplexCodigo": "TIT"
    },
    {
        "nombres": "Ana",
        "apellidos": "Rodríguez",
        "correo": "ana@cinepacho.com",
        "telefono": "3002223333",
        "password": "Password123",
        "codigoEmpleado": "EMP-002",
        "correoLaboral": "ana@cinepacho.com",
        "cargo": CargoEnum.director,
        "salario": 3500000,
        "multiplexCodigo": "UNI"
    },
    {
        "nombres": "Luis",
        "apellidos": "Martínez",
        "correo": "luis@cinepacho.com",
        "telefono": "3004445555",
        "password": "Password123",
        "codigoEmpleado": "EMP-003",
        "correoLaboral": "luis@cinepacho.com",
        "cargo": CargoEnum.aseador,
        "salario": 1300000,
        "multiplexCodigo": "GRE"
    }
]


def seedRoles(db):
    """
    Crea roles básicos.
    """

    roles = [
        "ADMIN_GENERAL",
        "ADMIN_MULTIPLEX",
        "CAJERO",
        "CLIENTE"
    ]

    for roleName in roles:

        stmt = select(Rol).where(
            Rol.nombre == roleName
        )

        existing = db.execute(
            stmt
        ).scalar_one_or_none()

        if not existing:
            db.add(Rol(nombre=roleName))

    db.commit()


def getRoleName(cargo: CargoEnum):

    if cargo == CargoEnum.director:
        return "ADMIN_MULTIPLEX"

    return "CAJERO"


def run():

    print("Iniciando seed de empleados...")

    db = SessionLocal()

    authService = AuthService()

    try:

        # ======================================
        # CREAR ROLES
        # ======================================

        seedRoles(db)

        # ======================================
        # CREAR EMPLEADOS
        # ======================================

        for data in EMPLEADOS:

            existing = db.execute(
                select(Empleado).where(
                    Empleado.correoLaboral == data["correoLaboral"]
                )
            ).scalar_one_or_none()

            if existing:

                print(
                    f"✓ Empleado ya existe: "
                    f"{data['correoLaboral']}"
                )

                continue

            multiplex = db.execute(
                select(Multiplex).where(
                    Multiplex.codigo == data["multiplexCodigo"]
                )
            ).scalar_one_or_none()

            if not multiplex:

                print(
                    f"✗ Multiplex no encontrado: "
                    f"{data['multiplexCodigo']}"
                )

                continue

            roleName = getRoleName(data["cargo"])

            rol = db.execute(
                select(Rol).where(
                    Rol.nombre == roleName
                )
            ).scalar_one()

            rolCliente = db.execute(
                select(Rol).where(
                    Rol.nombre == "CLIENTE"
                )
            ).scalar_one()

            # ======================================
            # CREAR CLIENTE
            # ======================================

            cliente = Cliente(
                nombres=data["nombres"],
                apellidos=data["apellidos"],
                correo=data["correo"],
                telefono=data["telefono"],
                activo=True,
                usuarioId=None
            )

            db.add(cliente)
            db.flush()

            # ======================================
            # CREAR USUARIO CLIENTE
            # ======================================

            usuarioCliente = Usuario(
                passwordHash=authService.hashPassword(
                    data["password"]
                ),
                personaId=cliente.id,
                rolId=rolCliente.id
            )

            db.add(usuarioCliente)
            db.flush()

            cliente.usuarioId = usuarioCliente.id

            # ======================================
            # CREAR EMPLEADO
            # ======================================

            empleado = Empleado(
                nombres=data["nombres"],
                apellidos=data["apellidos"],
                correo=data["correoLaboral"],
                telefono=data["telefono"],
                activo=True,
                codigoEmpleado=data["codigoEmpleado"],
                correoLaboral=data["correoLaboral"],
                usuarioId=1
            )

            db.add(empleado)
            db.flush()

            # ======================================
            # CREAR USUARIO EMPLEADO
            # ======================================

            usuario = Usuario(
                passwordHash=authService.hashPassword(
                    data["password"]
                ),
                personaId=empleado.id,
                rolId=rol.id
            )

            db.add(usuario)
            db.flush()

            # ======================================
            # ACTUALIZAR usuarioId
            # ======================================

            empleado.usuarioId = usuario.id

            # ======================================
            # CREAR CONTRATO
            # ======================================

            contrato = Contrato(
                empleadoId=empleado.id,
                multiplexId=multiplex.id,
                cargo=data["cargo"],
                salario=data["salario"],
                fechaInicio=date.today(),
                activo=True
            )

            db.add(contrato)

            # ======================================
            # COMMIT FINAL
            # ======================================

            db.commit()

            print(
                f"✓ Empleado creado: "
                f"{empleado.nombres} "
                f"{empleado.apellidos}"
            )

        print("✓ Seed empleados completado.")

    except Exception as e:

        db.rollback()

        print(f"✗ Error seed empleados: {e}")

        raise

    finally:
        db.close()


if __name__ == "__main__":
    run()