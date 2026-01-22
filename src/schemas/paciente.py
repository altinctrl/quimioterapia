from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True
    )


class ContatoEmergenciaBase(BaseSchema):
    nome: str
    parentesco: str
    telefone: str


class ContatoEmergenciaCreate(ContatoEmergenciaBase):
    pass


class ContatoEmergenciaResponse(ContatoEmergenciaBase):
    id: int


class PacienteBase(BaseSchema):
    nome: str
    cpf: str
    registro: str
    data_nascimento: date
    sexo: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    peso: Optional[float] = None
    altura: Optional[float] = None
    observacoes_clinicas: Optional[str] = None


class PacienteCreate(PacienteBase):
    contatos_emergencia: List[ContatoEmergenciaCreate] = []


class PacienteUpdate(BaseSchema):
    sexo: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    peso: Optional[float] = None
    altura: Optional[float] = None
    observacoes_clinicas: Optional[str] = None
    contatos_emergencia: Optional[List[ContatoEmergenciaCreate]] = None


class PacienteResponse(PacienteBase):
    id: str
    contatos_emergencia: List[ContatoEmergenciaResponse] = []
    protocolo_ultima_prescricao: Optional[str] = None


class PacienteImportResponse(BaseSchema):
    id: Optional[str] = None # None se existir no AGHU mas não existir no local
    nome: str
    cpf: str
    registro: str
    data_nascimento: date


class PacientePagination(BaseSchema):
    items: List[PacienteResponse]
    total: int
    page: int
    size: int
    pages: int
