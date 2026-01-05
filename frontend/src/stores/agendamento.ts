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

  async function fetchAgendamentos(inicio?: string, fim?: string) {
    try {
      const params: any = {}
      if (inicio) params.data_inicio = inicio
      if (fim) params.data_fim = fim

      const res = await api.get('/api/agendamentos', {params})
      agendamentos.value = res.data
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

  async function atualizarStatusAgendamento(
    id: string,
    status: StatusPaciente,
    detalhes?: any
  ) {
    try {
      const payload: any = {status}
      if (detalhes) payload.detalhes = detalhes
      else payload.detalhes = null

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
      const res = await api.put(`/api/agendamentos/${id}`, {statusFarmacia: status})
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data
      toast.success("Status farmácia atualizado")
    } catch (e) {
      toast.error("Erro na atualização")
    }
  }

  async function atualizarHorarioPrevisao(id: string, horario: string) {
    try {
      const res = await api.put(`/api/agendamentos/${id}`, {horarioPrevisaoEntrega: horario})
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data
    } catch (e) {
      toast.error("Erro ao atualizar horário")
    }
  }

  async function remarcarAgendamento(idOriginal: string, novaData: string, novoHorario: string, motivo: string) {
    try {
      const detalhesPayload = {
        tipo: 'remarcacao', motivo: motivo, data_nova: novaData
      }

      await atualizarStatusAgendamento(idOriginal, 'remarcado', detalhesPayload)

      const original = agendamentos.value.find(a => a.id === idOriginal)
      if (!original) return

      await adicionarAgendamento({
        pacienteId: original.pacienteId,
        data: novaData,
        turno: parseInt(novoHorario.split(':')[0]) < 13 ? 'manha' : 'tarde',
        horarioInicio: novoHorario,
        horarioFim: original.horarioFim,
        status: 'agendado',
        statusFarmacia: 'pendente',
        encaixe: true,
        observacoes: `Remarcado de ${original.data}. Motivo: ${motivo}`,
        cicloAtual: original.cicloAtual,
        diaCiclo: original.diaCiclo
      })
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

  return {
    agendamentos,
    getAgendamentosDoDia,
    fetchAgendamentos,
    adicionarAgendamento,
    atualizarStatusAgendamento,
    atualizarStatusFarmacia,
    atualizarHorarioPrevisao,
    remarcarAgendamento,
    atualizarTagsAgendamento
  }
})