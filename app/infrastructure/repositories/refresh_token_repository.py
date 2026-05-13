"""RefreshToken repository."""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.models.refrescar_token import RefreshToken
import hashlib


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def _hash(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def guardar(self, cliente_id: int, token: str, expires_at: datetime) -> None:
        rt = RefreshToken(
            cliente_id=cliente_id,
            token_hash=self._hash(token),
            expires_at=expires_at,
            revocado=False,
        )
        self.db.add(rt)
        self.db.commit()

    def buscar_valido(self, token: str) -> RefreshToken | None:
        result = self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == self._hash(token),
                RefreshToken.revocado == False,
            )
        )
        return result.scalar_one_or_none()

    def revocar(self, token: str) -> None:
        rt = self.buscar_valido(token)
        if rt:
            rt.revocado = True
            self.db.commit()