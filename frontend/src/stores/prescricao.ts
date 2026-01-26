import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {BlocoPrescricao, PacienteSnapshot, PrescricaoMedica, ProtocoloRef} from "@/types/prescricaoTypes.ts";

interface PayloadCriacaoPrescricao {
  paciente_id: string;
  medico_id: string;
  protocolo: ProtocoloRef;
  dados_paciente: PacienteSnapshot;
  observacoes_clinicas?: string;
  blocos: BlocoPrescricao[];
}

export const usePrescricaoStore = defineStore('prescricao', () => {
  const prescricoes = ref<PrescricaoMedica[]>([])

  function getPrescricoesPorPaciente(pacienteId: string) {
    return prescricoes.value.filter(p => p.pacienteId === pacienteId)
  }

  async function fetchPrescricoes(pacienteId: string) {
    try {
      const res = await api.get(`/api/prescricoes/paciente/${pacienteId}`)
      prescricoes.value = prescricoes.value.filter(p => p.pacienteId !== pacienteId).concat(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  async function adicionarPrescricao(payload: PayloadCriacaoPrescricao) {
    try {
      const res = await api.post('/api/prescricoes', payload)
      prescricoes.value.push(res.data as PrescricaoMedica)
      return res.data as PrescricaoMedica
    } catch (e) {
      toast.error("Erro ao criar prescrição")
      throw e
    }
  }

  return {
    prescricoes,
    getPrescricoesPorPaciente,
    fetchPrescricoes,
    adicionarPrescricao
  }
})
