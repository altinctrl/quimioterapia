import enum
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator, Field
from pydantic.alias_generators import to_camel


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


class DetalhesInfusao(BaseModel):
    status_farmacia: Optional[str] = "pendente"
    tempo_estimado_preparo: Optional[int] = None
    horario_previsao_entrega: Optional[str] = None
    ciclo_atual: Optional[int] = None
    dia_ciclo: Optional[str] = None


class DetalhesProcedimento(BaseModel):
    tipo_procedimento: TipoProcedimento


class DetalhesConsulta(BaseModel):
    tipo_consulta: TipoConsulta


class DetalhesIntercorrencia(BaseModel):
    tipo_intercorrencia: TipoIntercorrencia
    medicamento_intercorrencia: str


class DetalhesSuspensao(BaseModel):
    motivo_suspensao: MotivoSuspensao
    medicamento_falta: Optional[str] = None


class DetalhesCancelamento(BaseModel):
    motivo_cancelamento: str


class DetalhesRemarcacao(BaseModel):
    motivo_remarcacao: str
    nova_data: date


class DetalhesInfusaoUpdate(BaseModel):
    status_farmacia: Optional[str] = None
    tempo_estimado_preparo: Optional[int] = None
    horario_previsao_entrega: Optional[str] = None
    ciclo_atual: Optional[int] = None
    dia_ciclo: Optional[str] = None


class DetalhesProcedimentoUpdate(BaseModel):
    tipo_procedimento: Optional[TipoProcedimento] = None


class DetalhesConsultaUpdate(BaseModel):
    tipo_consulta: Optional[TipoConsulta] = None


class DetalhesAgendamento(BaseModel):
    infusao: Optional[DetalhesInfusao] = None
    procedimento: Optional[DetalhesProcedimento] = None
    consulta: Optional[DetalhesConsulta] = None
    suspensao: Optional[DetalhesSuspensao] = None
    intercorrencia: Optional[DetalhesIntercorrencia] = None
    cancelamento: Optional[DetalhesCancelamento] = None
    remarcacao: Optional[DetalhesRemarcacao] = None

    model_config = ConfigDict(extra='ignore', populate_by_name=True)


class DetalhesAgendamentoUpdate(BaseModel):
    infusao: Optional[DetalhesInfusaoUpdate] = None
    procedimento: Optional[DetalhesProcedimentoUpdate] = None
    consulta: Optional[DetalhesConsultaUpdate] = None
    suspensao: Optional[DetalhesSuspensao] = None
    intercorrencia: Optional[DetalhesIntercorrencia] = None
    cancelamento: Optional[DetalhesCancelamento] = None
    remarcacao: Optional[DetalhesRemarcacao] = None

    model_config = ConfigDict(extra='ignore', populate_by_name=True)


class AgendamentoBase(BaseModel):
    paciente_id: str
    tipo: TipoAgendamento
    data: date
    turno: str
    horario_inicio: str
    horario_fim: str
    status: str
    encaixe: bool = False
    observacoes: Optional[str] = None
    tags: Optional[List[str]] = []
    detalhes: DetalhesAgendamento = Field(default_factory=DetalhesAgendamento)

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


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


class AgendamentoUpdate(BaseModel):
    data: Optional[date] = None
    turno: Optional[str] = None
    horario_inicio: Optional[str] = None
    horario_fim: Optional[str] = None
    status: Optional[str] = None
    encaixe: Optional[bool] = None
    observacoes: Optional[str] = None
    tags: Optional[List[str]] = None
    detalhes: Optional[DetalhesAgendamentoUpdate] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class AgendamentoPaciente(BaseModel):
    id: str
    nome: str
    registro: str
    observacoes_clinicas: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)


class AgendamentoResponse(AgendamentoBase):
    id: str
    paciente: Optional[AgendamentoPaciente] = None

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
