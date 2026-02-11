<script lang="ts" setup>
import {computed, onMounted, reactive, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/storeGeral.ts'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import AgendaCabecalho from '@/components/agenda/AgendaCabecalho.vue'
import AgendaMetricas from '@/components/agenda/AgendaMetricas.vue'
import AgendaModalRemarcacao from '@/components/agenda/AgendaModalRemarcacao.vue'
import AgendaModalStatus from '@/components/agenda/AgendaModalStatus.vue'
import AgendaModalEtiquetas from '@/components/agenda/AgendaModalEtiquetas.vue'
import AgendaAba from '@/components/agenda/AgendaAba.vue'
import {
  Agendamento,
  AgendamentoStatusEnum,
  FiltrosAgenda,
  TipoAgendamento
} from "@/types/typesAgendamento.ts";
import {STATUS_INFUSAO_PRE_CHECKIN} from "@/constants/constAgenda.ts";
import {toast} from "vue-sonner";
import AgendamentoModalDetalhes from "@/components/comuns/AgendamentoModalDetalhes.vue";
import PrescricaoModalDetalhes from "@/components/comuns/PrescricaoModalDetalhes.vue";
import {useLocalStorage, useSessionStorage} from "@vueuse/core";
import {useAutoRefresh} from "@/composables/useAutoRefresh.ts";
import {useAgendaNavegacao} from "@/composables/useAgendaNavegacao.ts";
import {useAgendaModals} from "@/composables/useAgendaModals.ts";
import {useAgendaMetricas} from "@/composables/useAgendaMetricas.ts";

const router = useRouter()
const appStore = useAppStore()

const {
  dataSelecionada,
  handleHoje,
  handleDiaAnterior,
  handleProximoDia,
} = useAgendaNavegacao('agenda_data_selecionada')

const {
  detalhesModalOpen,
  agendamentoSelecionado,
  abrirDetalhesAgendamento: handleVerDetalhes,

  prescricaoModalOpen,
  prescricaoParaVisualizar,
  abrirPrescricao: handleAbrirPrescricao,

  tagsModalOpen,
  tagsModalData,
  abrirTags: handleAbrirTags,

  remarcarModalOpen,
  agendamentoParaRemarcar,
  abrirRemarcar: handleAbrirRemarcar,

  statusModalOpen,
  statusPendingData,
  abrirAlterarStatus,

  isAlgumModalAberto
} = useAgendaModals()

onMounted(async () => {
  await Promise.all([
    appStore.fetchConfiguracoes(),
    appStore.fetchProtocolos()
  ])
})

const selecoesPorAba = reactive({
  infusao: 0,
  consulta: 0,
  procedimento: 0
})

const existeSelecaoPendente = () => {
  return (selecoesPorAba.infusao + selecoesPorAba.consulta + selecoesPorAba.procedimento) > 0
}

useAutoRefresh(
    async () => {
      await appStore.fetchAgendamentos(dataSelecionada.value, dataSelecionada.value)
    },
    {
      intervaloPadrao: 60000,
      condicoesPausa: [
        () => isAlgumModalAberto.value,
        () => existeSelecaoPendente()
      ]
    }
)

const abaAtiva = useSessionStorage<TipoAgendamento>('agenda_aba_ativa', 'infusao')

const agendamentosDoDia = computed(() => {
  return appStore.getAgendamentosDoDia(dataSelecionada.value)
      .sort((a, b) => a.horarioInicio.localeCompare(b.horarioInicio))
})

const defaultFiltros = (): FiltrosAgenda => ({
  ordenacao: 'horario',
  turno: 'todos',
  statusFarmacia: [],
  gruposInfusao: [],
  esconderRemarcados: true
})

const filtrosInfusao = useLocalStorage<FiltrosAgenda>('agenda_filtros_infusao', defaultFiltros())
const filtrosConsulta = useLocalStorage<FiltrosAgenda>('agenda_filtros_consulta', defaultFiltros())
const filtrosProcedimento = useLocalStorage<FiltrosAgenda>('agenda_filtros_procedimento', defaultFiltros())

const resetFiltros = (tipo: TipoAgendamento) => {
  if (tipo === 'infusao') filtrosInfusao.value = defaultFiltros()
  if (tipo === 'consulta') filtrosConsulta.value = defaultFiltros()
  if (tipo === 'procedimento') filtrosProcedimento.value = defaultFiltros()
}

const agendamentosPorTipo = computed(() => {
  const base = agendamentosDoDia.value
  return {
    infusao: base.filter(a => a.tipo === 'infusao'),
    consulta: base.filter(a => a.tipo === 'consulta'),
    procedimento: base.filter(a => a.tipo === 'procedimento')
  } satisfies Record<TipoAgendamento, Agendamento[]>
})

const agendamentosTipoAtivo = computed(() => agendamentosPorTipo.value[abaAtiva.value])

const mostrarMetricas = useLocalStorage('agenda_mostrar_metricas', true)

const {
  metricas
} = useAgendaMetricas(agendamentosTipoAtivo)

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
}, {immediate: true})

const salvarTags = async (id: string, tags: string[]) => {
  await appStore.atualizarTagsAgendamento(id, tags)
  tagsModalOpen.value = false
}

const handleAlterarCheckin = async (agendamento: any, novoCheckin: boolean) => {
  if (!novoCheckin && !STATUS_INFUSAO_PRE_CHECKIN.includes(agendamento.status)) {
    toast.error("Ação Bloqueada", {
      description: `Não é possível remover o check-in pois o status "${agendamento.status}" exige presença do paciente.`
    })
    return
  }

  await appStore.atualizarCheckin(agendamento.id, novoCheckin)
}

const handleAlterarStatus = (agendamento: Agendamento, novoStatus: string) => {
  if ([AgendamentoStatusEnum.SUSPENSO, AgendamentoStatusEnum.INTERCORRENCIA].includes(novoStatus as AgendamentoStatusEnum)) {
    abrirAlterarStatus(agendamento, novoStatus as AgendamentoStatusEnum)
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

const handleRemarcado = () => {
  appStore.fetchAgendamentos(dataSelecionada.value, dataSelecionada.value)
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900">Agenda</h1>
    </div>

    <AgendamentoModalDetalhes
        v-model:open="detalhesModalOpen"
        :agendamento="agendamentoSelecionado"
        :paciente-nome="agendamentoSelecionado?.paciente?.nome"
        @abrir-prescricao="handleAbrirPrescricao"
    />

    <PrescricaoModalDetalhes
        v-if="prescricaoParaVisualizar"
        v-model:open="prescricaoModalOpen"
        :prescricao="prescricaoParaVisualizar"
    />

    <AgendaModalEtiquetas
        :agendamento-id="tagsModalData?.id || ''"
        :open="tagsModalOpen"
        :tags-atuais="tagsModalData?.tags || []"
        @salvar="salvarTags"
        @update:open="tagsModalOpen = $event"
    />

    <AgendaModalRemarcacao
        v-model:open="remarcarModalOpen"
        :agendamento="agendamentoParaRemarcar"
        @remarcado="handleRemarcado"
    />

    <AgendaModalStatus
        v-if="statusPendingData"
        v-model:open="statusModalOpen"
        :paciente-nome="statusPendingData.pacienteNome"
        :status-destino="statusPendingData.novoStatus"
        @confirm="confirmarAlteracaoStatus"
    />

    <Tabs v-model="abaAtiva" class="space-y-4">
      <TabsList>
        <TabsTrigger value="infusao">Infusão</TabsTrigger>
        <TabsTrigger value="consulta">Consulta</TabsTrigger>
        <TabsTrigger value="procedimento">Procedimento</TabsTrigger>
      </TabsList>

      <AgendaCabecalho
          v-model="dataSelecionada"
          :mostrar-metricas="mostrarMetricas"
          @toggle-metrics="mostrarMetricas = !mostrarMetricas"
          @navigate-prev="handleDiaAnterior"
          @navigate-next="handleProximoDia"
          @new-appointment="router.push('/agendamento')"
          @go-today="handleHoje"
      />

      <TabsContent class="space-y-4" value="infusao">
        <AgendaMetricas v-if="mostrarMetricas" :metricas="metricas" tipo="infusao"/>
        <AgendaAba
            v-model:filtros="filtrosInfusao"
            :agendamentos="agendamentosPorTipo.infusao"
            :mostrar-filtros-infusao="true"
            tipo="infusao"
            @reset="resetFiltros('infusao')"
            @abrir-detalhes="handleVerDetalhes"
            @abrir-prescricao="handleAbrirPrescricao"
            @abrir-tags="handleAbrirTags"
            @abrir-remarcar="handleAbrirRemarcar"
            @alterar-checkin="handleAlterarCheckin"
            @alterar-status="handleAlterarStatus"
            @remarcado="handleRemarcado"
            @selection-change="(n) => selecoesPorAba.infusao = n"
        />
      </TabsContent>

      <TabsContent class="space-y-4" value="consulta">
        <AgendaMetricas v-if="mostrarMetricas" :metricas="metricas" tipo="consulta"/>
        <AgendaAba
            v-model:filtros="filtrosConsulta"
            :agendamentos="agendamentosPorTipo.consulta"
            :mostrar-filtros-infusao="false"
            tipo="consulta"
            @reset="resetFiltros('consulta')"
            @abrir-detalhes="handleVerDetalhes"
            @abrir-prescricao="handleAbrirPrescricao"
            @abrir-tags="handleAbrirTags"
            @abrir-remarcar="handleAbrirRemarcar"
            @alterar-checkin="handleAlterarCheckin"
            @alterar-status="handleAlterarStatus"
            @remarcado="handleRemarcado"
            @selection-change="(n) => selecoesPorAba.consulta = n"
        />
      </TabsContent>

      <TabsContent class="space-y-4" value="procedimento">
        <AgendaMetricas v-if="mostrarMetricas" :metricas="metricas" tipo="procedimento"/>
        <AgendaAba
            v-model:filtros="filtrosProcedimento"
            :agendamentos="agendamentosPorTipo.procedimento"
            :mostrar-filtros-infusao="false"
            tipo="procedimento"
            @reset="resetFiltros('procedimento')"
            @abrir-detalhes="handleVerDetalhes"
            @abrir-prescricao="handleAbrirPrescricao"
            @abrir-tags="handleAbrirTags"
            @abrir-remarcar="handleAbrirRemarcar"
            @alterar-checkin="handleAlterarCheckin"
            @alterar-status="handleAlterarStatus"
            @remarcado="handleRemarcado"
            @selection-change="(n) => selecoesPorAba.procedimento = n"
        />
      </TabsContent>
    </Tabs>
  </div>
</template>
