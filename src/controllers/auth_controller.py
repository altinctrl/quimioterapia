import os
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException

from src.auth.auth_handler import auth_handler
from src.providers.interfaces.auth_provider_interface import AuthProviderInterface
from src.schemas.auth_schema import LoginResponse, UserSchema, UserUpdate


async def processar_login_ldap(
        user_data: dict,
        provider: AuthProviderInterface
) -> LoginResponse:
    db_user = await provider.get_or_create_user(user_data)
    claims = {"sub": db_user.username}
    access_token = auth_handler.encode_token(db_user.username, claims=claims)
    refresh_token_exp_days = int(os.getenv("JWT_REFRESH_TOKEN_EXP_DAYS"))
    refresh_token_str = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(days=refresh_token_exp_days)

    await provider.salvar_refresh_token(
        token=refresh_token_str,
        username=db_user.username,
        expires_at=expires_at
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=UserSchema.model_validate(db_user)
    )


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
    user = stored_token.usuario

    claims = {"sub": user.username}
    new_access_token = auth_handler.encode_token(user.username, claims=claims)
    new_refresh_token = secrets.token_hex(32)
    new_expires_at = datetime.now() + timedelta(days=7)

    await provider.salvar_refresh_token(
        token=new_refresh_token,
        username=user.username,
        expires_at=new_expires_at
    )

    return LoginResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserSchema.model_validate(user)
    )


async def encerrar_sessao(refresh_token: str, provider: AuthProviderInterface):
    sucesso = await provider.revogar_refresh_token(refresh_token)
    if not sucesso: pass
    return {"status": "success", "message": "Logout realizado com sucesso"}


async def atualizar_perfil_usuario(
        username: str,
        dados: UserUpdate,
        provider: AuthProviderInterface
) -> UserSchema:
    user = await provider.atualizar_registro_usuario(
        username=username,
        registro=dados.registro_profissional,
        tipo_registro=dados.tipo_registro
    )

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return UserSchema.model_validate(user)
