from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.models.auth_model import RefreshToken
from src.schemas.auth import UserSchema


class AuthProviderInterface(ABC):

    @abstractmethod
    async def salvar_refresh_token(
            self,
            token: str,
            username: str,
            expires_at: datetime
    ) -> RefreshToken:
        pass

    @abstractmethod
    async def buscar_refresh_token(self, token: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    async def revogar_refresh_token(self, token: str) -> bool:
        pass

    async def atualizar_registro_usuario(self, username, registro, tipo_registro) -> Optional[UserSchema]:
        pass

    async def get_or_create_user(self, user_data):
        pass

    async def buscar_usuario_por_username(self, username: str) -> Optional[UserSchema]:
        pass
