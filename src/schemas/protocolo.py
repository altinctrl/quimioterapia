from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ItemProtocoloBase(BaseModel):
    nome: str
    dose_padrao: Optional[str] = None
    unidade_padrao: Optional[str] = None
    via_padrao: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ItemProtocoloCreate(ItemProtocoloBase):
    pass


class ItemProtocoloResponse(ItemProtocoloBase):
    id: int
    tipo: str

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ProtocoloBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    indicacao: Optional[str] = None
    duracao: int
    frequencia: Optional[str] = None
    numero_ciclos: Optional[int] = None
    grupo_infusao: Optional[str] = None
    dias_semana_permitidos: Optional[List[int]] = None
    observacoes: Optional[str] = None
    precaucoes: Optional[str] = None
    ativo: bool = True

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ProtocoloCreate(ProtocoloBase):
    medicamentos: List[ItemProtocoloCreate] = []
    pre_medicacoes: List[ItemProtocoloCreate] = []
    pos_medicacoes: List[ItemProtocoloCreate] = []


class ProtocoloUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    indicacao: Optional[str] = None
    duracao: Optional[int] = None
    frequencia: Optional[str] = None
    numero_ciclos: Optional[int] = None
    grupo_infusao: Optional[str] = None
    dias_semana_permitidos: Optional[List[int]] = None
    observacoes: Optional[str] = None
    precaucoes: Optional[str] = None
    ativo: Optional[bool] = None
    medicamentos: Optional[List[ItemProtocoloCreate]] = None
    pre_medicacoes: Optional[List[ItemProtocoloCreate]] = None
    pos_medicacoes: Optional[List[ItemProtocoloCreate]] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ProtocoloResponse(ProtocoloBase):
    id: str
    medicamentos: List[ItemProtocoloResponse] = []
    pre_medicacoes: List[ItemProtocoloResponse] = []
    pos_medicacoes: List[ItemProtocoloResponse] = []
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
