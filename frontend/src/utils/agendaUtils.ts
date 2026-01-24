import {Agendamento} from '@/types';

export type GrupoInfusao = 'rapido' | 'medio' | 'longo' | 'extra_longo' | 'indefinido'

export const LIMITE_RAPIDO_MINUTOS = 30
export const LIMITE_MEDIO_MINUTOS = 120
export const LIMITE_LONGO_MINUTOS = 240

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
  switch (grupo) {
    case 'rapido': return 'bg-blue-500'
    case 'medio': return 'bg-emerald-500'
    case 'longo': return 'bg-amber-500'
    case 'extra_longo': return 'bg-rose-600'
    default: return 'bg-gray-200'
  }
}

export function getBadgeGrupo(grupo: GrupoInfusao): string {
  switch (grupo) {
    case 'rapido': return 'text-blue-700 bg-blue-50 border-blue-100'
    case 'medio': return 'text-emerald-700 bg-emerald-50 border-emerald-100'
    case 'longo': return 'text-amber-700 bg-amber-50 border-amber-100'
    case 'extra_longo': return 'text-rose-700 bg-rose-50 border-rose-100'
    default: return 'text-gray-500 bg-gray-50 border-gray-100'
  }
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
