from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.models.auth_model import RefreshToken


class AuthProviderInterface(ABC):

    @abstractmethod
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
        pass

    @abstractmethod
    async def buscar_refresh_token(self, token: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    async def revogar_refresh_token(self, token: str) -> bool:
        pass
