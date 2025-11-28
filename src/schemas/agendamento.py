from pydantic import BaseModel
from datetime import date
from typing import Optional
from .enums import Turno, StatusPaciente, StatusFarmacia


class AgendamentoBase(BaseModel):
    paciente_id: int
    data: date
    turno: Turno
    horario_inicio: str
    horario_fim: str
    poltrona_id: int
    encaixe: bool = False


class AgendamentoCreate(AgendamentoBase):
    pass


class AgendamentoUpdateStatus(BaseModel):
    status: StatusPaciente
    observacoes: Optional[str] = None


class AgendamentoResponse(AgendamentoBase):
    id: int
    status: StatusPaciente
    status_farmacia: StatusFarmacia
    hora_inicio_real: Optional[str] = None
    hora_fim_real: Optional[str] = None
    intercorrencias: Optional[str] = None

    class Config:
        from_attributes = True