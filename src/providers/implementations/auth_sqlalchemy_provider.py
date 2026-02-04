from datetime import datetime
from typing import Optional, List

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.auth_model import RefreshToken
from src.providers.interfaces.auth_provider_interface import AuthProviderInterface


class AuthSqlAlchemyProvider(AuthProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def salvar_refresh_token(
            self,
            token: str,
            username: str,
            email: str,
            display_name: str,
            groups: List[str],
            role: str,
            expires_at: datetime
    ) -> RefreshToken:
        db_token = RefreshToken(
            token=token,
            username=username,
            email=email,
            display_name=display_name,
            groups=groups,
            role=role,
            expires_at=expires_at
        )
        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return db_token

    async def buscar_refresh_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def revogar_refresh_token(self, token: str) -> bool:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(stmt)
        item = result.scalars().first()

        if item:
            await self.session.delete(item)
            await self.session.commit()
            return True
        return False

    async def revogar_tokens_usuario(self, username: str) -> bool:
        stmt = delete(RefreshToken).where(RefreshToken.username == username)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
