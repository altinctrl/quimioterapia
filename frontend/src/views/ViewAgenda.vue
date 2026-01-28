<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/storeGeral.ts'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import AgendaCabecalho from '@/components/agenda/AgendaCabecalho.vue'
import AgendaMetricas from '@/components/agenda/AgendaMetricas.vue'
import AgendaModalRemarcacao from '@/components/agenda/AgendaModalRemarcacao.vue'
import AgendaModalStatus from '@/components/agenda/AgendaModalStatus.vue'
import AgendaModalEtiquetas from '@/components/agenda/AgendaModalEtiquetas.vue'
import {type FiltrosAgenda} from '@/components/agenda/AgendaControles.vue'
import AgendaAba from '@/components/agenda/AgendaAba.vue'
import {getDuracaoAgendamento, getGrupoInfusao, somarDias} from '@/utils/utilsAgenda.ts'
import {Agendamento, AgendamentoStatusEnum, FarmaciaStatusEnum, TipoAgendamento} from "@/types/typesAgendamento.ts";
import {statusPermitidosSemCheckin} from "@/constants/constAgenda.ts";
import {getDataLocal} from '@/lib/utils.ts';
import {toast} from "vue-sonner";
import AgendamentoModalDetalhes from "@/components/comuns/AgendamentoModalDetalhes.vue";
import PrescricaoModalDetalhes from "@/components/comuns/PrescricaoModalDetalhes.vue";

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

const activeTipo = ref<TipoAgendamento>('infusao')

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

const filtrosInfusao = ref<FiltrosAgenda>(defaultFiltros())
const filtrosConsulta = ref<FiltrosAgenda>(defaultFiltros())
const filtrosProcedimento = ref<FiltrosAgenda>(defaultFiltros())

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

const agendamentosTipoAtivo = computed(() => agendamentosPorTipo.value[activeTipo.value])

const mostrarMetricas = ref(true)

const metricas = computed(() => {
  const list = agendamentosTipoAtivo.value

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

    <Tabs v-model="activeTipo" class="space-y-4">
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
        />
      </TabsContent>
    </Tabs>
  </div>
</template>
