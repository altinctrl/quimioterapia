import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException

from src.auth.auth import auth_handler
from src.providers.interfaces.auth_provider_interface import AuthProviderInterface
from src.schemas.auth import LoginResponse, UserSchema


async def renovar_token(
        old_refresh_token: str,
        provider: AuthProviderInterface
) -> LoginResponse:
    stored_token = await provider.buscar_refresh_token(old_refresh_token)

    if not stored_token:
        raise HTTPException(status_code=401, detail="Refresh token inválido.")

    if stored_token.expires_at < datetime.now():
        await provider.revogar_refresh_token(old_refresh_token)
        raise HTTPException(status_code=401, detail="Refresh token expirado.")

    await provider.revogar_refresh_token(old_refresh_token)

    new_access_token_claims = {
        "sub": stored_token.username,
        "username": stored_token.username,
        "email": stored_token.email,
        "display_name": stored_token.display_name,
        "groups": stored_token.groups,
        "role": stored_token.role,
    }
    new_access_token = auth_handler.encode_token(stored_token.username, claims=new_access_token_claims)

    new_refresh_token_str = secrets.token_hex(32)
    new_expires_at = datetime.now() + timedelta(days=7)

    await provider.salvar_refresh_token(
        token=new_refresh_token_str,
        username=stored_token.username,
        email=stored_token.email,
        display_name=stored_token.display_name,
        groups=stored_token.groups,
        role=stored_token.role,
        expires_at=new_expires_at
    )

    return LoginResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token_str,
        user=UserSchema(
            username=stored_token.username,
            email=stored_token.email,
            display_name=stored_token.display_name,
            groups=stored_token.groups,
            role=stored_token.role
        )
    )


async def encerrar_sessao(refresh_token: str, provider: AuthProviderInterface):
    sucesso = await provider.revogar_refresh_token(refresh_token)
    if not sucesso: pass
    return {"status": "success", "message": "Logout realizado com sucesso"}
