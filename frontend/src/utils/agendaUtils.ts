export type GrupoInfusao = 'curto' | 'medio' | 'longo' | 'indefinido'

export const LIMITE_CURTO_MINUTOS = 119
export const LIMITE_MEDIO_MINUTOS = 239

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

export function getGrupoInfusao(minutos: number): GrupoInfusao {
  if (minutos <= 0) return 'indefinido'
  if (minutos <= LIMITE_CURTO_MINUTOS) return 'curto'
  if (minutos <= LIMITE_MEDIO_MINUTOS) return 'medio'
  return 'longo'
}

export function getCorGrupo(grupo: GrupoInfusao): string {
  switch (grupo) {
    case 'curto': return 'bg-emerald-500'
    case 'medio': return 'bg-amber-500'
    case 'longo': return 'bg-rose-600'
    default: return 'bg-gray-200'
  }
}

export function getBadgeGrupo(grupo: GrupoInfusao): string {
  switch (grupo) {
    case 'curto': return 'text-emerald-700 bg-emerald-50 border-emerald-100'
    case 'medio': return 'text-amber-700 bg-amber-50 border-amber-100'
    case 'longo': return 'text-rose-700 bg-rose-50 border-rose-100'
    default: return 'text-gray-500 bg-gray-50 border-gray-100'
  }
}