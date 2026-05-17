from sqlalchemy import Column, Boolean, Integer, String

class Persona:
    """
    Clase abstracta reutilizable.
    NO genera tabla en BD.
    """
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    correo = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
