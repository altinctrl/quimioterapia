import {defineStore} from 'pinia'
import {ref} from 'vue'
import type {TipoAgendamento} from '@/types'

type TipoAgendamentoCapacidade = Exclude<TipoAgendamento, 'infusao'>

type VagasPorTipo = Record<TipoAgendamentoCapacidade, number>

const STORAGE_KEY = 'quimioterapia.config.vagasPorTipo'

const defaultVagasPorTipo: VagasPorTipo = {
  consulta: 4,
  procedimento: 4
}

function safeParse(json: string | null): unknown {
  if (!json) return null
  try {
    return JSON.parse(json)
  } catch {
    return null
  }
}

function sanitize(payload: unknown): VagasPorTipo {
  if (!payload || typeof payload !== 'object') return {...defaultVagasPorTipo}

  const p = payload as Partial<Record<string, unknown>>

  const consulta = Number(p.consulta)
  const procedimento = Number(p.procedimento)

  return {
    consulta: Number.isFinite(consulta) && consulta >= 0 ? consulta : defaultVagasPorTipo.consulta,
    procedimento: Number.isFinite(procedimento) && procedimento >= 0 ? procedimento : defaultVagasPorTipo.procedimento
  }
}

export const useConfiguracaoLocalStore = defineStore('configuracaoLocal', () => {
  const vagasPorTipo = ref<VagasPorTipo>({...defaultVagasPorTipo})

  function hydrate() {
    if (typeof window === 'undefined') return
    const parsed = safeParse(window.localStorage.getItem(STORAGE_KEY))
    vagasPorTipo.value = sanitize(parsed)
  }

  function persist() {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(vagasPorTipo.value))
  }

  function setVaga(tipo: TipoAgendamentoCapacidade, vagas: number) {
    vagasPorTipo.value = {
      ...vagasPorTipo.value,
      [tipo]: Number.isFinite(vagas) && vagas >= 0 ? vagas : 0
    }
    persist()
  }

  function getLimite(tipo: TipoAgendamentoCapacidade) {
    return vagasPorTipo.value[tipo] ?? 0
  }

  hydrate()

  return {
    vagasPorTipo,
    setVaga,
    getLimite,
    hydrate
  }
})
