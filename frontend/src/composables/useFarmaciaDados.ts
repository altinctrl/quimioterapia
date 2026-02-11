import { computed, Ref, ref } from 'vue'
import { useLocalStorage, useSessionStorage } from "@vueuse/core"
import { useAppStore } from '@/stores/storeGeral.ts'
import {
  AgendamentoStatusEnum,
  FarmaciaStatusEnum,
  FarmaciaTableRow,
  FiltrosFarmacia
} from "@/types/typesAgendamento.ts"
import { extrairMedicamentosDoAgendamento } from "@/utils/utilsFarmacia.ts"
import { isInfusao } from "@/utils/utilsAgenda.ts"
import { STATUS_ORDER } from "@/constants/constFarmacia.ts"
import { useAgendaMetricas } from "@/composables/useAgendaMetricas.ts"

export function useFarmaciaDados(dataSelecionada: Ref<string>) {
  const appStore = useAppStore()

  const filtros = useLocalStorage<FiltrosFarmacia>('farmacia_filtros', {
    ordenacao: 'horario',
    turno: 'todos',
    status: []
  })

  const mostrarMetricas = useLocalStorage('farmacia_mostrar_metricas', true)
  const expandedIdsMap = useSessionStorage<Record<string, string[]>>('farmacia_listas_expandidas_map', {})
  const selectedIds = ref<string[]>([])

  const agendamentosDoDia = computed(() => {
    return appStore.getAgendamentosDoDia(dataSelecionada.value).filter(ag =>
      ag.tipo === 'infusao' && ag.detalhes?.infusao
    )
  })

  const { metricas: metricasGerais } = useAgendaMetricas(agendamentosDoDia)

  const metricas = computed(() => ({
    total: metricasGerais.value.total,
    pendente: metricasGerais.value.farmaciaPendentes,
    emPreparacao: metricasGerais.value.farmaciaPreparando,
    pronta: metricasGerais.value.farmaciaProntas,
    enviada: metricasGerais.value.farmaciaEnviadas
  }))

  const tableRows = computed<FarmaciaTableRow[]>(() => {
    return agendamentosDoDia.value.map(ag => {
      const infoInfusao = ag.detalhes?.infusao
      const prescricao = ag.prescricao
      const medicamentosRow = extrairMedicamentosDoAgendamento(ag)
      const totalMeds = medicamentosRow.length
      const totalChecked = medicamentosRow.filter(m => m.checked).length
      const checklistLabel = totalMeds > 0 ? `${totalChecked}/${totalMeds}` : '-'

      const statusFarmacia = infoInfusao?.statusFarmacia || FarmaciaStatusEnum.PENDENTE
      const bloqueado = [AgendamentoStatusEnum.SUSPENSO, AgendamentoStatusEnum.REMARCADO].includes(ag.status)

      const getStatusDotColor = (statusId: string) => {
        const config = appStore.getStatusConfig(statusId)
        return config ? config.cor.split(' ')[0] : 'bg-gray-200'
      }

      return {
        id: ag.id,
        pacienteId: ag.pacienteId,
        horario: ag.horarioInicio,
        pacienteNome: ag.paciente?.nome || 'Paciente não carregado',
        pacienteRegistro: ag.paciente?.registro || '',
        observacoesClinicas: ag.paciente?.observacoesClinicas,
        protocoloNome: prescricao?.conteudo?.protocolo?.nome || '-',
        checkin: ag.checkin,
        statusTexto: ag.status ? ag.status.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '',
        statusBloqueado: bloqueado,
        statusFarmacia: statusFarmacia,
        statusFarmaciaCor: getStatusDotColor(bloqueado ? 'pendente' : statusFarmacia),
        previsaoEntrega: isInfusao(ag) ? ag.detalhes.infusao.horarioPrevisaoEntrega || '' : '',
        medicamentos: medicamentosRow,
        checklistLabel,
        hasMedicamentos: totalMeds > 0
      }
    })
  })

  const viewRows = computed(() => {
    let lista = [...tableRows.value]

    if (filtros.value.turno !== 'todos') {
      const idsTurno = new Set(agendamentosDoDia.value
        .filter(a => a.turno === filtros.value.turno)
        .map(a => a.id))
      lista = lista.filter(r => idsTurno.has(r.id))
    }

    if (filtros.value.status.length > 0) {
      lista = lista.filter(r => filtros.value.status.includes(r.statusFarmacia))
    }

    return lista.sort((a, b) => {
      if (filtros.value.ordenacao === 'horario') {
        return a.horario.localeCompare(b.horario)
      }
      if (filtros.value.ordenacao === 'status') {
        const rankA = STATUS_ORDER[a.statusFarmacia] ?? 0
        const rankB = STATUS_ORDER[b.statusFarmacia] ?? 0
        return rankA - rankB
      }
      return 0
    })
  })

  const expandedIdsDoDia = computed({
    get: () => expandedIdsMap.value[dataSelecionada.value] || [],
    set: (novosIds: string[]) => {
      expandedIdsMap.value = {
        ...expandedIdsMap.value,
        [dataSelecionada.value]: novosIds
      }
    }
  })

  const handleResetFiltros = () => {
    filtros.value = { ordenacao: 'horario', turno: 'todos', status: [] }
  }

  const limparSelecao = () => {
    selectedIds.value = []
  }

  return {
    filtros,
    mostrarMetricas,
    selectedIds,
    tableRows,
    viewRows,
    metricas,
    expandedIdsDoDia,
    handleResetFiltros,
    limparSelecao
  }
}
