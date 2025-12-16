from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class AgendamentoBase(BaseModel):
    paciente_id: str
    data: date
    turno: str
    horario_inicio: str
    horario_fim: str
    status: str
    status_farmacia: str
    encaixe: bool = False
    observacoes: Optional[str] = None
    tags: Optional[List[str]] = []
    tempo_estimado_preparo: Optional[int] = None
    horario_previsao_entrega: Optional[str] = None
    ciclo_atual: Optional[int] = None
    dia_ciclo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class AgendamentoCreate(AgendamentoBase):
    pass


class AgendamentoUpdate(BaseModel):
    data: Optional[date] = None
    turno: Optional[str] = None
    horario_inicio: Optional[str] = None
    horario_fim: Optional[str] = None
    status: Optional[str] = None
    status_farmacia: Optional[str] = None
    encaixe: Optional[bool] = None
    observacoes: Optional[str] = None
    tags: Optional[List[str]] = None
    tempo_estimado_preparo: Optional[int] = None
    horario_previsao_entrega: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class AgendamentoPaciente(BaseModel):
    id: str
    nome: str
    registro: str

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class AgendamentoResponse(AgendamentoBase):
    id: str
    paciente: Optional[AgendamentoPaciente] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
