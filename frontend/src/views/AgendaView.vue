<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
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
import {getDuracaoAgendamento, getGrupoInfusao, somarDias} from '@/utils/agendaUtils'
import {type Agendamento, AgendamentoStatusEnum, FarmaciaStatusEnum, statusPermitidosSemCheckin} from "@/types";
import {getDataLocal} from '@/lib/utils.ts';
import {toast} from "vue-sonner";
import AgendamentoDetalhesModal from "@/components/modals/AgendamentoDetalhesModal.vue";
import PrescricaoHistoricoModal from "@/components/modals/PrescricaoHistoricoModal.vue";

const router = useRouter()
const appStore = useAppStore()

onMounted(async () => {
  await Promise.all([
    appStore.fetchConfiguracoes(),
    appStore.fetchProtocolos()
  ])
})

const dataSelecionada = ref(getDataLocal())

const detalhesModalOpen = ref(false)
const agendamentoSelecionado = ref<Agendamento | null>(null)
const prescricaoModalOpen = ref(false)
const prescricaoParaVisualizar = ref<any>(null)
const tagsModalOpen = ref(false)
const tagsModalData = ref<{ id: string; tags: string[] } | null>(null)
const remarcarModalOpen = ref(false)
const agendamentoParaRemarcar = ref<Agendamento | null>(null)
const statusModalOpen = ref(false)
const statusPendingData = ref<{ id: string; novoStatus: AgendamentoStatusEnum; pacienteNome: string } | null>(null)

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

  if (filtros.value.esconderRemarcados) lista = lista.filter(a => a.status !== AgendamentoStatusEnum.REMARCADO)
  if (filtros.value.turno !== 'todos') lista = lista.filter(a => a.turno === filtros.value.turno)
  if (filtros.value.statusFarmacia.length > 0) {
    lista = lista.filter(a => {
      const status = a.detalhes?.infusao?.statusFarmacia
      return status && filtros.value.statusFarmacia.includes(status)
    })
  }
  if (filtros.value.gruposInfusao.length > 0) {
    lista = lista.filter(a => {
      const duracao = getDuracaoAgendamento(a)
      const grupo = getGrupoInfusao(duracao)
      return filtros.value.gruposInfusao.includes(grupo)
    })
  }

  return lista.sort((a, b) => {
    const durA = getDuracaoAgendamento(a)
    const durB = getDuracaoAgendamento(b)

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

const mostrarMetricas = ref(true)

const metricas = computed(() => {
  const list = agendamentosDoDia.value

  let rapido = 0
  let medio = 0
  let longo = 0
  let extraLongo = 0

  const getStatusFarmacia = (a: any) => a.detalhes?.infusao?.status_farmacia
  list.forEach(a => {
    const minutos = getDuracaoAgendamento(a)
    const grupo = getGrupoInfusao(minutos)
    if (grupo === 'rapido') rapido++
    else if (grupo === 'medio') medio++
    else if (grupo === 'longo') longo++
    else if (grupo === 'extra_longo') extraLongo++
  })

  return {
    total: list.length,
    manha: list.filter(a => a.turno === 'manha').length,
    tarde: list.filter(a => a.turno === 'tarde').length,
    emAndamento: list.filter(a => [AgendamentoStatusEnum.EM_INFUSAO, AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO].includes(a.status)).length,
    concluidos: list.filter(a => a.status === AgendamentoStatusEnum.CONCLUIDO).length,
    encaixes: list.filter(a => a.encaixe).length,
    suspensos: list.filter(a => a.status === AgendamentoStatusEnum.SUSPENSO).length,
    rapido,
    medio,
    longo,
    extraLongo,
    intercorrencias: list.filter(a => a.status === AgendamentoStatusEnum.INTERCORRENCIA).length,
    farmaciaPendentes: list.filter(a => getStatusFarmacia(a) === FarmaciaStatusEnum.PENDENTE).length,
    farmaciaPreparando: list.filter(a => getStatusFarmacia(a) === FarmaciaStatusEnum.EM_PREPARACAO).length,
    farmaciaProntas: list.filter(a => getStatusFarmacia(a) === FarmaciaStatusEnum.PRONTO).length
  }
})

const handleDiaAnterior = () => {
  dataSelecionada.value = somarDias(dataSelecionada.value, -1)
}

const handleProximoDia = () => {
  dataSelecionada.value = somarDias(dataSelecionada.value, 1)
}

const handleHoje = () => {
  dataSelecionada.value = getDataLocal()
}

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
}, {immediate: true})

const handleVerDetalhes = (ag: Agendamento) => {
  agendamentoSelecionado.value = ag
  detalhesModalOpen.value = true
}

const handleAbrirPrescricao = (agendamento: Agendamento) => {
  if (detalhesModalOpen.value) detalhesModalOpen.value = false
  if (agendamento.prescricao) {
    prescricaoParaVisualizar.value = agendamento.prescricao
    prescricaoModalOpen.value = true
  } else {
    toast.error("Nenhuma prescrição vinculada a este agendamento.")
  }
}

const handleAbrirTags = (agendamento: Agendamento) => {
  tagsModalData.value = {id: agendamento.id, tags: agendamento.tags || []}
  tagsModalOpen.value = true
}

const salvarTags = async (id: string, tags: string[]) => {
  await appStore.atualizarTagsAgendamento(id, tags)
  tagsModalOpen.value = false
}

const handleAlterarCheckin = async (agendamento: any, novoCheckin: boolean) => {
  if (!novoCheckin && !statusPermitidosSemCheckin.includes(agendamento.status)) {
    toast.error("Ação Bloqueada", {
      description: `Não é possível remover o check-in pois o status "${agendamento.status}" exige presença do paciente.`
    })
    return
  }

  await appStore.atualizarCheckin(agendamento.id, novoCheckin)
}

const handleAlterarStatus = (agendamento: Agendamento, novoStatus: string) => {
  if ([AgendamentoStatusEnum.SUSPENSO, AgendamentoStatusEnum.INTERCORRENCIA].includes(novoStatus as AgendamentoStatusEnum)) {
    statusPendingData.value = {
      id: agendamento.id,
      novoStatus: novoStatus as AgendamentoStatusEnum,
      pacienteNome: agendamento.paciente?.nome || 'Paciente'
    }
    statusModalOpen.value = true
  } else {
    appStore.atualizarStatusAgendamento(agendamento.id, novoStatus as AgendamentoStatusEnum)
  }
}

const confirmarAlteracaoStatus = (detalhes: any) => {
  if (statusPendingData.value && statusPendingData.value.id) {
    appStore.atualizarStatusAgendamento(
        statusPendingData.value.id,
        statusPendingData.value.novoStatus as AgendamentoStatusEnum,
        detalhes
    )
    statusPendingData.value = null
  }
}

const handleAbrirRemarcar = (agendamento: Agendamento) => {
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

    <AgendamentoDetalhesModal
        v-model:open="detalhesModalOpen"
        :agendamento="agendamentoSelecionado"
        :paciente-nome="agendamentoSelecionado?.paciente?.nome"
        @abrir-prescricao="handleAbrirPrescricao"
    />

    <PrescricaoHistoricoModal
        v-if="prescricaoParaVisualizar"
        v-model:open="prescricaoModalOpen"
        :prescricao="prescricaoParaVisualizar"
    />

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
        :paciente-nome="statusPendingData.pacienteNome"
        :status-destino="statusPendingData.novoStatus"
        @confirm="confirmarAlteracaoStatus"
    />

    <AgendaHeader
        v-model="dataSelecionada"
        :mostrar-metricas="mostrarMetricas"
        @toggle-metrics="mostrarMetricas = !mostrarMetricas"
        @navigate-prev="handleDiaAnterior"
        @navigate-next="handleProximoDia"
        @new-appointment="router.push('/agendamento')"
        @go-today="handleHoje"
    />

    <AgendaMetrics v-if="mostrarMetricas" :metricas="metricas"/>

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
            @abrir-detalhes="handleVerDetalhes"
            @abrir-prescricao="handleAbrirPrescricao"
            @abrir-tags="handleAbrirTags"
            @abrir-remarcar="handleAbrirRemarcar"
            @alterar-checkin="handleAlterarCheckin"
            @alterar-status="handleAlterarStatus"
        />
      </CardContent>
    </Card>
  </div>
</template>
