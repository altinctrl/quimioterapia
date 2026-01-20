import enum
from datetime import date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class CargoEnum(str, enum.Enum):
    ENFERMEIRO = "Enfermeiro"
    TECNICO = "Técnico de Enfermagem"
    FARMACEUTICO = "Farmacêutico"
    MEDICO = "Médico"
    ADMINISTRATIVO = "Administrativo"


class TurnoEnum(str, enum.Enum):
    MANHA = "Manhã"
    TARDE = "Tarde"
    INTEGRAL = "Integral"


class MotivoAusenciaEnum(str, enum.Enum):
    FOLGA = "Folga"
    LTS = "Licença Tratamento Saúde"
    BH = "Banco de Horas"
    FERIAS = "Férias"
    OUTRO = "Outro"


class ProfissionalBase(BaseModel):
    username: str
    nome: str
    cargo: str
    registro: Optional[str] = None
    ativo: bool = True


class ProfissionalCreate(ProfissionalBase):
    pass


class EscalaPlantaoBase(BaseModel):
    data: date
    profissional_id: str
    funcao: str
    turno: str


class EscalaPlantaoCreate(EscalaPlantaoBase):
    pass


class AusenciaProfissionalBase(BaseModel):
    profissional_id: str
    data_inicio: date
    data_fim: date
    motivo: str
    observacao: Optional[str] = None


class AusenciaProfissionalCreate(AusenciaProfissionalBase):
    pass


class ProfissionalResponse(ProfissionalBase):
    model_config = ConfigDict(from_attributes=True)


class AusenciaProfissionalResponse(AusenciaProfissionalBase):
    id: str
    profissional: Optional[ProfissionalResponse] = None

    model_config = ConfigDict(from_attributes=True)


class EscalaPlantaoResponse(EscalaPlantaoBase):
    id: str
    profissional: Optional[ProfissionalResponse] = None

    model_config = ConfigDict(from_attributes=True)


class EscalaDiariaResponse(BaseModel):
    data: date
    escalados: List[EscalaPlantaoResponse]
    ausencias: List[AusenciaProfissionalResponse]
