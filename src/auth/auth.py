import os
import time
from typing import Optional, Dict, Union

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()


class AuthHandler:
    security = HTTPBearer()
    secret = os.getenv("JWT_SECRET", "secret_key_dev")
    algorithm = "HS256"

    jwt_exp_hours = int(os.getenv("JWT_EXP_HOURS", 24))

    def encode_token(self, user_id: str, claims: Optional[Dict] = None) -> str:
        payload = {
            "sub": user_id,
            "exp": time.time() + (self.jwt_exp_hours * 3600),
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

    async def get_current_user(self, auth: HTTPAuthorizationCredentials = Security(security)):
        token = auth.credentials
        payload = self.decode_token(token)

        # Compatibilidade, deve ser resolvido depois:
        if "username" not in payload and "sub" in payload:
            payload["username"] = payload["sub"]
        if "display_name" not in payload:
            if "displayName" in payload:
                val = payload["displayName"]
                payload["display_name"] = val[0] if isinstance(val, list) and val else str(val)
            elif "name" in payload:
                payload["display_name"] = payload["name"]
            else:
                payload["display_name"] = payload.get("username", "Usuário")
        if "displayName" not in payload and "display_name" in payload:
            payload["displayName"] = payload["display_name"]
        if "groups" not in payload or payload["groups"] is None:
            payload["groups"] = []

        return payload


auth_handler = AuthHandler()
