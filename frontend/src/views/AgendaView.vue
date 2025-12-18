<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent} from '@/components/ui/card'
import AgendaHeader from '@/components/agenda/AgendaHeader.vue'
import AgendaMetrics from '@/components/agenda/AgendaMetrics.vue'
import AgendaTable from '@/components/agenda/AgendaTable.vue'
import AgendaRemarcarModal from '@/components/agenda/AgendaRemarcarModal.vue'
import StatusChangeModal from '@/components/agenda/AgendaStatusChangeModal.vue'
import TagsModal from '@/components/modals/TagsModal.vue'
import AgendaControls, {type FiltrosAgenda} from '@/components/agenda/AgendaControls.vue'
import {calcularDuracaoMinutos, getGrupoInfusao} from '@/utils/agendaUtils'
import {StatusPaciente} from "@/types";

const router = useRouter()
const appStore = useAppStore()

const dataSelecionada = ref(new Date().toISOString().split('T')[0])

const tagsModalOpen = ref(false)
const tagsModalData = ref<{ id: string; tags: string[] } | null>(null)

const remarcarModalOpen = ref(false)
const agendamentoParaRemarcar = ref<any>(null)

const statusModalOpen = ref(false)
const statusPendingData = ref<{ id: string; novoStatus: string; pacienteNome: string } | null>(null)

const agendamentosDoDia = computed(() => {
  return appStore.getAgendamentosDoDia(dataSelecionada.value)
      .sort((a, b) => a.horarioInicio.localeCompare(b.horarioInicio))
})

const filtros = ref<FiltrosAgenda>({
  ordenacao: 'grupo_asc',
  turno: 'todos',
  statusFarmacia: [],
  gruposInfusao: [],
  esconderRemarcados: true
})

const resetFiltros = () => {
  filtros.value = {
    ordenacao: 'grupo_asc',
    turno: 'todos',
    statusFarmacia: [],
    gruposInfusao: [],
    esconderRemarcados: true
  }
}

const agendamentosProcessados = computed(() => {
  let lista = appStore.getAgendamentosDoDia(dataSelecionada.value)

  if (filtros.value.esconderRemarcados) lista = lista.filter(a => a.status !== 'remarcado')
  if (filtros.value.turno !== 'todos') lista = lista.filter(a => a.turno === filtros.value.turno)
  if (filtros.value.statusFarmacia.length > 0) lista = lista.filter(a => filtros.value.statusFarmacia.includes(a.statusFarmacia))
  if (filtros.value.gruposInfusao.length > 0) {
    lista = lista.filter(a => {
      const duracao = calcularDuracaoMinutos(a.horarioInicio, a.horarioFim)
      const grupo = getGrupoInfusao(duracao)
      return filtros.value.gruposInfusao.includes(grupo)
    })
  }

  return lista.sort((a, b) => {
    const durA = calcularDuracaoMinutos(a.horarioInicio, a.horarioFim)
    const durB = calcularDuracaoMinutos(b.horarioInicio, b.horarioFim)

    switch (filtros.value.ordenacao) {
      case 'grupo_asc':
        if (durA !== durB) return durA - durB
        return a.horarioInicio.localeCompare(b.horarioInicio)

      case 'grupo_desc':
        if (durA !== durB) return durB - durA
        return a.horarioInicio.localeCompare(b.horarioInicio)

      case 'horario':
        return a.horarioInicio.localeCompare(b.horarioInicio)

      case 'status':
        const getPeso = (s: string) => {
          if (['suspenso', 'intercorrencia', 'ausente'].includes(s)) return 0
          if (s === 'aguardando-medicamento') return 1
          if (s === 'em-infusao') return 2
          if (s === 'concluido') return 10
          return 5
        }
        return getPeso(a.status) - getPeso(b.status)

      default:
        return 0
    }
  })
})

const metricas = computed(() => {
  const list = agendamentosDoDia.value
  return {
    total: list.length,
    manha: list.filter(a => a.turno === 'manha').length,
    tarde: list.filter(a => a.turno === 'tarde').length,
    emAndamento: list.filter(a => ['em-infusao', 'aguardando-medicamento'].includes(a.status)).length,
    concluidos: list.filter(a => a.status === 'concluido').length
  }
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

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
  const pacientesIds = [...new Set(appStore.agendamentos.map(a => a.pacienteId))]
  if (pacientesIds.length > 0) {
    await Promise.all(pacientesIds.map(id => appStore.fetchPrescricoes(id)))
  }
}, {immediate: true})

const handleAbrirTags = (agendamento: any) => {
  tagsModalData.value = {id: agendamento.id, tags: agendamento.tags || []}
  tagsModalOpen.value = true
}

const salvarTags = (id: string, tags: string[]) => {
  const agendamento = appStore.agendamentos.find(a => a.id === id)
  if (agendamento) {
    agendamento.tags = tags
  }
  tagsModalOpen.value = false
}

const handleAlterarStatus = (agendamento: any, novoStatus: string) => {
  if (['suspenso', 'intercorrencia'].includes(novoStatus)) {
    statusPendingData.value = {
      id: agendamento.id,
      novoStatus,
      pacienteNome: agendamento.paciente?.nome || 'Paciente'
    }
    statusModalOpen.value = true
  } else {
    appStore.atualizarStatusAgendamento(agendamento.id, novoStatus as StatusPaciente)
  }
}

const confirmarAlteracaoStatus = (detalhes: any) => {
  if (statusPendingData.value && statusPendingData.value.id) {
    appStore.atualizarStatusAgendamento(
      statusPendingData.value.id,
      statusPendingData.value.novoStatus as StatusPaciente,
      detalhes
    )
    statusPendingData.value = null
  }
}

const handleAbrirRemarcar = (agendamento: any) => {
  agendamentoParaRemarcar.value = agendamento
  remarcarModalOpen.value = true
}

const handleRemarcado = () => {
  appStore.fetchAgendamentos(dataSelecionada.value, dataSelecionada.value)
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900">Agenda</h1>
    </div>

    <TagsModal
        :agendamento-id="tagsModalData?.id || ''"
        :open="tagsModalOpen"
        :tags-atuais="tagsModalData?.tags || []"
        @salvar="salvarTags"
        @update:open="tagsModalOpen = $event"
    />

    <AgendaRemarcarModal
        v-model:open="remarcarModalOpen"
        :agendamento="agendamentoParaRemarcar"
        @remarcado="handleRemarcado"
    />

    <StatusChangeModal
        v-if="statusPendingData"
        v-model:open="statusModalOpen"
        :status-destino="statusPendingData.novoStatus"
        :paciente-nome="statusPendingData.pacienteNome"
        @confirm="confirmarAlteracaoStatus"
    />

    <AgendaHeader
        v-model="dataSelecionada"
        @navigate-prev="handleDiaAnterior"
        @navigate-next="handleProximoDia"
        @new-appointment="router.push('/agendamento')"
    />

    <AgendaMetrics :metricas="metricas"/>

    <Card class="overflow-hidden">
      <div class="px-4 pt-4">
        <AgendaControls
            v-model="filtros"
            @reset="resetFiltros"
        />
      </div>

      <CardContent class="p-0 mt-0">
        <AgendaTable
            :agendamentos="agendamentosProcessados"
            class="border-0 rounded-none shadow-none"
            @abrir-tags="handleAbrirTags"
            @abrir-remarcar="handleAbrirRemarcar"
            @alterar-status="handleAlterarStatus"
        />
      </CardContent>
    </Card>
  </div>
</template>