import {useAppStore} from '@/stores/storeGeral.ts'
import {toast} from 'vue-sonner'
import {Agendamento, AgendamentoStatusEnum} from "@/types/typesAgendamento.ts"
import {STATUS_INFUSAO_PRE_CHECKIN} from "@/constants/constAgenda.ts"

interface OperacoesCallbacks {
  abrirRemarcar?: (ag: Agendamento) => void
  abrirModalStatus?: (ag: Agendamento, novoStatus: AgendamentoStatusEnum) => void
}

export function useAgendaOperacoes() {
  const appStore = useAppStore()

  const alterarCheckin = async (agendamento: Agendamento, novoCheckin: boolean) => {
    if (!novoCheckin && !STATUS_INFUSAO_PRE_CHECKIN.includes(agendamento.status)) {
      toast.error("Ação Bloqueada", {
        description: `Não é possível remover o check-in pois o status "${agendamento.status}" exige presença do paciente.`
      })
      return
    }
    await appStore.atualizarCheckin(agendamento.id, novoCheckin)
  }

  const alterarStatusPaciente = async (
    agendamento: Agendamento,
    novoStatus: string,
    callbacks?: OperacoesCallbacks
  ) => {
    const statusEnum = novoStatus as AgendamentoStatusEnum

    if (statusEnum === AgendamentoStatusEnum.REMARCADO) {
      callbacks?.abrirRemarcar?.(agendamento)
      return
    }

    if ([AgendamentoStatusEnum.SUSPENSO, AgendamentoStatusEnum.INTERCORRENCIA].includes(statusEnum)) {
      callbacks?.abrirModalStatus?.(agendamento, statusEnum)
      return
    }

    await appStore.atualizarStatusAgendamento(agendamento.id, statusEnum)
  }

  const aplicarStatusPacienteLote = async (
    selecionados: Agendamento[],
    novoStatus: AgendamentoStatusEnum
  ) => {
    if (!novoStatus) {
      toast.error('Selecione um status para aplicar.')
      return
    }
    if (selecionados.length === 0) return

    const exigeCheckin = !STATUS_INFUSAO_PRE_CHECKIN.includes(novoStatus)
    const precisaMarcarCheckin = selecionados.some(ag => !ag.checkin)

    let forcarCheckin = false

    if (exigeCheckin && precisaMarcarCheckin) {
      const confirmacao = window.confirm(
        `O status "${novoStatus}" exige que o paciente esteja em sala.\n\nDeseja marcar os pacientes como "em sala" para os agendamentos selecionados e continuar?`
      )
      if (!confirmacao) return
      forcarCheckin = true
    }

    const itensParaAtualizar = selecionados.map(ag => {
      const payload: any = {
        id: ag.id,
        status: novoStatus
      }
      if (forcarCheckin && !ag.checkin) {
        payload.checkin = true
      }
      return payload
    })

    const itensFiltrados = itensParaAtualizar.filter(item => {
      const original = selecionados.find(s => s.id === item.id)
      if (!original) return false
      const statusMudou = original.status !== item.status
      const checkinMudou = item.checkin === true && !original.checkin
      return statusMudou || checkinMudou
    })

    if (itensFiltrados.length === 0) {
      toast.info('Nenhuma alteração necessária nos itens selecionados.')
      return
    }

    try {
      await appStore.atualizarAgendamentosEmLote(itensFiltrados)
    } catch (error) {
      console.error("Falha no update em lote", error)
    }
  }

  const remarcarLote = async (
    ids: string[],
    form: { novaData: string, novoHorario: string, motivo: string, manterHorario: boolean }
  ) => {
    if (!form.novaData || !form.motivo) {
      toast.error('Preencha data e motivo.')
      throw new Error('Dados inválidos')
    }

    if (!form.manterHorario && !form.novoHorario) {
      toast.error('Informe o novo horário ou mantenha o horário original.')
      throw new Error('Dados inválidos')
    }

    await appStore.remarcarAgendamentosLote(
      ids,
      form.novaData,
      form.novoHorario,
      form.motivo,
      form.manterHorario
    )
  }

  return {
    alterarCheckin,
    alterarStatusPaciente,
    aplicarStatusPacienteLote,
    remarcarLote,
  }
}
