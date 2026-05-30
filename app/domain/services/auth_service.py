from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
from app.utils.timezone import nowColombia

class AuthService:
    """Encapsula la lógica de autenticación y creación de tokens."""
    def __init__(self):
        self.pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hashPassword(self, password: str) -> str:
        """Genera un hash seguro para una contraseña simple."""
        return self.pwdContext.hash(password)

    def verifyPassword(self, plainPassword: str, hashedPassword: str) -> bool:
        """Verifica si la contraseña sin hash coincide con el hash guardado."""
        return self.pwdContext.verify(plainPassword, hashedPassword)

    def createAccessToken(self, data: dict) -> str:
        """Genera un JWT de acceso con expiración establecida."""
        payload = data.copy()
        expiration = nowColombia() + timedelta(minutes=settings.access_token_expire_minutes)
        payload.update({"exp": expiration, "jti": str(uuid4())})

        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    
    def createRefreshToken(self, data: dict) -> str:

        toEncode = data.copy()
        expire = nowColombia() + timedelta(days=7)

        toEncode.update(
            {
                "exp": expire,
                "type": "refresh"
            }
        )
        encodedJwt = jwt.encode(toEncode, settings.secret_key, algorithm=settings.algorithm)
        return encodedJwt