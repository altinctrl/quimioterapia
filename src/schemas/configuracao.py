from typing import List, Dict

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class GrupoInfusaoConfig(BaseModel):
    vagas: int
    duracao: str

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ConfiguracaoBase(BaseModel):
    horario_abertura: str
    horario_fechamento: str
    dias_funcionamento: List[int]
    grupos_infusao: Dict[str, GrupoInfusaoConfig]
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class ConfiguracaoUpdate(ConfiguracaoBase):
    pass


class ConfiguracaoResponse(ConfiguracaoBase):
    id: int

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
