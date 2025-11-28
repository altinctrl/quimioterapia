from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from datetime import date
from typing import List, Optional
from .enums import ViaAdministracao


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


class Medicamento(CamelModel):
    id: Optional[str] = None
    nome: str
    dose: str
    unidade: str
    via: ViaAdministracao
    tempo_infusao: Optional[int] = None
    veiculo: Optional[str] = None
    volume_veiculo: Optional[str] = None
    observacoes: Optional[str] = None


class PrescricaoBase(CamelModel):
    paciente_id: int
    medico_nome: str
    medico_id: Optional[str] = None

    data_prescricao: date = Field(default_factory=date.today)

    peso: Optional[float] = None
    altura: Optional[float] = None
    superficie_corporea: Optional[float] = None
    diagnostico: Optional[str] = None

    protocolo: str
    numero_ciclo: int
    dia_ciclo: Optional[str] = None
    frequencia: Optional[str] = None
    observacoes_protocolo: Optional[str] = None

    pre_qt: List[Medicamento] = []
    qt: List[Medicamento] = []
    pos_qt: List[Medicamento] = []

    tempo_total_infusao: int

    assinado: bool = False
    data_assinatura: Optional[date] = None
    hora_assinatura: Optional[str] = None


class PrescricaoCreate(PrescricaoBase):
    pass


class PrescricaoResponse(PrescricaoBase):
    id: int