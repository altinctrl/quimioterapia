from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import date
from typing import Optional
from .enums import Turno, StatusPaciente, StatusFarmacia

class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class AgendamentoBase(CamelModel):
    paciente_id: int
    data: date
    turno: Turno
    horario_inicio: str
    horario_fim: str
    poltrona_id: int
    encaixe: bool = False


class AgendamentoCreate(AgendamentoBase):
    status: Optional[StatusPaciente] = StatusPaciente.agendado
    status_farmacia: Optional[StatusFarmacia] = StatusFarmacia.pendente


class AgendamentoUpdateStatus(CamelModel):
    status: StatusPaciente
    observacoes: Optional[str] = None


class AgendamentoResponse(AgendamentoBase):
    id: int
    status: StatusPaciente
    status_farmacia: StatusFarmacia
    hora_inicio_real: Optional[str] = None
    hora_fim_real: Optional[str] = None
    intercorrencias: Optional[str] = None