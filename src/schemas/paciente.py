from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ContatoEmergenciaBase(BaseModel):
    nome: str
    parentesco: str
    telefone: str

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ContatoEmergenciaCreate(ContatoEmergenciaBase):
    pass


class ContatoEmergenciaResponse(ContatoEmergenciaBase):
    id: int


class PacienteBase(BaseModel):
    nome: str
    cpf: str
    registro: str
    data_nascimento: date
    telefone: Optional[str] = None
    email: Optional[str] = None
    peso: Optional[float] = None
    altura: Optional[float] = None
    observacoes_clinicas: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class PacienteCreate(PacienteBase):
    contatos_emergencia: List[ContatoEmergenciaCreate] = []


class PacienteUpdate(BaseModel):
    telefone: Optional[str] = None
    email: Optional[str] = None
    peso: Optional[float] = None
    altura: Optional[float] = None
    observacoes_clinicas: Optional[str] = None
    contatos_emergencia: Optional[List[ContatoEmergenciaCreate]] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class PacienteResponse(PacienteBase):
    id: str
    contatos_emergencia: List[ContatoEmergenciaResponse] = []
    protocolo_ultima_prescricao: Optional[str] = None


class PacientePagination(BaseModel):
    items: List[PacienteResponse]
    total: int
    page: int
    size: int
    pages: int
