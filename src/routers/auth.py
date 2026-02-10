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
from src.schemas.auth import LoginResponse, UserSchema, RefreshTokenRequest, UserUpdate
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
    return await auth_controller.processar_login_ldap(user_data, auth_provider)


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


@router.patch("/users/me/registro", response_model=UserSchema)
async def atualizar_registro(
        payload: UserUpdate,
        current_user: dict = Depends(auth_handler.get_current_user),
        auth_provider: AuthProviderInterface = Depends(get_auth_provider)
):
    return await auth_controller.atualizar_perfil_usuario(
        username=current_user["username"],
        dados=payload,
        provider=auth_provider
    )
