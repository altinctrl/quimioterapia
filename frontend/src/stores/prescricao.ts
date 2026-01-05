import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import type {PrescricaoMedica} from '@/types'
import {useProtocoloStore} from './protocolo'

export const usePrescricaoStore = defineStore('prescricao', () => {
  const prescricoes = ref<PrescricaoMedica[]>([])

  const protocoloStore = useProtocoloStore()

  function getPrescricoesPorPaciente(pacienteId: string) {
    return prescricoes.value.filter(p => p.pacienteId === pacienteId)
  }

  function getProtocoloPeloHistorico(pacienteId: string) {
    const lista = prescricoes.value.filter(p => p.pacienteId === pacienteId)

    if (lista.length === 0) return null

    const ultima = lista.sort((a, b) =>
      new Date(b.dataPrescricao).getTime() - new Date(a.dataPrescricao).getTime()
    )[0]

    if (ultima.protocoloId) {
      const proto = protocoloStore.protocolos.find(p => p.id === ultima.protocoloId)
      if (proto) return proto
    }

    if (ultima.protocolo) {
      return {nome: ultima.protocolo} as any
    }

    return null
  }

  async function fetchPrescricoes(pacienteId: string) {
    try {
      const res = await api.get(`/api/prescricoes/paciente/${pacienteId}`)
      prescricoes.value = prescricoes.value.filter(p => p.pacienteId !== pacienteId).concat(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  async function adicionarPrescricao(prescricao: any) {
    try {
      const res = await api.post('/api/prescricoes', prescricao)
      prescricoes.value.push(res.data)
      return res.data
    } catch (e) {
      toast.error("Erro ao criar prescrição")
      throw e
    }
  }

  return {
    prescricoes,
    getPrescricoesPorPaciente,
    getProtocoloPeloHistorico,
    fetchPrescricoes,
    adicionarPrescricao
  }
})