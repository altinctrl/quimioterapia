from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from .enums import ViaAdministracao


class Medicamento(BaseModel):
    nome: str
    dose: str
    unidade: str
    via: ViaAdministracao
    tempo_infusao: Optional[int] = None
    veiculo: Optional[str] = None
    volume_veiculo: Optional[str] = None
    observacoes: Optional[str] = None


class PrescricaoBase(BaseModel):
    paciente_id: int
    medico_nome: str
    medico_id: Optional[str] = None

    data_prescricao: date

    peso: Optional[float] = None
    altura: Optional[float] = None
    superficie_corporea: Optional[float] = None
    diagnostico: Optional[str] = None

    protocolo_nome: str
    numero_ciclo: int
    dia_ciclo: Optional[str] = None
    frequencia: Optional[str] = None
    observacoes_protocolo: Optional[str] = None

    pre_qt: List[Medicamento] = []
    qt: List[Medicamento] = []
    pos_qt: List[Medicamento] = []

    tempo_total_infusao: int


class PrescricaoCreate(PrescricaoBase):
    pass


class PrescricaoAssinar(BaseModel):
    assinado: bool = True
    data_assinatura: date
    hora_assinatura: str


class PrescricaoResponse(PrescricaoBase):
    id: int
    assinado: bool
    data_assinatura: Optional[date] = None
    hora_assinatura: Optional[str] = None

    class Config:
        from_attributes = True