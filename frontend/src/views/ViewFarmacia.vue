<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/storeGeral.ts'
import {FarmaciaStatusEnum, FarmaciaTableRow} from "@/types/typesAgendamento.ts";
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import FarmaciaCabecalho from '@/components/farmacia/FarmaciaCabecalho.vue'
import FarmaciaMetricas from '@/components/farmacia/FarmaciaMetricas.vue'
import FarmaciaTabela from '@/components/farmacia/FarmaciaTabela.vue'
import FarmaciaControles from '@/components/farmacia/FarmaciaControles.vue'
import AgendamentoModalDetalhes from "@/components/comuns/AgendamentoModalDetalhes.vue";
import PrescricaoModalDetalhes from "@/components/comuns/PrescricaoModalDetalhes.vue";
import {useAutoRefresh} from "@/composables/useAutoRefresh.ts";
import {STATUS_ORDER} from "@/constants/constFarmacia.ts";
import {useAgendaNavegacao} from "@/composables/useAgendaNavegacao.ts";
import {useAgendaModals} from "@/composables/useAgendaModals.ts";
import {useFarmaciaOperacoes} from "@/composables/useFarmaciaOperacoes.ts";
import {useFarmaciaDados} from "@/composables/useFarmaciaDados.ts";

const router = useRouter()
const appStore = useAppStore()

const {
  dataSelecionada,
  handleHoje,
  handleDiaAnterior,
  handleProximoDia,
} = useAgendaNavegacao('farmacia_data_selecionada')

const {
  detalhesModalOpen,
  agendamentoSelecionado,
  abrirDetalhesAgendamento,
  prescricaoModalOpen,
  prescricaoParaVisualizar,
  abrirPrescricao,
  isAlgumModalAberto
} = useAgendaModals()

const {
  filtros,
  mostrarMetricas,
  selectedIds,
  viewRows,
  metricas,
  expandedIdsDoDia,
  handleResetFiltros,
  limparSelecao
} = useFarmaciaDados(dataSelecionada)

const {
  alterarStatusFarmacia: handleAlterarStatus,
  alterarHorarioPrevisao: handleAlterarHorario,
  aplicarStatusFarmaciaLote: aplicarStatusLote,
  toggleItemChecklist,
} = useFarmaciaOperacoes()

onMounted(() => {
  appStore.fetchConfiguracoes()
})

const bulkStatus = ref<FarmaciaStatusEnum | ''>('')
const isSelecaoAtiva = () => selectedIds.value.length > 0

useAutoRefresh(
    async () => {
      await appStore.fetchAgendamentos(dataSelecionada.value, dataSelecionada.value)
    },
    {
      intervaloPadrao: 60000,
      condicoesPausa: [
        () => isAlgumModalAberto.value,
        () => isSelecaoAtiva()
      ]
    }
)

const handleVerDetalhes = (row: FarmaciaTableRow) => {
  const ag = appStore.agendamentos.find(a => a.id === row.id)
  abrirDetalhesAgendamento(ag)
}

const handleAbrirPrescricao = (row: FarmaciaTableRow) => {
  const ag = appStore.agendamentos.find(a => a.id === row.id)
  abrirPrescricao(ag)
}

const handleNavigatePaciente = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const handleToggleCheckItem = async (agId: string, itemKey: string, statusAtual: FarmaciaStatusEnum) => {
  const row = viewRows.value.find(r => r.id === agId)
  const totalItens = row?.medicamentos.length || 0
  await toggleItemChecklist(agId, itemKey, statusAtual, totalItens)
}

const selectedRows = computed(() => {
  const ids = new Set(selectedIds.value)
  return viewRows.value.filter(r => ids.has(r.id))
})

const handleLimparSelecao = () => {
  limparSelecao()
  bulkStatus.value = ''
}

const handleAplicarStatusLote = async () => {
  await aplicarStatusLote(selectedRows.value, bulkStatus.value as FarmaciaStatusEnum)
  handleLimparSelecao()
}

const opcoesStatusFarmacia = computed(() => {
  return appStore.statusConfig
      .filter(s => s.tipo === 'farmacia')
      .sort((a, b) => {
        const rankA = STATUS_ORDER[a.id] ?? 99
        const rankB = STATUS_ORDER[b.id] ?? 99
        return rankA - rankB
      })
})

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
}, {immediate: true})

watch(viewRows, (lista) => {
  const idsVisiveis = new Set(lista.map(r => r.id))
  selectedIds.value = selectedIds.value.filter(id => idsVisiveis.has(id))
})
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Farmácia</h1>

    <AgendamentoModalDetalhes
        v-model:open="detalhesModalOpen"
        :agendamento="agendamentoSelecionado"
        :paciente-nome="agendamentoSelecionado?.paciente?.nome"
    />

    <PrescricaoModalDetalhes
        v-if="prescricaoParaVisualizar"
        v-model:open="prescricaoModalOpen"
        :prescricao="prescricaoParaVisualizar"
    />

    <FarmaciaCabecalho
        v-model="dataSelecionada"
        :mostrar-metricas="mostrarMetricas"
        @dia-anterior="handleDiaAnterior"
        @proximo-dia="handleProximoDia"
        @toggle-metrics="mostrarMetricas = !mostrarMetricas"
        @go-today="handleHoje"
    />

    <FarmaciaMetricas
        v-if="mostrarMetricas"
        :metricas="metricas"
    />

    <Card class="overflow-hidden">
      <div class="px-4 pt-4">
        <FarmaciaControles
            v-model="filtros"
            @reset="handleResetFiltros"
        />
      </div>

      <div v-if="selectedIds.length" class="px-4 py-3">
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between bg-blue-50 border border-blue-100 rounded-md p-3">
          <span class="text-sm font-medium text-blue-700">
            {{ selectedIds.length }} selecionados
          </span>
          <div class="flex flex-wrap items-center gap-2">
            <select
                v-model="bulkStatus"
                class="flex h-8 min-w-[200px] items-center justify-between rounded-md border border-input bg-white
                px-2 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none
                focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <option disabled value="">Alterar status...</option>
              <option
                  v-for="opcao in opcoesStatusFarmacia"
                  :key="opcao.id"
                  :value="opcao.id"
              >
                {{ opcao.label }}
              </option>
            </select>
            <Button class="h-8" size="sm" variant="outline" @click="handleLimparSelecao">
              Cancelar
            </Button>
            <Button class="h-8" size="sm" @click="handleAplicarStatusLote">
              Confirmar
            </Button>
          </div>
        </div>
      </div>

      <CardContent class="p-0 mt-0">
        <FarmaciaTabela
            v-model:expanded-ids="expandedIdsDoDia"
            v-model:selected-ids="selectedIds"
            :opcoes-status="opcoesStatusFarmacia"
            :rows="viewRows"
            @alterar-status="handleAlterarStatus"
            @alterar-horario="handleAlterarHorario"
            @abrir-detalhes="handleVerDetalhes"
            @abrir-prescricao="handleAbrirPrescricao"
            @click-paciente="handleNavigatePaciente"
            @toggle-check-item="handleToggleCheckItem"
        />
      </CardContent>
    </Card>
  </div>
</template>
