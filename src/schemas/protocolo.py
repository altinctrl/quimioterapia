from enum import Enum
from typing import List, Optional, Union, Literal, Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class FaseEnum(str, Enum):
    NA = "NA"
    ADJUVANTE = "Adjuvante"
    NEOADJUVANTE = "Neoadjuvante"
    PALIATIVO = "Paliativo"
    CONTROLE = "Controle"
    CURATIVO = "Curativo"


class CategoriaBlocoEnum(str, Enum):
    PRE_MED = "pre_med"
    QT = "qt"
    POS_MED_HOSPITALAR = "pos_med_hospitalar"
    POS_MED_DOMICILIAR = "pos_med_domiciliar"


class UnidadeDoseEnum(str, Enum):
    MG = "mg"
    MG_M2 = "mg/m2"
    MG_KG = "mg/kg"
    MCG_KG = "mcg/kg"
    AUC = "AUC"
    UI = "UI"
    G = "g"


class ViaAdministracaoEnum(str, Enum):
    IV = "IV"
    VO = "VO"
    SC = "SC"
    IT = "IT"
    IM = "IM"


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True
    )


class ConfiguracaoDiluicao(BaseSchema):
    opcoes_permitidas: Optional[List[str]] = None
    selecionada: Optional[str] = None


class DetalhesMedicamento(BaseSchema):
    medicamento: str
    dose_referencia: float
    unidade: UnidadeDoseEnum
    dose_maxima: Optional[float] = None
    via: ViaAdministracaoEnum
    configuracao_diluicao: Optional[ConfiguracaoDiluicao] = None
    tempo_minutos: int
    dias_do_ciclo: List[int]
    notas_especificas: Optional[str] = None


class MedicamentoUnico(BaseSchema):
    tipo: Literal["medicamento_unico"] = "medicamento_unico"
    dados: DetalhesMedicamento


class GrupoAlternativas(BaseSchema):
    tipo: Literal["grupo_alternativas"] = "grupo_alternativas"
    label_grupo: str
    opcoes: List[DetalhesMedicamento]


ItemBloco = Union[MedicamentoUnico, GrupoAlternativas]


class BlocoMedicacao(BaseSchema):
    ordem: int
    categoria: CategoriaBlocoEnum
    itens: List[Annotated[ItemBloco, Field(discriminator='tipo')]]


class TemplateCiclo(BaseSchema):
    id_template: str
    aplicavel_aos_ciclos: Optional[str] = None
    blocos: List[BlocoMedicacao]


class ProtocoloBase(BaseSchema):
    nome: str
    total_ciclos: Optional[int] = None
    duracao_ciclo_dias: int = Field(..., ge=1)
    fase: Optional[FaseEnum] = None
    linha: Optional[int] = None
    indicacao: Optional[str] = None
    precaucoes: Optional[str] = None
    observacoes: Optional[str] = None
    tempo_total_minutos: int = None
    dias_semana_permitidos: Optional[List[int]] = None
    ativo: bool = True
    templates_ciclo: List[TemplateCiclo]


class ProtocoloCreate(ProtocoloBase):
    pass


class ProtocoloUpdate(BaseSchema):
    nome: Optional[str] = None
    total_ciclos: Optional[int] = None
    duracao_ciclo_dias: Optional[int] = None
    fase: Optional[FaseEnum] = None
    linha: Optional[int] = None
    indicacao: Optional[str] = None
    precaucoes: Optional[str] = None
    observacoes: Optional[str] = None
    tempo_total_minutos: Optional[int] = None
    dias_semana_permitidos: Optional[List[int]] = None
    ativo: Optional[bool] = None
    templates_ciclo: Optional[List[TemplateCiclo]] = None


class ProtocoloResponse(ProtocoloBase):
    id: str
    created_at: Optional[str] = None
