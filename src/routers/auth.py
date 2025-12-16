from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.auth import auth_handler
from src.schemas.auth import LoginRequest, LoginResponse, UserSchema

router = APIRouter(prefix="/api", tags=["Autenticação"])

MOCK_USERS_DB = {
    "admin": {
        "pass": "admin",
        "display": "Administradora",
        "groups": ["Administradores"],
        "email": "admin@hc.gov.br"
    },
    "enfermeiro": {
        "pass": "enfermeiro123",
        "display": "Enfermeira",
        "groups": ["Enfermagem"],
        "email": "enf.maria@hc.gov.br"
    },
    "medico": {
        "pass": "medico123",
        "display": "Médica",
        "groups": ["Medicos"],
        "email": "dr.joao@hc.gov.br"
    },
    "farmacia": {
        "pass": "farmacia123",
        "display": "Farmacêutica",
        "groups": ["Farmacia"],
        "email": "ana.farmacia@hc.gov.br"
    }
}


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = MOCK_USERS_DB.get(form_data.username)

    if not user_data or user_data["pass"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )

    claims = {
        "sub": form_data.username,
        "username": form_data.username,
        "displayName": user_data["display"],
        "display_name": user_data["display"],
        "groups": user_data["groups"],
        "email": user_data["email"]
    }

    access_token = auth_handler.encode_token(form_data.username, claims=claims)

    return LoginResponse(
        access_token=access_token,
        user=UserSchema(
            username=form_data.username,
            email=user_data["email"],
            display_name=user_data["display"],
            groups=user_data["groups"]
        )
    )

@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: dict = Depends(auth_handler.get_current_user)):
    return current_user
