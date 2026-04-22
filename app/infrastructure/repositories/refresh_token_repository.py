"""RefreshToken repository."""
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refrescar_token import RefreshToken
import hashlib


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _hash(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def guardar(self, cliente_id: int, token: str, expires_at: datetime) -> None:
        rt = RefreshToken(
            cliente_id=cliente_id,
            token_hash=self._hash(token),
            expires_at=expires_at,
            revocado=False,
        )
        self.session.add(rt)
        await self.session.commit()

    async def buscar_valido(self, token: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == self._hash(token),
                RefreshToken.revocado == False,
            )
        )
        return result.scalar_one_or_none()

    async def revocar(self, token: str) -> None:
        rt = await self.buscar_valido(token)
        if rt:
            rt.revocado = True
            await self.session.commit()