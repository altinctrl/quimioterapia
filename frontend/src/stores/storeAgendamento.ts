import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {Agendamento, AgendamentoStatusEnum, FarmaciaStatusEnum} from "@/types/typesAgendamento.ts";

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
      const dadosRetornados = res.data as Agendamento[]

      if (pacienteId) {
        const outros = agendamentos.value.filter(a => a.pacienteId !== pacienteId)
        agendamentos.value = [...outros, ...dadosRetornados]

        return dadosRetornados
      } else {
        agendamentos.value = dadosRetornados
      }

    } catch (e) {
      console.error(e)
      toast.error("Erro ao buscar agendamentos")
    }
  }

  async function adicionarAgendamento(agendamento: any) {
    try {
      const res = await api.post('/api/agendamentos', agendamento)
      agendamentos.value.push(res.data)
      return res.data as Agendamento
    } catch (e: any) {
      if (e.response?.status === 409) {
        toast.error(e.response.data.detail || "Conflito de agendamento")
      } else {
        toast.error("Erro ao criar agendamento")
      }
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
    } catch (e) {
      console.error(e)
      toast.error("Erro ao atualizar check-in")
    }
  }

  async function atualizarStatusAgendamento(
    id: string,
    status: AgendamentoStatusEnum,
    detalhes?: any
  ) {
    try {
      const payload: any = {status}
      if (detalhes) payload.detalhes = detalhes

      const res = await api.put(`/api/agendamentos/${id}`, payload)

      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) {
        const prescricaoAntiga = agendamentos.value[idx].prescricao
        agendamentos.value[idx] = {...res.data, prescricao: prescricaoAntiga}
      }
      toast.success(`Status atualizado para ${status}`)
    } catch (e) {
      console.error(e)
      toast.error("Erro ao atualizar status")
    }
  }

  async function atualizarStatusFarmacia(id: string, status: FarmaciaStatusEnum) {
    try {
      const payload = {
        detalhes: {
          infusao: {
            status_farmacia: status
          }
        }
      }
      const res = await api.put(`/api/agendamentos/${id}`, payload)
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) {
        const prescricaoAntiga = agendamentos.value[idx].prescricao
        agendamentos.value[idx] = {...res.data, prescricao: prescricaoAntiga}
      }
    } catch (e) {
      console.error(e)
      toast.error("Erro ao atualizar status da farmácia")
    }
  }


  async function atualizarHorarioPrevisao(id: string, horario: string) {
    try {
      const payload = {detalhes: {infusao: {horario_previsao_entrega: horario}}}
      const res = await api.put(`/api/agendamentos/${id}`, payload)
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) {
        const prescricaoAntiga = agendamentos.value[idx].prescricao
        agendamentos.value[idx] = {...res.data, prescricao: prescricaoAntiga}
      }
    } catch (e) {
      toast.error("Erro ao atualizar horário")
    }
  }

  async function trocarPrescricaoAgendamento(
    id: string,
    prescricaoId: string,
    motivo?: string,
    pacienteId?: string
  ) {
    try {
      const payload: any = {prescricao_id: prescricaoId}
      if (motivo) payload.motivo = motivo

      await api.put(`/api/agendamentos/${id}/prescricao`, payload)
      if (pacienteId) {
        await fetchAgendamentos(undefined, undefined, pacienteId)
      }
      toast.success("Prescrição do agendamento atualizada")
    } catch (e) {
      console.error(e)
      toast.error("Erro ao trocar prescrição do agendamento")
      throw e
    }
  }

  async function remarcarAgendamento(idOriginal: string, novaData: string, novoHorario: string, motivo: string) {
    try {
      const payload = {
        nova_data: novaData,
        novo_horario: novoHorario,
        motivo: motivo,
        manter_horario: false
      }
      await api.post(`/api/agendamentos/${idOriginal}/remarcar`, payload)
      toast.success("Agendamento remarcado")
    } catch (e: any) {
      console.error(e)
      toast.error(e.response?.data?.detail || "Erro ao remarcar agendamento")
    }
  }

  async function remarcarAgendamentosLote(ids: string[], novaData: string, novoHorario: string, motivo: string, manterHorario: boolean) {
     try {
       const payload = {
         ids: ids,
         nova_data: novaData,
         novo_horario: manterHorario ? null : novoHorario,
         motivo: motivo,
         manter_horario: manterHorario
       }
       await api.post('/api/agendamentos/remarcar-lote', payload)
       toast.success(`Agendamentos remarcados`)
     } catch (e: any) {
       console.error(e)
       toast.error(e.response?.data?.detail || "Erro ao remarcar em lote")
       throw e
     }
  }

  async function atualizarTagsAgendamento(id: string, tags: string[]) {
    try {
      const res = await api.put(`/api/agendamentos/${id}`, {tags})
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) {
        const prescricaoAntiga = agendamentos.value[idx].prescricao
        agendamentos.value[idx] = {...res.data, prescricao: prescricaoAntiga}
      }
    } catch (e) {
      console.error(e)
      toast.error("Erro ao salvar tags")
      throw e
    }
  }

  async function salvarChecklistFarmacia(id: string, itensPreparados: string[]) {
    try {
      const payload = {
        detalhes: {
          infusao: {
            itens_preparados: itensPreparados
          }
        }
      }
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

  async function atualizarAgendamentosEmLote(itens: { id: string, [key: string]: any }[]) {
    try {
      const payload = {
        itens: itens
      }

      const res = await api.put('/api/agendamentos/lote', payload)
      const atualizados = res.data as Agendamento[]

      atualizados.forEach(atualizado => {
        const idx = agendamentos.value.findIndex(a => a.id === atualizado.id)
        if (idx !== -1) {
          const prescricaoAntiga = agendamentos.value[idx].prescricao
          agendamentos.value[idx] = { ...atualizado, prescricao: prescricaoAntiga }
        }
      })

      toast.success(`${atualizados.length} agendamentos atualizados`)
      return atualizados
    } catch (e: any) {
      console.error(e)
      if (e.response?.data?.detail) {
          toast.error(e.response.data.detail)
      } else {
          toast.error("Erro ao atualizar agendamentos em lote")
      }
      throw e
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
    trocarPrescricaoAgendamento,
    remarcarAgendamento,
    remarcarAgendamentosLote,
    atualizarTagsAgendamento,
    atualizarAgendamentosEmLote,
    salvarChecklistFarmacia
  }
})
