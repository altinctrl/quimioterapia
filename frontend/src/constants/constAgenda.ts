import {AgendamentoStatusEnum, GrupoInfusao, TipoConsultaEnum, TipoProcedimentoEnum} from "@/types/typesAgendamento.ts";
import {LABELS_STATUS_AGENDAMENTO} from "@/constants/constStatus.ts";

export const LIMITE_RAPIDO_MINUTOS = 30
export const LIMITE_MEDIO_MINUTOS = 120
export const LIMITE_LONGO_MINUTOS = 240

export const DURACAO_CONSULTA_PADRAO = 30
export const DURACAO_PROCEDIMENTO_PADRAO = 60

export const DURACOES_CONSULTA: Record<string, number> = {
  [TipoConsultaEnum.TRIAGEM]: 40,
  [TipoConsultaEnum.NAVEGACAO]: 60
}

export const DURACOES_PROCEDIMENTO: Record<string, number> = {
  [TipoProcedimentoEnum.RETIRADA_INFUSOR]: 30,
  [TipoProcedimentoEnum.PARACENTESE_ALIVIO]: 60,
  [TipoProcedimentoEnum.MANUTENCAO_CTI]: 45,
  [TipoProcedimentoEnum.RETIRADA_PONTOS]: 10,
  [TipoProcedimentoEnum.TROCA_BOLSA]: 30,
  [TipoProcedimentoEnum.CURATIVO]: 20,
  [TipoProcedimentoEnum.MEDICACAO]: 10,
};

export const STATUS_GERAL_PRE_CHECKIN = [
  AgendamentoStatusEnum.AGENDADO,
  AgendamentoStatusEnum.REMARCADO
]

export const STATUS_GERAL_POS_CHECKIN = [
  ...STATUS_GERAL_PRE_CHECKIN,
  AgendamentoStatusEnum.CONCLUIDO
]

export const STATUS_INFUSAO_PRE_CHECKIN = [
  AgendamentoStatusEnum.AGENDADO,
  AgendamentoStatusEnum.AGUARDANDO_CONSULTA,
  AgendamentoStatusEnum.AGUARDANDO_EXAME,
  AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO,
  AgendamentoStatusEnum.INTERNADO,
  AgendamentoStatusEnum.SUSPENSO,
  AgendamentoStatusEnum.REMARCADO
]

export const LABELS_STATUS_LOTE_AGENDA = [
  {id: AgendamentoStatusEnum.AGENDADO,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.AGENDADO]},
  {id: AgendamentoStatusEnum.AGUARDANDO_CONSULTA,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.AGUARDANDO_CONSULTA]},
  {id: AgendamentoStatusEnum.AGUARDANDO_EXAME,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.AGUARDANDO_EXAME]},
  {id: AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO]},
  {id: AgendamentoStatusEnum.INTERNADO,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.INTERNADO]},
  {id: AgendamentoStatusEnum.EM_TRIAGEM,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.EM_TRIAGEM]},
  {id: AgendamentoStatusEnum.EM_INFUSAO,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.EM_INFUSAO]},
  {id: AgendamentoStatusEnum.CONCLUIDO,
    label: LABELS_STATUS_AGENDAMENTO[AgendamentoStatusEnum.CONCLUIDO]},
]

export const LABELS_PROCEDIMENTO = [
  {value: TipoProcedimentoEnum.RETIRADA_INFUSOR, label: 'Retirada de Infusor'},
  {value: TipoProcedimentoEnum.PARACENTESE_ALIVIO, label: 'Paracentese de Alívio'},
  {value: TipoProcedimentoEnum.MANUTENCAO_CTI, label: 'Manutenção CTI'},
  {value: TipoProcedimentoEnum.RETIRADA_PONTOS, label: 'Retirada de Pontos'},
  {value: TipoProcedimentoEnum.TROCA_BOLSA, label: 'Troca de Bolsa'},
  {value: TipoProcedimentoEnum.CURATIVO, label: 'Curativo'},
  {value: TipoProcedimentoEnum.MEDICACAO, label: 'Medicação'}
]

export const LABELS_CONSULTA = [
  {value: TipoConsultaEnum.TRIAGEM, label: 'Triagem'},
  {value: TipoConsultaEnum.NAVEGACAO, label: 'Navegação'}
]

export const LABELS_MESES = [
  {value: '1', label: 'Janeiro'},
  {value: '2', label: 'Fevereiro'},
  {value: '3', label: 'Março'},
  {value: '4', label: 'Abril'},
  {value: '5', label: 'Maio'},
  {value: '6', label: 'Junho'},
  {value: '7', label: 'Julho'},
  {value: '8', label: 'Agosto'},
  {value: '9', label: 'Setembro'},
  {value: '10', label: 'Outubro'},
  {value: '11', label: 'Novembro'},
  {value: '12', label: 'Dezembro'}
]

export const LABELS_GRUPO_INFUSAO: Record<GrupoInfusao, string> = {
  rapido: 'Rápida',
  medio: 'Média',
  longo: 'Longa',
  extra_longo: 'Extra Longa',
  indefinido: '-'
}

export const LABELS_MOTIVOS_SUSPENSAO = [
  {value: 'alteracoes_clinicas', label: 'Alterações clínicas'},
  {value: 'mudanca_protocolo', label: 'Mudança de protocolo'},
  {value: 'medicacao_falta', label: 'Medicação em falta'},
  {value: 'alteracoes_laboratoriais', label: 'Alterações laboratoriais'},
  {value: 'obito', label: 'Óbito'},
  {value: 'sem_processo', label: 'Sem processo para liberação de QTAN'}
]

export const LABELS_TIPOS_INTERCORRENCIA = [
  {value: 'hipersensibilidade', label: 'Reação de Hipersensibilidade'},
  {value: 'extravasamento', label: 'Extravasamento'},
  {value: 'derramamento', label: 'Derramamento Acidental de QT'}
]

export const OPCOES_MEDICAMENTOS_FALTA = [
  'Paclitaxel',
  'Carboplatina',
  'Docetaxel',
  '5FU',
  'Medicações judicializadas',
  'Outros'
]

export const CORES_GRUPOS_INFUSAO: Record<GrupoInfusao, string> = {
  rapido: 'bg-blue-500',
  medio: 'bg-emerald-500',
  longo: 'bg-amber-500',
  extra_longo: 'bg-rose-600',
  indefinido: 'bg-gray-200'
};

export const ESTILOS_BADGE_GRUPOS_INFUSAO: Record<GrupoInfusao, string> = {
  rapido: 'text-blue-700 bg-blue-50 border-blue-100',
  medio: 'text-emerald-700 bg-emerald-50 border-emerald-100',
  longo: 'text-amber-700 bg-amber-50 border-amber-100',
  extra_longo: 'text-rose-700 bg-rose-50 border-rose-100',
  indefinido: 'text-gray-500 bg-gray-50 border-gray-100'
};
