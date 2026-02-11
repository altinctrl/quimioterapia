import {Agendamento, AgendamentoStatusEnum, DetalhesInfusao, GrupoInfusao} from "@/types/typesAgendamento.ts";
import {
  LABELS_CONSULTA,
  LABELS_GRUPO_INFUSAO,
  LABELS_PROCEDIMENTO,
  LIMITE_LONGO_MINUTOS,
  LIMITE_MEDIO_MINUTOS,
  LIMITE_RAPIDO_MINUTOS,
  STATUS_INFUSAO_PRE_CHECKIN,
  STATUS_GERAL_POS_CHECKIN,
  STATUS_GERAL_PRE_CHECKIN,
  CORES_GRUPOS_INFUSAO,
  ESTILOS_BADGE_GRUPOS_INFUSAO,
} from "@/constants/constAgenda.ts";
import {computed} from "vue";
import {useAppStore} from '@/stores/storeGeral.ts'

export function somarMinutosAoHorario(horario: string, minutos: number): string {
  if (!horario) return ''
  const [h, m] = horario.split(':').map(Number)
  const dataBase = new Date()
  dataBase.setHours(h, m, 0, 0)
  dataBase.setMinutes(dataBase.getMinutes() + minutos)
  const hFinal = String(dataBase.getHours()).padStart(2, '0')
  const mFinal = String(dataBase.getMinutes()).padStart(2, '0')
  return `${hFinal}:${mFinal}`
}

export function calcularDuracaoMinutos(inicio: string, fim: string): number {
  if (!inicio || !fim) return 0
  const [h1, m1] = inicio.split(':').map(Number)
  const [h2, m2] = fim.split(':').map(Number)
  return (h2 * 60 + m2) - (h1 * 60 + m1)
}

export function formatarDuracao(minutos: number): string {
  if (minutos <= 0) return '-'
  const h = Math.floor(minutos / 60)
  const m = minutos % 60
  if (h > 0 && m > 0) return `${h}h ${m}m`
  if (h > 0) return `${h}h`
  return `${m}m`
}

export function getDuracaoAgendamento(ag: Agendamento): number {
  return calcularDuracaoMinutos(ag.horarioInicio, ag.horarioFim)
}

export function getGrupoInfusao(minutos: number): GrupoInfusao {
  if (minutos <= 0) return 'indefinido'
  if (minutos <= LIMITE_RAPIDO_MINUTOS) return 'rapido'
  if (minutos <= LIMITE_MEDIO_MINUTOS) return 'medio'
  if (minutos <= LIMITE_LONGO_MINUTOS) return 'longo'
  return 'extra_longo'
}

export function getCorGrupo(grupo: GrupoInfusao): string {
  return CORES_GRUPOS_INFUSAO[grupo] || CORES_GRUPOS_INFUSAO.indefinido;
}

export function getBadgeGrupo(grupo: GrupoInfusao): string {
  return ESTILOS_BADGE_GRUPOS_INFUSAO[grupo] || ESTILOS_BADGE_GRUPOS_INFUSAO.indefinido;
}

export const somarDias = (dataStr: string, dias: number): string => {
  const [y, m, d] = dataStr.split('-').map(Number)
  const date = new Date(y, m - 1, d) // Construtor local
  date.setDate(date.getDate() + dias)

  const ano = date.getFullYear()
  const mes = String(date.getMonth() + 1).padStart(2, '0')
  const dia = String(date.getDate()).padStart(2, '0')
  return `${ano}-${mes}-${dia}`
}

export const getPaciente = (id: string) => {
  const appStore = useAppStore()
  appStore.getPacienteById(id)
}

const opcoesStatusPaciente = computed(() => {
  const appStore = useAppStore()
  return appStore.statusConfig.filter(s => s.tipo === 'paciente')
})

export const formatarConsulta = (tipo: string | undefined) => {
  if (!tipo) return "-"
  return LABELS_CONSULTA.find(opt => opt.value === tipo)?.label || tipo
}

export const formatarProcedimento = (tipo: string | undefined) => {
  if (!tipo) return "-"
  return LABELS_PROCEDIMENTO.find(opt => opt.value === tipo)?.label || tipo
}

export const getOpcoesStatus = (ag: Agendamento) => {
  if (ag.tipo == 'infusao') {
    if (ag.checkin) return opcoesStatusPaciente.value
    return opcoesStatusPaciente.value.filter(op => STATUS_INFUSAO_PRE_CHECKIN.includes(op.id as AgendamentoStatusEnum))
  }
  if (ag.checkin) return opcoesStatusPaciente.value.filter(op => STATUS_GERAL_POS_CHECKIN.includes(op.id as AgendamentoStatusEnum))
  return opcoesStatusPaciente.value.filter(op => STATUS_GERAL_PRE_CHECKIN.includes(op.id as AgendamentoStatusEnum))
}

export const getStatusDotColor = (statusId: string) => {
  const appStore = useAppStore()
  const config = appStore.getStatusConfig(statusId)
  return config.cor.split(' ')[0]
}

export const getAgendamentoInfo = (ag: Agendamento) => {
  const duracaoMin = getDuracaoAgendamento(ag)
  const grupo = getGrupoInfusao(duracaoMin)
  return {
    duracaoTexto: formatarDuracao(duracaoMin),
    corBorda: getCorGrupo(grupo),
    corBadge: getBadgeGrupo(grupo),
    grupoLabel: LABELS_GRUPO_INFUSAO[grupo]
  }
}

export const getObservacoesClinicas = (ag: Agendamento) => {
  return ag.paciente?.observacoesClinicas
}

export const getFarmaciaStatusConfig = (statusId: string | undefined) => {
  const appStore = useAppStore()
  const id = statusId || 'pendente'
  return appStore.statusConfig.find(s => s.id === id && s.tipo === 'farmacia') || {
    label: '-',
    corBadge: 'bg-gray-100 hover:bg-gray-100 text-gray-800 border-gray-200'
  }
}

export function isInfusao(ag: Partial<Agendamento>): ag is Agendamento & { detalhes: { infusao: DetalhesInfusao } } {
  return !!ag.detalhes?.infusao;
}

export function isProcedimento(ag: Partial<Agendamento>): ag is Agendamento & { detalhes: { procedimento: any } } {
  return !!ag.detalhes?.procedimento;
}

export function isConsulta(ag: Partial<Agendamento>): ag is Agendamento & { detalhes: { consulta: any } } {
  return !!ag.detalhes?.consulta;
}
