from typing import List

from pydantic import BaseModel, Field, field_serializer


class LoginRequest(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    username: str
    email: str
    groups: List[str]

    display_name: str = Field(..., serialization_alias="displayName")

    class Config:
        populate_by_name = True

    @field_serializer('display_name')
    def serialize_display_name(self, display_name: str, _info):
        return [display_name]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema
