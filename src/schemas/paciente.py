from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import date
from typing import Optional
from .protocolo import ProtocoloResponse

class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class PacienteBase(CamelModel):
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
    protocolo: Optional[str] = None