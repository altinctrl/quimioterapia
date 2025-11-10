import os
import jwt
import ldap
import re
import secrets
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..resources.database import get_app_db_session
from ..models.refresh_token import RefreshToken

load_dotenv()

# --- Configurações --- 
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 24))
REFRESH_TOKEN_EXP_DAYS = int(os.getenv("REFRESH_TOKEN_EXP_DAYS", 30))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# --- Interface e Implementações de Provedor de Autenticação ---

class AuthProviderInterface(ABC):
    """Interface para provedores de autenticação."""
    @abstractmethod
    def authenticate_user(self, username, password) -> dict:
        pass

class MockAuthProvider(AuthProviderInterface):
    """Provedor de autenticação mock para desenvolvimento offline."""
    def authenticate_user(self, username, password) -> dict:
        print("--- Using Mock Authentication ---")
        if username == "admin" and password == "admin":
            print(f"Authentication successful for mock user: {username}")
            # O nome do grupo que o frontend usa para identificar administradores
            admin_group = "GLO-SEC-HCPE-SETISD"
            return {
                "username": "admin",
                "displayName": ["Mock Admin"],
                "groups": [admin_group, "Users"],
                "email": "admin@mock.com"
            }
        else:
            print(f"Authentication failed for mock user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid mock credentials"
            )

class ActiveDirectoryAuthProvider(AuthProviderInterface):
    """Provedor de autenticação real usando LDAP/Active Directory."""
    def __init__(self):
        self.ad_url = os.getenv("AD_URL")
        self.ad_basedn = os.getenv("AD_BASEDN")
        self.ad_bind_user = os.getenv("AD_BIND_USER")
        self.ad_bind_password = os.getenv("AD_BIND_PASSWORD")
        if not self.ad_url or not self.ad_basedn:
            raise RuntimeError("Active Directory is not configured. Check .env file.")

    def authenticate_user(self, username, password) -> dict:
        print(f"--- Starting AD Authentication for user: {username} ---")
        l = None
        try:
            l = ldap.initialize(self.ad_url)
            l.protocol_version = ldap.VERSION3
            l.set_option(ldap.OPT_REFERRALS, 0)

            user_bind_dn = f"EBSERHNET\\{username}"
            l.simple_bind_s(user_bind_dn, password)

            groups = []
            search_ldap_conn = l
            if self.ad_bind_user and self.ad_bind_password:
                search_ldap_conn = ldap.initialize(self.ad_url)
                search_ldap_conn.protocol_version = ldap.VERSION3
                search_ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
                search_ldap_conn.simple_bind_s(self.ad_bind_user, self.ad_bind_password)

            search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
            result_id = search_ldap_conn.search(self.ad_basedn, ldap.SCOPE_SUBTREE, search_filter, ["*"])
            result_type, result_data = search_ldap_conn.result(result_id, 1)

            user_info = {"username": username}
            if result_data and result_data[0][1]:
                user_entry = result_data[0][1]
                for key, value in user_entry.items():
                    if key == 'memberOf':
                        groups = [re.match(r'CN=([^,]+)', group_dn.decode('utf-8')).group(1) for group_dn in value if re.match(r'CN=([^,]+)', group_dn.decode('utf-8'))]
                        user_info['groups'] = groups
                    else:
                        user_info[key] = [i.decode('utf-8', 'ignore') for i in value] if isinstance(value, list) else value.decode('utf-8', 'ignore')

            if search_ldap_conn != l:
                search_ldap_conn.unbind_s()
            
            print(f"--- AD Authentication successful for user: {username}. ---")
            return user_info

        except ldap.INVALID_CREDENTIALS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        except ldap.SERVER_DOWN:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AD server is down or unreachable")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AD error: {e}")
        finally:
            if l:
                l.unbind_s()

# --- AuthHandler Principal ---

class AuthHandler:
    def __init__(self):
        # Lógica de troca: decide qual provedor usar na inicialização
        if os.getenv("AD_URL"):
            print("INFO: Using Active Directory authentication.")
            self.provider: AuthProviderInterface = ActiveDirectoryAuthProvider()
        else:
            print("WARNING: AD environment variables not found. Using Mock authentication.")
            self.provider: AuthProviderInterface = MockAuthProvider()

    def authenticate_user(self, username, password):
        return self.provider.authenticate_user(username, password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if 'username' in to_encode:
            to_encode['sub'] = to_encode['username']
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=JWT_EXP_HOURS))
        to_encode.update({"exp": expire})
        if not JWT_SECRET:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT_SECRET not configured")
        return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

    async def create_refresh_token(self, user_id: str, groups: list, db: AsyncSession) -> str:
        refresh_token_string = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXP_DAYS)
        new_refresh_token = RefreshToken(user_id=user_id, token=refresh_token_string, groups=groups, expires_at=expires_at)
        db.add(new_refresh_token)
        await db.commit()
        return refresh_token_string

    async def verify_refresh_token(self, refresh_token: str, db: AsyncSession):
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token)
        result = await db.execute(stmt)
        token_obj = result.scalar_one_or_none()
        if not token_obj or token_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        return token_obj

    async def invalidate_refresh_token(self, refresh_token: str, db: AsyncSession):
        stmt = delete(RefreshToken).where(RefreshToken.token == refresh_token)
        await db.execute(stmt)
        await db.commit()

    def decode_token(self, token: str = Depends(oauth2_scheme)):
        try:
            if not JWT_SECRET:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT_SECRET not configured")
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Instância única que será usada em toda a aplicação
auth_handler = AuthHandler()