import os
import time
from typing import Optional, Dict, Union

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth_model import User
from src.resources.database import get_app_db_session

load_dotenv()


class AuthHandler:
    security = HTTPBearer()
    secret = os.getenv("JWT_SECRET")
    exp_time = int(os.getenv("JWT_EXP_MINUTES")) * 60
    algorithm = "HS256"

    def encode_token(self, user_id: str, claims: Optional[Dict] = None) -> str:
        payload = {
            "sub": user_id,
            "exp": time.time() + self.exp_time,
            "iat": time.time(),
            "type": "access"
        }

        if claims:
            payload.update(claims)

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: Union[HTTPAuthorizationCredentials, str] = Security(security)) -> Dict:
        if hasattr(token, "credentials"):
            actual_token = token.credentials
        else:
            actual_token = str(token)

        try:
            payload = jwt.decode(actual_token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")

    async def get_current_user(
            self,
            auth: HTTPAuthorizationCredentials = Security(security),
            session: AsyncSession = Depends(get_app_db_session)
    ):
        token = auth.credentials
        payload = self.decode_token(token)

        username = payload.get("sub") or payload.get("username")

        if not username:
            raise HTTPException(status_code=401, detail="Token inválido: identificador ausente")

        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user_db = result.scalars().first()

        if not user_db:
            raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")

        return {
            "sub": user_db.username,
            "username": user_db.username,
            "email": user_db.email,
            "display_name": user_db.display_name,
            "displayName": user_db.display_name,
            "name": user_db.display_name,
            "groups": user_db.groups if user_db.groups else [],
            "role": user_db.role,
            "registro_profissional": user_db.registro_profissional,
            "tipo_registro": user_db.tipo_registro
        }


auth_handler = AuthHandler()


def _normalizar_grupos(grupos):
    if not grupos:
        return set()
    return {str(grupo).strip().lower() for grupo in grupos if grupo is not None}


def require_groups(grupos_permitidos):
    grupos_permitidos_norm = _normalizar_grupos(grupos_permitidos)

    async def _guard(current_user: dict = Depends(auth_handler.get_current_user)):
        grupos_usuario = _normalizar_grupos(current_user.get("groups"))

        if grupos_permitidos_norm and not (grupos_usuario & grupos_permitidos_norm):
            raise HTTPException(status_code=403, detail="Usuário sem permissão para esta ação")

        return current_user

    return _guard
