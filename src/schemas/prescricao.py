from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from src.schemas.protocolo import CategoriaBlocoEnum, UnidadeDoseEnum, ViaAdministracaoEnum


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True
    )


class PrescricaoStatusEnum(str, Enum):
    PENDENTE = 'pendente'
    AGENDADA = 'agendada'
    EM_CURSO = 'em-curso'
    CONCLUIDA = 'concluida'
    SUSPENSA = 'suspensa'
    SUBSTITUIDA = 'substituida'
    CANCELADA = 'cancelada'


class MedicoSnapshot(BaseSchema):
    nome: str
    crm_uf: str


class PacienteSnapshot(BaseSchema):
    nome: str
    prontuario: str
    nascimento: Union[str, date]
    sexo: str
    peso: float
    altura: float
    sc: float
    creatinina: Optional[float] = None


class ProtocoloRef(BaseSchema):
    nome: str
    ciclo_atual: int


class ItemPrescricao(BaseSchema):
    id_item: str
    medicamento: str
    dose_referencia: str
    unidade: UnidadeDoseEnum
    dose_maxima: Optional[float] = None
    dose_teorica: Optional[float] = None
    percentual_ajuste: float = 100.0
    dose_final: float
    via: ViaAdministracaoEnum
    diluicao_final: Optional[str] = None  # TODO: Validar, obrigatório dependendo da via
    tempo_minutos: int
    dias_do_ciclo: List[int]
    notas_especificas: Optional[str] = None


class BlocoPrescricao(BaseSchema):
    ordem: int
    categoria: CategoriaBlocoEnum
    itens: List[ItemPrescricao]


class PrescricaoConteudo(BaseSchema):
    data_emissao: str
    paciente: PacienteSnapshot
    medico: MedicoSnapshot
    protocolo: ProtocoloRef
    blocos: List[BlocoPrescricao]
    observacoes: Optional[str] = None


class PrescricaoStatusHistoricoItem(BaseSchema):
    data: datetime
    usuario_id: Optional[str] = None
    usuario_nome: Optional[str] = None
    status_anterior: PrescricaoStatusEnum
    status_novo: PrescricaoStatusEnum
    motivo: Optional[str] = None


class PrescricaoHistoricoAgendamentoItem(BaseSchema):
    data: datetime
    agendamento_id: str
    status_agendamento: str
    usuario_id: Optional[str] = None
    usuario_nome: Optional[str] = None
    observacoes: Optional[str] = None


class PrescricaoCreate(BaseSchema):
    paciente_id: str
    medico_id: str
    protocolo: ProtocoloRef
    dados_paciente: PacienteSnapshot
    observacoes_clinicas: Optional[str] = None
    blocos: List[BlocoPrescricao]


class PrescricaoResponse(BaseSchema):
    id: str
    paciente_id: str
    medico_id: str
    data_emissao: datetime
    status: PrescricaoStatusEnum  # TODO: Permitir atualizar status no banco de dados
    conteudo: PrescricaoConteudo
    historico_status: List[PrescricaoStatusHistoricoItem] = []
    historico_agendamentos: List[PrescricaoHistoricoAgendamentoItem] = []
    prescricao_substituta_id: Optional[str] = None
    prescricao_original_id: Optional[str] = None


class PrescricaoStatusUpdate(BaseSchema):
    status: PrescricaoStatusEnum
    motivo: Optional[str] = None
    prescricao_substituta_id: Optional[str] = None
