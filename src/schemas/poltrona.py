from pydantic import BaseModel

class PoltronaBase(BaseModel):
    numero: int
    tipo: str
    disponivel: bool = True

class PoltronaCreate(PoltronaBase):
    pass

class PoltronaResponse(PoltronaBase):
    id: int

    class Config:
        from_attributes = True