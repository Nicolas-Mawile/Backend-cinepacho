"""API dependencies for authentication and authorization."""


def get_current_user():
    raise NotImplementedError


def require_rol(role: str):
    raise NotImplementedError


def require_multiplex(multiplex_id: int):
    raise NotImplementedError
