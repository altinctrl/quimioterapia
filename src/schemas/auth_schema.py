from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    username: str
    display_name: str
    email: Optional[str] = None
    groups: List[str] = []
    role: str
    registro_profissional: Optional[str] = None
    tipo_registro: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )


class UserUpdate(BaseModel):
    registro_profissional: Optional[str] = None
    tipo_registro: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserSchema
