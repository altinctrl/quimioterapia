import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {
  BlocoPrescricao,
  PacienteSnapshot,
  PrescricaoMedica,
  PrescricaoStatusEnum,
  ProtocoloRef
} from "@/types/typesPrescricao.ts";

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

  const atualizarLocal = (prescricaoAtualizada: PrescricaoMedica) => {
    const idx = prescricoes.value.findIndex(p => p.id === prescricaoAtualizada.id)
    if (idx !== -1) {
      prescricoes.value[idx] = prescricaoAtualizada
    } else {
      prescricoes.value.push(prescricaoAtualizada)
    }
  }

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
      const pacienteId = (payload as any).paciente_id || (payload as any).pacienteId
      if (pacienteId) {
        await fetchPrescricoes(pacienteId)
      }
      return res.data as PrescricaoMedica
    } catch (e) {
      toast.error("Erro ao criar prescrição")
      throw e
    }
  }

  async function adicionarPrescricaoSubstituicao(
    payload: PayloadCriacaoPrescricao,
    prescricaoOriginalId: string,
    motivo?: string
  ) {
    try {
      const corpo: any = {
        ...payload,
        prescricao_original_id: prescricaoOriginalId
      }
      if (motivo) corpo.motivo = motivo

      const res = await api.post('/api/prescricoes/substituir', corpo)
      prescricoes.value.push(res.data as PrescricaoMedica)
      const pacienteId = (payload as any).paciente_id || (payload as any).pacienteId
      if (pacienteId) {
        await fetchPrescricoes(pacienteId)
      }
      return res.data as PrescricaoMedica
    } catch (e) {
      toast.error("Erro ao substituir prescrição")
      throw e
    }
  }

  async function baixarPrescricao(id: string) {
    toast.info('Gerando PDF...');
    try {
      const {data} = await api.get(`/api/prescricoes/${id}/pdf`, {responseType: 'blob'});
      const url = window.URL.createObjectURL(data);
      const link = document.createElement('a');
      link.href = url;
      link.download = `prescricao_${id}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      toast.error("Erro ao gerar PDF.");
      console.error(e);
    }
  }

  async function alterarStatusPrescricao(id: string, status: PrescricaoStatusEnum, motivo?: string) {
    try {
      const payload: any = {status}
      if (motivo) payload.motivo = motivo

      const res = await api.put(`/api/prescricoes/${id}/status`, payload)
      atualizarLocal(res.data as PrescricaoMedica)
      toast.success("Status da prescrição atualizado")
      return res.data as PrescricaoMedica
    } catch (e) {
      toast.error("Erro ao atualizar status da prescrição")
      throw e
    }
  }

  async function substituirPrescricao(id: string, prescricaoSubstitutaId: string, motivo?: string) {
    try {
      const payload: any = {
        status: PrescricaoStatusEnum.SUBSTITUIDA,
        prescricao_substituta_id: prescricaoSubstitutaId
      }
      if (motivo) payload.motivo = motivo

      const res = await api.put(`/api/prescricoes/${id}/status`, payload)
      atualizarLocal(res.data as PrescricaoMedica)
      toast.success("Prescrição substituída")
      return res.data as PrescricaoMedica
    } catch (e) {
      toast.error("Erro ao substituir prescrição")
      throw e
    }
  }

  return {
    prescricoes,
    getPrescricoesPorPaciente,
    fetchPrescricoes,
    adicionarPrescricao,
    adicionarPrescricaoSubstituicao,
    baixarPrescricao,
    alterarStatusPrescricao,
    substituirPrescricao
  }
})
