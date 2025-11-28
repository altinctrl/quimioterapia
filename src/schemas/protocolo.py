from pydantic import BaseModel
from typing import Optional

class ProtocoloBase(BaseModel):
    nome: str
    duracao: int
    frequencia: str
    restricoes: Optional[str] = None

class ProtocoloCreate(ProtocoloBase):
    pass

class ProtocoloResponse(ProtocoloBase):
    id: int

    class Config:
        from_attributes = True