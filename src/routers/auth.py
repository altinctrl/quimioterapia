import os
import secrets
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.auth import auth_handler
from src.controllers import auth_controller
from src.dependencies import get_auth_provider
from src.providers.interfaces.auth_provider_interface import AuthProviderInterface
from src.schemas.auth import LoginResponse, UserSchema, RefreshTokenRequest
from src.services.ldap_service import authenticate_ldap

router = APIRouter(prefix="/api", tags=["Autenticação"])
load_dotenv()

@router.post("/login", response_model=LoginResponse)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_provider: AuthProviderInterface = Depends(get_auth_provider)
):
    user_data = authenticate_ldap(form_data.username, form_data.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    claims = {
        "sub": user_data["username"],
        "username": user_data["username"],
        "display_name": user_data["display_name"],
        "groups": user_data["groups"],
        "role": user_data["role"],
        "email": user_data["email"]
    }
    access_token = auth_handler.encode_token(user_data["username"], claims=claims)

    refresh_token_str = secrets.token_hex(32)
    refresh_token_exp_days = int(os.getenv("JWT_REFRESH_TOKEN_EXP_DAYS"))
    expires_at = datetime.now() + timedelta(days=refresh_token_exp_days)

    await auth_provider.salvar_refresh_token(
        token=refresh_token_str,
        username=user_data["username"],
        email=user_data["email"],
        display_name=user_data["display_name"],
        groups=user_data["groups"],
        role=user_data["role"],
        expires_at=expires_at
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=UserSchema(
            username=user_data["username"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            groups=user_data["groups"],
            role=user_data["role"]
        )
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
        request: RefreshTokenRequest,
        auth_provider: AuthProviderInterface = Depends(get_auth_provider)
):
    return await auth_controller.renovar_token(request.refresh_token, auth_provider)


@router.post("/logout")
async def logout(
        request: RefreshTokenRequest,
        auth_provider: AuthProviderInterface = Depends(get_auth_provider)
):
    return await auth_controller.encerrar_sessao(request.refresh_token, auth_provider)


@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: dict = Depends(auth_handler.get_current_user)):
    return current_user
