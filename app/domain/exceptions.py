"""Domain-specific exceptions."""


class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ValidationError(DomainError):
    pass


# Excepciones de Sala
class SalaNotFoundError(NotFoundError):
    """Sala no encontrada."""
    pass


class MultiplexNotFoundError(NotFoundError):
    """Multiplex no encontrado."""
    pass


class SalaLimitExceededError(ValidationError):
    """Límite de salas por multiplex alcanzado."""
    pass


class DuplicateNumeroSalaError(ValidationError):
    """El número de sala ya existe."""
    pass


class SalaConfigurationError(ValidationError):
    """Configuración inválida de sala."""
    pass


class SalaDependenciesError(ValidationError):
    """La sala tiene dependencias (funciones, sillas)."""
    pass
