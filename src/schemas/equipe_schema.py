import enum
from datetime import date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.schemas.auth_schema import UserSchema


class CargoEnum(str, enum.Enum):
    ENFERMEIRO = "Enfermeiro"
    TECNICO = "Técnico de Enfermagem"


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
    cargo: str
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
    usuario: Optional[UserSchema] = Field(default=None, exclude=True)
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    def nome(self) -> str:
        if self.usuario:
            return self.usuario.display_name or self.usuario.username
        return self.username

    @computed_field
    def registro(self) -> Optional[str]:
        if self.usuario:
            return self.usuario.registro_profissional
        return None


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
