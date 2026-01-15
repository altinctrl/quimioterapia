import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import type {Agendamento, StatusFarmacia, StatusPaciente} from '@/types'

export const useAgendamentoStore = defineStore('agendamento', () => {
  const agendamentos = ref<Agendamento[]>([])

  function getAgendamentosDoDia(data: string) {
    return agendamentos.value.filter(a => a.data === data)
  }

  async function fetchAgendamentos(inicio?: string, fim?: string, pacienteId?: string) {
    try {
      const params: any = {}
      if (inicio) params.data_inicio = inicio
      if (fim) params.data_fim = fim
      if (pacienteId) params.paciente_id = pacienteId

      const res = await api.get('/api/agendamentos', {params})

      if (pacienteId) {
        return res.data;
      } else {
        agendamentos.value = res.data;
      }

    } catch (e) {
      console.error(e)
    }
  }

  async function adicionarAgendamento(agendamento: any) {
    try {
      const res = await api.post('/api/agendamentos', agendamento)
      agendamentos.value.push(res.data)
      return res.data
    } catch (e) {
      toast.error("Erro ao criar agendamento")
      throw e
    }
  }

  async function atualizarCheckin(id: string, checkin: boolean) {
    try {
      const res = await api.put(`/api/agendamentos/${id}`, {checkin})

      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) {
        const prescricaoAntiga = agendamentos.value[idx].prescricao
        agendamentos.value[idx] = {...res.data, prescricao: prescricaoAntiga}
      }
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || "Erro ao atualizar check-in"
      toast.error(errorMsg)
    }
  }

  async function atualizarStatusAgendamento(
    id: string,
    status: StatusPaciente,
    detalhes?: any
  ) {
    try {
      const payload: any = {status}
      if (detalhes) payload.detalhes = detalhes

      const res = await api.put(`/api/agendamentos/${id}`, payload)

      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data

      toast.success(`Status atualizado para: ${status}`)
    } catch (e) {
      toast.error("Erro ao atualizar status")
    }
  }

  async function atualizarStatusFarmacia(id: string, status: StatusFarmacia) {
    try {
      const payload = {detalhes: {infusao: {status_farmacia: status}}}
      const res = await api.put(`/api/agendamentos/${id}`, payload)
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) {
        const prescricaoAntiga = agendamentos.value[idx].prescricao
        agendamentos.value[idx] = {...res.data, prescricao: prescricaoAntiga}
      }
    } catch (e) {
      toast.error("Erro na atualização")
    }
  }

  async function atualizarHorarioPrevisao(id: string, horario: string) {
    try {
      const payload = {detalhes: {infusao: {horario_previsao_entrega: horario}}}
      const res = await api.put(`/api/agendamentos/${id}`, payload)
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data
    } catch (e) {
      toast.error("Erro ao atualizar horário")
    }
  }

  async function remarcarAgendamento(idOriginal: string, novaData: string, novoHorario: string, motivo: string) {
    try {
      const detalhesPayload = {
        remarcacao: {
          motivo_remarcacao: motivo,
          nova_data: novaData
        }
      }

      await atualizarStatusAgendamento(idOriginal, 'remarcado', detalhesPayload)

      const original = agendamentos.value.find(a => a.id === idOriginal)
      if (!original) return

      const detalhesInfusaoOriginal = original.detalhes?.infusao

      const novoAgendamento = {
        pacienteId: original.pacienteId,
        tipo: original.tipo || 'infusao',
        data: novaData,
        turno: parseInt(novoHorario.split(':')[0]) < 13 ? 'manha' : 'tarde',
        horarioInicio: novoHorario,
        horarioFim: original.horarioFim,
        status: 'agendado',
        encaixe: true,
        observacoes: `Remarcado de ${original.data}. Motivo: ${motivo}`,
        detalhes: {
          infusao: {
            status_farmacia: 'pendente',
            ciclo_atual: detalhesInfusaoOriginal?.ciclo_atual,
            dia_ciclo: detalhesInfusaoOriginal?.dia_ciclo
          }
        }
      }

      await adicionarAgendamento(novoAgendamento)
      toast.success("Agendamento remarcado")
    } catch (e) {
      toast.error("Erro ao remarcar")
    }
  }

  async function atualizarTagsAgendamento(id: string, tags: string[]) {
    try {
      const res = await api.put(`/api/agendamentos/${id}`, {tags})
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data
      toast.success("Tags atualizadas")
    } catch (e) {
      console.error(e)
      toast.error("Erro ao salvar tags")
      throw e
    }
  }

  async function salvarChecklistFarmacia(id: string, checklist: Record<string, boolean>) {
    try {
      const payload = {detalhes: {infusao: {checklist_farmacia: checklist}}}
      const res = await api.put(`/api/agendamentos/${id}`, payload)

      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) {
        const prescricaoAntiga = agendamentos.value[idx].prescricao
        agendamentos.value[idx] = {...res.data, prescricao: prescricaoAntiga}
      }

    } catch (e) {
      console.error("Erro ao salvar checklist", e)
      toast.error("Erro ao salvar checklist")
    }
  }

  return {
    agendamentos,
    getAgendamentosDoDia,
    fetchAgendamentos,
    adicionarAgendamento,
    atualizarCheckin,
    atualizarStatusAgendamento,
    atualizarStatusFarmacia,
    atualizarHorarioPrevisao,
    remarcarAgendamento,
    atualizarTagsAgendamento,
    salvarChecklistFarmacia
  }
})