import {AgendamentoStatusEnum, TipoConsultaEnum, TipoProcedimentoEnum} from "@/types/typesAgendamento.ts";

export const statusInfusaoPermitidosSemCheckin = [
  'agendado',
  'aguardando-consulta',
  'aguardando-exame',
  'aguardando-medicamento',
  'internado',
  'suspenso',
  'remarcado'
]

export const statusOutrosPermitidosSemCheckin = [
  'agendado',
  'remarcado'
]

export const statusOutrosPermitidosComCheckin = [
  'agendado',
  'remarcado',
  'concluido'
]

export const statusPermitidosSemCheckin = [
  AgendamentoStatusEnum.AGENDADO,
  AgendamentoStatusEnum.AGUARDANDO_CONSULTA,
  AgendamentoStatusEnum.AGUARDANDO_EXAME,
  AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO,
  AgendamentoStatusEnum.INTERNADO,
  AgendamentoStatusEnum.SUSPENSO,
  AgendamentoStatusEnum.REMARCADO
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

export const MESES = [
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
