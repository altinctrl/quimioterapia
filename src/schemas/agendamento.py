import enum
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator, Field
from pydantic.alias_generators import to_camel

from src.schemas.equipe import ProfissionalResponse
from src.schemas.prescricao import PrescricaoResponse


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True
    )


class AgendamentoStatusEnum(str, enum.Enum):
    AGENDADO = 'agendado'
    AGUARDANDO_CONSULTA = 'aguardando-consulta'
    AGUARDANDO_EXAME = 'aguardando-exame'
    AGUARDANDO_MEDICAMENTO = 'aguardando-medicamento'
    INTERNADO = 'internado'
    SUSPENSO = 'suspenso'
    REMARCADO = 'remarcado'
    EM_TRIAGEM = 'em-triagem'
    EM_INFUSAO = 'em-infusao'
    INTERCORRENCIA = 'intercorrencia'
    CONCLUIDO = 'concluido'


class FarmaciaStatusEnum(str, enum.Enum):
    PENDENTE = 'pendente'
    EM_PREPARACAO = 'em-preparacao'
    PRONTO = 'pronto'
    ENVIADO = 'enviado'
    AGUARDA_PRESCRICAO = 'aguarda-prescricao' # Não recebido
    VALIDANDO_PRESCRICAO = 'validando-prescricao' # Aguarda confirmação dos dados da prescrição
    MED_EM_FALTA = 'med-em-falta'
    MED_JUD_EM_FALTA = 'med-jud-em-falta'
    SEM_PROCESSO = 'sem-processo'
    PRESCRICAO_DEVOLVIDA = 'prescricao-devolvida' # Devolvido


class TipoAgendamento(str, enum.Enum):
    INFUSAO = "infusao"
    PROCEDIMENTO = "procedimento"
    CONSULTA = "consulta"


class TipoProcedimento(str, enum.Enum):
    RETIRADA_INFUSOR = "retirada_infusor"
    PARACENTESE_ALIVIO = "paracentese_alivio"
    MANUTENCAO_CTI = "manutencao_cti"
    RETIRADA_PONTOS = "retirada_pontos"
    TROCA_BOLSA = "troca_bolsa"
    CURATIVO = "curativo"
    MEDICACAO = "medicacao"


class TipoConsulta(str, enum.Enum):
    TRIAGEM = "triagem"
    NAVEGACAO = "navegacao"


class MotivoSuspensao(str, enum.Enum):
    CLINICA = "alteracoes_clinicas"
    PROTOCOLO = "mudanca_protocolo"
    FALTA_MEDICACAO = "medicacao_falta"
    LABORATORIAL = "alteracoes_laboratoriais"
    OBITO = "obito"
    ADMINISTRATIVO = "sem_processo"


class TipoIntercorrencia(str, enum.Enum):
    HIPERSENSIBILIDADE = "hipersensibilidade"
    EXTRAVASAMENTO = "extravasamento"
    DERRAMAMENTO = "derramamento"


class DetalhesInfusao(BaseSchema):
    prescricao_id: str
    status_farmacia: Optional[FarmaciaStatusEnum] = FarmaciaStatusEnum.PENDENTE
    tempo_estimado_preparo: Optional[int] = None
    horario_previsao_entrega: Optional[str] = None
    ciclo_atual: int
    dia_ciclo: int
    itens_preparados: List[str] = []


class DetalhesProcedimento(BaseSchema):
    tipo_procedimento: TipoProcedimento


class DetalhesConsulta(BaseSchema):
    tipo_consulta: TipoConsulta


class DetalhesIntercorrencia(BaseSchema):
    tipo_intercorrencia: TipoIntercorrencia
    medicamento_intercorrencia: str
    vigihosp: Optional[bool] = None
    observacoes: Optional[str] = None


class DetalhesSuspensao(BaseSchema):
    motivo_suspensao: MotivoSuspensao
    medicamento_falta: Optional[str] = None
    observacoes: Optional[str] = None


class DetalhesCancelamento(BaseSchema):
    motivo_cancelamento: str


class DetalhesRemarcacao(BaseSchema):
    motivo_remarcacao: str
    nova_data: date


class DetalhesInfusaoUpdate(BaseSchema):
    status_farmacia: Optional[FarmaciaStatusEnum] = None
    tempo_estimado_preparo: Optional[int] = None
    horario_previsao_entrega: Optional[str] = None
    itens_preparados: Optional[List[str]] = None


class DetalhesProcedimentoUpdate(BaseSchema):
    tipo_procedimento: Optional[TipoProcedimento] = None


class DetalhesConsultaUpdate(BaseSchema):
    tipo_consulta: Optional[TipoConsulta] = None


class DetalhesAgendamento(BaseSchema):
    infusao: Optional[DetalhesInfusao] = None
    procedimento: Optional[DetalhesProcedimento] = None
    consulta: Optional[DetalhesConsulta] = None
    suspensao: Optional[DetalhesSuspensao] = None
    intercorrencia: Optional[DetalhesIntercorrencia] = None
    cancelamento: Optional[DetalhesCancelamento] = None
    remarcacao: Optional[DetalhesRemarcacao] = None


class DetalhesAgendamentoUpdate(BaseSchema):
    infusao: Optional[DetalhesInfusaoUpdate] = None
    procedimento: Optional[DetalhesProcedimentoUpdate] = None
    consulta: Optional[DetalhesConsultaUpdate] = None
    suspensao: Optional[DetalhesSuspensao] = None
    intercorrencia: Optional[DetalhesIntercorrencia] = None
    cancelamento: Optional[DetalhesCancelamento] = None
    remarcacao: Optional[DetalhesRemarcacao] = None


class AgendamentoBase(BaseSchema):
    paciente_id: str
    tipo: TipoAgendamento
    data: date
    turno: str
    horario_inicio: str
    horario_fim: str
    checkin: bool = False
    status: AgendamentoStatusEnum = AgendamentoStatusEnum.AGENDADO
    encaixe: bool = False
    observacoes: Optional[str] = None
    tags: Optional[List[str]] = []
    detalhes: DetalhesAgendamento = Field(default_factory=DetalhesAgendamento)


class AgendamentoCreate(AgendamentoBase):
    @model_validator(mode='after')
    def validar_detalhes_por_tipo(self):
        if self.tipo == TipoAgendamento.INFUSAO:
            if not self.detalhes.infusao: raise ValueError("Detalhes da infusão são obrigatórios.")
        elif self.tipo == TipoAgendamento.PROCEDIMENTO:
            if not self.detalhes.procedimento: raise ValueError("Detalhes do procedimento são obrigatórios.")
        elif self.tipo == TipoAgendamento.CONSULTA:
            if not self.detalhes.consulta: raise ValueError("Detalhes da consulta são obrigatórios.")
        return self


class AgendamentoUpdate(BaseSchema):
    data: Optional[date] = None
    turno: Optional[str] = None
    horario_inicio: Optional[str] = None
    horario_fim: Optional[str] = None
    checkin: Optional[bool] = None
    status: Optional[AgendamentoStatusEnum] = None
    encaixe: Optional[bool] = None
    observacoes: Optional[str] = None
    tags: Optional[List[str]] = None
    detalhes: Optional[DetalhesAgendamentoUpdate] = None


class AgendamentoPaciente(BaseSchema):
    id: str
    nome: str
    registro: str
    observacoes_clinicas: Optional[str] = None


class AgendamentoResponse(AgendamentoBase):
    id: str
    criado_por_id: Optional[str] = None
    criado_por: Optional[ProfissionalResponse] = None
    paciente: Optional[AgendamentoPaciente] = None
    prescricao: Optional[PrescricaoResponse] = None
