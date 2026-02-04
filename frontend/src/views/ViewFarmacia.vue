<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/storeGeral.ts'
import {Agendamento, AgendamentoStatusEnum, FarmaciaStatusEnum} from "@/types/typesAgendamento.ts";
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import FarmaciaCabecalho from '@/components/farmacia/FarmaciaCabecalho.vue'
import FarmaciaMetricas from '@/components/farmacia/FarmaciaMetricas.vue'
import FarmaciaTabela, {type FarmaciaTableRow} from '@/components/farmacia/FarmaciaTabela.vue'
import FarmaciaControles, {type FiltrosFarmacia} from '@/components/farmacia/FarmaciaControles.vue'
import {getDataLocal} from '@/lib/utils.ts'
import {isInfusao, somarDias} from '@/utils/utilsAgenda.ts'
import AgendamentoModalDetalhes from "@/components/comuns/AgendamentoModalDetalhes.vue";
import PrescricaoModalDetalhes from "@/components/comuns/PrescricaoModalDetalhes.vue";
import {useLocalStorage, useSessionStorage} from "@vueuse/core";
import {toast} from 'vue-sonner'
import {useAutoRefresh} from "@/composables/useAutoRefresh.ts";

const router = useRouter()
const appStore = useAppStore()
const dataSelecionada = useSessionStorage('farmacia_data_selecionada', getDataLocal())

onMounted(() => {
  appStore.fetchConfiguracoes()
})

const STATUS_ORDER: Record<string, number> = {
  [FarmaciaStatusEnum.AGENDADO]: 0,
  [FarmaciaStatusEnum.AGUARDA_PRESCRICAO]: 1,
  [FarmaciaStatusEnum.VALIDANDO_PRESCRICAO]: 2,
  [FarmaciaStatusEnum.PENDENTE]: 3,
  [FarmaciaStatusEnum.EM_PREPARACAO]: 4,
  [FarmaciaStatusEnum.PRONTO]: 5,
  [FarmaciaStatusEnum.ENVIADO]: 6,
  [FarmaciaStatusEnum.MED_EM_FALTA]: 7,
  [FarmaciaStatusEnum.MED_JUD_EM_FALTA]: 8,
  [FarmaciaStatusEnum.SEM_PROCESSO]: 9,
  [FarmaciaStatusEnum.PRESCRICAO_DEVOLVIDA]: 10,
}

const filtros = useLocalStorage<FiltrosFarmacia>('farmacia_filtros', {
  ordenacao: 'horario',
  turno: 'todos',
  status: []
})

const mostrarMetricas = useLocalStorage('farmacia_mostrar_metricas', true)
const expandedIdsMap = useSessionStorage<Record<string, string[]>>('farmacia_listas_expandidas_map', {})
const selectedIds = ref<string[]>([])
const bulkStatus = ref<FarmaciaStatusEnum | ''>('')

const detalhesModalOpen = ref(false)
const agendamentoSelecionado = ref<Agendamento | null>(null)
const prescricaoModalOpen = ref(false)
const prescricaoParaVisualizar = ref<any>(null)

const isAlgumModalAberto = () => {
  return detalhesModalOpen.value || prescricaoModalOpen.value
}
const isSelecaoAtiva = () => selectedIds.value.length > 0

useAutoRefresh(
  async () => {
    await appStore.fetchAgendamentos(dataSelecionada.value, dataSelecionada.value)
  },
  {
    intervaloPadrao: 60000,
    condicoesPausa: [
      () => isAlgumModalAberto(),
      () => isSelecaoAtiva()
    ]
  }
)

const handleVerDetalhes = (row: FarmaciaTableRow) => {
  const ag = appStore.agendamentos.find(a => a.id === row.id)
  if (ag) {
    agendamentoSelecionado.value = ag
    detalhesModalOpen.value = true
  }
}

const handleAbrirPrescricao = (row: FarmaciaTableRow) => {
  const ag = appStore.agendamentos.find(a => a.id === row.id)
  if (ag && ag.prescricao) {
    prescricaoParaVisualizar.value = ag.prescricao
    prescricaoModalOpen.value = true
  }
}

const getStatusDotColor = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config ? config.cor.split(' ')[0] : 'bg-gray-200'
}

const agendamentosDoDia = computed(() => {
  return appStore.getAgendamentosDoDia(dataSelecionada.value).filter(ag =>
      ag.tipo === 'infusao' && ag.detalhes?.infusao
  )
})

const getUnidadeFinal = (unidade: string) => {
  if (!unidade) return ''
  if (unidade.includes('/')) {
    return unidade.split('/')[0]
  }
  return unidade
}

const tableRows = computed<FarmaciaTableRow[]>(() => {
  return agendamentosDoDia.value.map(ag => {
    const infoInfusao = ag.detalhes?.infusao;
    const prescricao = ag.prescricao;
    const diaCicloAtual = infoInfusao?.diaCiclo || 1;

    const itensPreparados = new Set(infoInfusao?.itensPreparados || []);

    const medicamentosRow: Array<{
      key: string;
      nome: string;
      dose: string;
      unidade: string;
      checked: boolean
    }> = [];

    if (prescricao && prescricao.conteudo && prescricao.conteudo.blocos) {
      prescricao.conteudo.blocos.forEach(bloco => {
        bloco.itens.forEach(item => {
          if (item.diasDoCiclo.includes(diaCicloAtual)) {
            const key = item.idItem || `${bloco.ordem}-${item.medicamento}`;

            medicamentosRow.push({
              key: key,
              nome: item.medicamento,
              dose: String(item.doseFinal),
              unidade: getUnidadeFinal(item.unidade),
              checked: itensPreparados.has(key)
            });
          }
        });
      });
    }

    const totalMeds = medicamentosRow.length;
    const totalChecked = medicamentosRow.filter(m => m.checked).length;
    const checklistLabel = totalMeds > 0 ? `${totalChecked}/${totalMeds}` : '-';

    const statusFarmacia = infoInfusao?.statusFarmacia || FarmaciaStatusEnum.PENDENTE;
    const bloqueado = [AgendamentoStatusEnum.SUSPENSO, AgendamentoStatusEnum.REMARCADO].includes(ag.status)

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
  get: () => {
    return expandedIdsMap.value[dataSelecionada.value] || []
  },
  set: (novosIds: string[]) => {
    expandedIdsMap.value = {
      ...expandedIdsMap.value,
      [dataSelecionada.value]: novosIds
    }
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

const handleResetFiltros = () => {
  filtros.value = {ordenacao: 'horario', turno: 'todos', status: []}
}

const handleAlterarStatus = (agendamentoId: string, novoStatus: FarmaciaStatusEnum) => {
  appStore.atualizarStatusFarmacia(agendamentoId, novoStatus)
}

const handleAlterarHorario = (agendamentoId: string, novoHorario: string) => {
  appStore.atualizarHorarioPrevisao(agendamentoId, novoHorario)
}

const handleNavigatePaciente = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const handleToggleCheckItem = async (agId: string, itemKey: string, statusAtual: FarmaciaStatusEnum) => {
  const agendamento = appStore.agendamentos.find(a => a.id === agId)
  if (!agendamento || !isInfusao(agendamento)) return

  const rowAtual = tableRows.value.find(r => r.id === agId)
  if (!rowAtual) return
  const currentChecklist = new Set(agendamento.detalhes.infusao.itensPreparados || [])

  if (currentChecklist.has(itemKey)) {
    currentChecklist.delete(itemKey)
  } else {
    currentChecklist.add(itemKey)
  }
  const novoChecklist = Array.from(currentChecklist)

  const totalChecked = currentChecklist.size
  const totalItens = rowAtual.medicamentos.length || 0

  let proximoStatus: FarmaciaStatusEnum | null = null
  if (statusAtual === FarmaciaStatusEnum.PENDENTE && totalChecked > 0) {
    proximoStatus = FarmaciaStatusEnum.EM_PREPARACAO
  } else if (totalChecked === totalItens && totalItens > 0 && statusAtual !== FarmaciaStatusEnum.PRONTO) {
    proximoStatus = FarmaciaStatusEnum.PRONTO
  } else if (totalChecked < totalItens && statusAtual === FarmaciaStatusEnum.PRONTO) {
    proximoStatus = FarmaciaStatusEnum.EM_PREPARACAO
  }

  try {
    await appStore.salvarChecklistFarmacia(agId, novoChecklist)
    if (proximoStatus && proximoStatus !== statusAtual) {
      handleAlterarStatus(agId, proximoStatus)
    }
  } catch (error) {
    console.error("Erro ao sincronizar farmácia", error)
  }
}

const metricas = computed(() => {
  const rows = tableRows.value
  return {
    total: rows.length,
    pendente: rows.filter(r => r.statusFarmacia === FarmaciaStatusEnum.PENDENTE).length,
    emPreparacao: rows.filter(r => r.statusFarmacia === FarmaciaStatusEnum.EM_PREPARACAO).length,
    pronta: rows.filter(r => r.statusFarmacia === FarmaciaStatusEnum.PRONTO).length,
    enviada: rows.filter(r => r.statusFarmacia === FarmaciaStatusEnum.ENVIADO).length
  }
})

const selectedRows = computed(() => {
  const ids = new Set(selectedIds.value)
  return viewRows.value.filter(r => ids.has(r.id))
})

const limparSelecao = () => {
  selectedIds.value = []
  bulkStatus.value = ''
}

const aplicarStatusLote = async () => {
  if (!bulkStatus.value) {
    toast.error('Selecione um status para aplicar.')
    return
  }

  const selecionados = selectedRows.value
  if (selecionados.length === 0) return

  const itensParaAtualizar: any[] = []
  let bloqueadosCount = 0

  selecionados.forEach(row => {
    if (row.statusBloqueado) {
      bloqueadosCount++
      return
    }

    if (row.statusFarmacia !== bulkStatus.value) {
      itensParaAtualizar.push({
        id: row.id,
        detalhes: {
          infusao: {
            status_farmacia: bulkStatus.value
          }
        }
      })
    }
  })

  if (itensParaAtualizar.length === 0) {
    if (bloqueadosCount > 0) {
      toast.warning('Nenhum item válido para atualizar.')
    } else {
      toast.info('Todos os itens já estão com este status.')
    }
    limparSelecao()
    return
  }

  try {
    await appStore.atualizarAgendamentosEmLote(itensParaAtualizar)

    if (bloqueadosCount > 0) {
      toast.warning(`${bloqueadosCount} itens bloqueados foram ignorados.`)
    }

    limparSelecao()
  } catch (error) {
    console.error("Erro na atualização em lote da farmácia", error)
  }
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
            <Button class="h-8" size="sm" variant="outline" @click="limparSelecao">
              Cancelar
            </Button>
            <Button class="h-8" size="sm" @click="aplicarStatusLote">
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
