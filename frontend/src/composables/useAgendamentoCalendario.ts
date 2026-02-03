import {computed, Ref, ref} from 'vue'
import {useAppStore} from '@/stores/storeGeral.ts'
import {Agendamento, GrupoInfusao, TipoAgendamento} from "@/types/typesAgendamento.ts";

export interface VagasInfo {
  count: number
  full: boolean
  label?: string
  blocked?: boolean
  hidden?: boolean
}

export function useAgendamentoCalendario(
  tipoAgendamento: Ref<TipoAgendamento>,
  grupoInfusao: Ref<GrupoInfusao>,
  prescricaoSelecionadaId: Ref<string>,
  diasSemanaPermitidos: Ref<number[] | undefined>
) {
  const appStore = useAppStore()

  const mesSelecionado = ref(String(new Date().getMonth() + 1))
  const anoSelecionado = ref(String(new Date().getFullYear()))

  const diasDoMes = computed(() => {
    const year = parseInt(anoSelecionado.value)
    const month = parseInt(mesSelecionado.value) - 1
    const date = new Date(year, month, 1)
    const days: Date[] = []
    while (date.getMonth() === month) {
      days.push(new Date(date))
      date.setDate(date.getDate() + 1)
    }
    return days
  })

  const espacosVazios = computed(() => {
    if (diasDoMes.value.length === 0) return 0
    return diasDoMes.value[0].getDay()
  })

  const todayStr = new Date().toISOString().split('T')[0]

  const isDiaBloqueado = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0]
    const isPastDate = dateStr < todayStr
    const dayOfWeek = date.getDay()
    const isClosedDay = !appStore.parametros.diasFuncionamento.includes(dayOfWeek)
    return isPastDate || isClosedDay
  }

  const getStatusVagas = (dataStr: string): VagasInfo => {
    const dateObj = new Date(dataStr + 'T12:00:00');
    const dayOfWeek = dateObj.getDay();

    const agendamentosNoDia = appStore.getAgendamentosDoDia(dataStr)
    const limiteVagas = appStore.parametros.vagas

    const isConsideradoNaCapacidade = (ag: Agendamento) => {
      return ag.status !== 'remarcado' && ag.status !== 'suspenso'
    }

    if (tipoAgendamento.value !== 'infusao') {
      const tipo = tipoAgendamento.value
      const limite = tipo === 'consulta' ? limiteVagas.consultas : limiteVagas.procedimentos
      const countNoTipo = agendamentosNoDia.reduce((acc, ag) => {
        if (!isConsideradoNaCapacidade(ag)) return acc
        return ag.tipo === tipo ? acc + 1 : acc
      }, 0)

      const vagasRestantes = limite - countNoTipo
      return {
        count: vagasRestantes,
        full: vagasRestantes <= 0,
        label: tipo
      }
    } else {

      if (!prescricaoSelecionadaId.value) {
        return { count: 0, full: false, hidden: true }
      }

      if (diasSemanaPermitidos.value && diasSemanaPermitidos.value.length > 0) {
        if (!diasSemanaPermitidos.value.includes(dayOfWeek)) {
          return {
            count: 0,
            full: true,
            blocked: true,
            label: 'Não Permitido'
          }
        }
      }

      const grupo = grupoInfusao.value
      const chaveGrupo = `infusao_${grupo}` as keyof typeof limiteVagas
      const limiteGrupo = limiteVagas[chaveGrupo] || 0

      const countNoGrupo = agendamentosNoDia.reduce((acc, ag) => {
        if (!isConsideradoNaCapacidade(ag)) return acc
        if (ag.tipo !== 'infusao') return acc

        const p = appStore.getPacienteById(ag.pacienteId)
        const prot = appStore.getProtocoloById((p as any)?.protocoloId || '')
        const g = (prot as any)?.grupoInfusao || 'medio'
        return g === grupo ? acc + 1 : acc
      }, 0)

      const vagasRestantes = limiteGrupo - countNoGrupo
      return {
        count: vagasRestantes,
        full: vagasRestantes <= 0,
        label: `grupo ${grupo}`
      }
    }
  }

  return {
    mesSelecionado,
    anoSelecionado,
    diasDoMes,
    espacosVazios,
    isDiaBloqueado,
    getStatusVagas
  }
}
