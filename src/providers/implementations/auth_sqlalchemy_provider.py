from datetime import datetime
from typing import Optional

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.models.auth_model import RefreshToken, User
from src.providers.interfaces.auth_provider_interface import AuthProviderInterface


class AuthSqlAlchemyProvider(AuthProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, user_data: dict) -> User:
        stmt = select(User).where(User.username == user_data["username"])
        result = await self.session.execute(stmt)
        db_user = result.scalars().first()

        if not db_user:
            db_user = User(
                username=user_data["username"],
                display_name=user_data["display_name"],
                email=user_data["email"],
                groups=user_data["groups"],
                role=user_data["role"]
            )
            self.session.add(db_user)
        else:
            db_user.display_name = user_data["display_name"]
            db_user.email = user_data["email"]
            db_user.groups = user_data["groups"]
            db_user.role = user_data["role"]

        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def salvar_refresh_token(self, token: str, username: str, expires_at: datetime) -> RefreshToken:
        db_token = RefreshToken(
            token=token,
            username=username,
            expires_at=expires_at
        )
        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return db_token

    async def buscar_refresh_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).options(joinedload(RefreshToken.usuario)).where(RefreshToken.token == token)
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

    async def atualizar_registro_usuario(self, username: str, registro: str, tipo_registro: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if user:
            user.registro_profissional = registro
            user.tipo_registro = tipo_registro
            await self.session.commit()
            await self.session.refresh(user)

        return user

    async def buscar_usuario_por_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()
