from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional

class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class ProtocoloBase(CamelModel):
    nome: str
    duracao: int
    frequencia: str
    restricoes: Optional[str] = None

class ProtocoloCreate(ProtocoloBase):
    pass

class ProtocoloResponse(ProtocoloBase):
    id: int