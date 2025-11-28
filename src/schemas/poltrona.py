from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class PoltronaBase(CamelModel):
    numero: int
    tipo: str
    disponivel: bool = True

class PoltronaCreate(PoltronaBase):
    pass

class PoltronaResponse(PoltronaBase):
    id: int