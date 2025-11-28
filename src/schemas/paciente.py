from pydantic import BaseModel
from datetime import date
from typing import Optional
from .protocolo import ProtocoloResponse

class PacienteBase(BaseModel):
    nome: str
    registro: str
    data_nascimento: date
    telefone: str
    protocolo_id: Optional[int] = None
    observacoes: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteResponse(PacienteBase):
    id: int
    protocolo: Optional[ProtocoloResponse] = None

    class Config:
        from_attributes = True