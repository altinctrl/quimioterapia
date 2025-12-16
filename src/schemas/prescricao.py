from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ItemPrescricaoBase(BaseModel):
    nome: str
    dose: Optional[str] = None
    unidade: Optional[str] = None
    via: Optional[str] = None
    tempo_infusao: Optional[int] = None
    veiculo: Optional[str] = None
    volume_veiculo: Optional[str] = None
    observacoes: Optional[str] = None
    ordem: int = 0

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ItemPrescricaoCreate(ItemPrescricaoBase):
    pass


class ItemPrescricaoResponse(ItemPrescricaoBase):
    id: int
    tipo: str

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class PrescricaoBase(BaseModel):
    paciente_id: str
    medico_nome: str
    protocolo_id: Optional[str] = None
    ciclo_atual: Optional[int] = None
    ciclos_total: Optional[int] = None
    peso: Optional[float] = None
    altura: Optional[float] = None
    superficie_corporea: Optional[float] = None
    diagnostico: Optional[str] = None
    status: str = "ativa"
    observacoes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class PrescricaoCreate(PrescricaoBase):
    medicamentos: List[ItemPrescricaoCreate] = []
    qt: List[ItemPrescricaoCreate] = []
    pos_medicacoes: List[ItemPrescricaoCreate] = []
    protocolo_nome_snapshot: str = None


class PrescricaoResponse(PrescricaoBase):
    id: str
    data_prescricao: date
    protocolo: Optional[str] = None
    medicamentos: List[ItemPrescricaoResponse] = []
    qt: List[ItemPrescricaoResponse] = []
    pos_medicacoes: List[ItemPrescricaoResponse] = []

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
