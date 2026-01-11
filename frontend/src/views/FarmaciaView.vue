<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useAppStore} from '@/stores/app'
import {isInfusao, type StatusFarmacia} from '@/types'
import {Card, CardContent} from '@/components/ui/card'
import FarmaciaHeader from '@/components/farmacia/FarmaciaHeader.vue'
import FarmaciaMetrics from '@/components/farmacia/FarmaciaMetrics.vue'
import FarmaciaTable from '@/components/farmacia/FarmaciaTable.vue'
import FarmaciaControls, {type FiltrosFarmacia} from '@/components/farmacia/FarmaciaControls.vue'
import {getDataLocal} from '@/lib/utils.ts';

const appStore = useAppStore()
const dataSelecionada = ref(getDataLocal())

const filtros = ref<FiltrosFarmacia>({
  ordenacao: 'horario',
  turno: 'todos',
  status: []
})

const expandedIds = ref<string[]>([])

const allExpanded = computed(() => {
  const ids = agendamentosDoDia.value.map(a => a.id)
  if (ids.length === 0) return false
  const expanded = new Set(expandedIds.value)
  return ids.every(id => expanded.has(id))
})

const handleDiaAnterior = () => {
  const d = new Date(dataSelecionada.value)
  d.setDate(d.getDate() - 1)
  dataSelecionada.value = d.toISOString().split('T')[0]
}

const handleProximoDia = () => {
  const d = new Date(dataSelecionada.value)
  d.setDate(d.getDate() + 1)
  dataSelecionada.value = d.toISOString().split('T')[0]
}

const handleResetFiltros = () => {
  filtros.value = {
    ordenacao: 'horario',
    turno: 'todos',
    status: []
  }
}

const handleToggleExpandAll = () => {
  const ids = agendamentosDoDia.value.map(a => a.id)
  if (ids.length === 0) {
    expandedIds.value = []
    return
  }

  expandedIds.value = allExpanded.value ? [] : ids
}

const agendamentosDoDia = computed(() => {
  let lista = appStore.agendamentos.filter(a => a.data === dataSelecionada.value)

  // Filtro de Turno
  if (filtros.value.turno !== 'todos') {
    lista = lista.filter(a => a.turno === filtros.value.turno)
  }

  // Filtro de Status
  if (filtros.value.status.length > 0) {
    lista = lista.filter(a => {
      if (!isInfusao(a)) return false
      return filtros.value.status.includes(a.detalhes.infusao.status_farmacia)
    })
  }

  // Ordenação
  return lista.sort((a, b) => {
    if (filtros.value.ordenacao === 'horario') {
      return a.horarioInicio.localeCompare(b.horarioInicio)
    }

    if (filtros.value.ordenacao === 'status') {
      // Prioridade: Pendente > Em Prep > Pronta > Enviada
      const statusOrder: Record<string, number> = {
        'pendente': 0, 'em-preparacao': 1, 'pronta': 2, 'enviada': 3
      }
      const sa = isInfusao(a) ? a.detalhes.infusao.status_farmacia : 'pendente'
      const sb = isInfusao(b) ? b.detalhes.infusao.status_farmacia : 'pendente'
      if (statusOrder[sa] !== statusOrder[sb]) return statusOrder[sa] - statusOrder[sb]
      return a.horarioInicio.localeCompare(b.horarioInicio)
    }

    return a.horarioInicio.localeCompare(b.horarioInicio)
  })
})

const metricas = computed(() => {
  const infusoes = agendamentosDoDia.value.filter(isInfusao)
  const total = infusoes.length
  const pendente = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'pendente').length
  const emPreparacao = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'em-preparacao').length
  const pronta = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'pronta').length
  const enviada = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'enviada').length
  return {total, pendente, emPreparacao, pronta, enviada}
})

const handleAlterarStatus = (agendamentoId: string, novoStatus: StatusFarmacia) => {
  appStore.atualizarStatusFarmacia(agendamentoId, novoStatus)
}

const handleAlterarHorario = (agendamentoId: string, novoHorario: string) => {
  appStore.atualizarHorarioPrevisao(agendamentoId, novoHorario)
}

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
  const pacientesIds = [...new Set(appStore.agendamentos.map(a => a.pacienteId))]
  if (pacientesIds.length > 0) {
    await Promise.all(pacientesIds.map(id => appStore.fetchPrescricoes(id)))
  }
}, {immediate: true})

watch(agendamentosDoDia, (lista) => {
  const ids = new Set(lista.map(a => a.id))
  expandedIds.value = expandedIds.value.filter(id => ids.has(id))
})
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Farmácia</h1>

    <FarmaciaHeader
        v-model="dataSelecionada"
        @dia-anterior="handleDiaAnterior"
        @proximo-dia="handleProximoDia"
    />

        <FarmaciaMetrics
        :metricas="metricas"
    />

    <Card class="overflow-hidden">
      <div class="px-4 pt-4">
        <FarmaciaControls
            v-model="filtros"
            :all-expanded="allExpanded"
            @toggle-expand-all="handleToggleExpandAll"
            @reset="handleResetFiltros"
        />
      </div>

      <CardContent class="p-0 mt-0">
        <FarmaciaTable
            :agendamentos="agendamentosDoDia"
            v-model:expanded-ids="expandedIds"
            @alterar-status="handleAlterarStatus"
            @alterar-horario="handleAlterarHorario"
        />
      </CardContent>
    </Card>
  </div>
</template>