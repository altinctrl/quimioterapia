import {computed, Ref, watch} from 'vue'
import {useAppStore} from '@/stores/storeGeral.ts'
import {Agendamento, TipoAgendamento} from "@/types/typesAgendamento.ts"

export function useAgendaDados(dataSelecionada: Ref<string>) {
  const appStore = useAppStore()

  watch(dataSelecionada, async (novaData) => {
    await appStore.fetchAgendamentos(novaData, novaData)
  }, {immediate: true})

  const recarregarDados = async () => {
    await appStore.fetchAgendamentos(dataSelecionada.value, dataSelecionada.value)
  }

  const agendamentosDoDia = computed(() => {
    return appStore.getAgendamentosDoDia(dataSelecionada.value)
      .sort((a, b) => a.horarioInicio.localeCompare(b.horarioInicio))
  })

  const agendamentosPorTipo = computed(() => {
    const base = agendamentosDoDia.value
    return {
      infusao: base.filter(a => a.tipo === 'infusao'),
      consulta: base.filter(a => a.tipo === 'consulta'),
      procedimento: base.filter(a => a.tipo === 'procedimento')
    } satisfies Record<TipoAgendamento, Agendamento[]>
  })

  return {
    agendamentosPorTipo,
    recarregarDados
  }
}
