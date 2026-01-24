<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Agendamento, AgendamentoStatusEnum, FarmaciaStatusEnum, isInfusao} from '@/types'
import {Card, CardContent} from '@/components/ui/card'
import FarmaciaHeader from '@/components/farmacia/FarmaciaHeader.vue'
import FarmaciaMetrics from '@/components/farmacia/FarmaciaMetrics.vue'
import FarmaciaTable, {type FarmaciaTableRow} from '@/components/farmacia/FarmaciaTable.vue'
import FarmaciaControls, {type FiltrosFarmacia} from '@/components/farmacia/FarmaciaControls.vue'
import {getDataLocal} from '@/lib/utils.ts'
import {somarDias} from '@/utils/agendaUtils.ts'
import AgendamentoDetalhesModal from "@/components/modals/AgendamentoDetalhesModal.vue";
import PrescricaoHistoricoModal from "@/components/modals/PrescricaoHistoricoModal.vue";

const router = useRouter()
const appStore = useAppStore()
const dataSelecionada = ref(getDataLocal())

onMounted(() => {
  appStore.fetchConfiguracoes()
})

const STATUS_ORDER: Record<string, number> = {
  [FarmaciaStatusEnum.AGUARDA_PRESCRICAO]: 0,
  [FarmaciaStatusEnum.VALIDANDO_PRESCRICAO]: 1,
  [FarmaciaStatusEnum.PENDENTE]: 2,
  [FarmaciaStatusEnum.EM_PREPARACAO]: 3,
  [FarmaciaStatusEnum.PRONTO]: 4,
  [FarmaciaStatusEnum.ENVIADO]: 5,
  [FarmaciaStatusEnum.MED_EM_FALTA]: 6,
  [FarmaciaStatusEnum.MED_JUD_EM_FALTA]: 7,
  [FarmaciaStatusEnum.SEM_PROCESSO]: 8,
  [FarmaciaStatusEnum.PRESCRICAO_DEVOLVIDA]: 9,
}

const filtros = ref<FiltrosFarmacia>({
  ordenacao: 'horario',
  turno: 'todos',
  status: []
})

const mostrarMetricas = ref(true)
const expandedIds = ref<string[]>([])

const detalhesModalOpen = ref(false)
const agendamentoSelecionado = ref<Agendamento | null>(null)
const prescricaoModalOpen = ref(false)
const prescricaoParaVisualizar = ref<any>(null)

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

const handleDiaAnterior = () => {
  dataSelecionada.value = somarDias(dataSelecionada.value, -1)
}

const handleProximoDia = () => {
  dataSelecionada.value = somarDias(dataSelecionada.value, 1)
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
  expandedIds.value = expandedIds.value.filter(id => idsVisiveis.has(id))
})
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Farmácia</h1>

    <AgendamentoDetalhesModal
        v-model:open="detalhesModalOpen"
        :agendamento="agendamentoSelecionado"
        :paciente-nome="agendamentoSelecionado?.paciente?.nome"
    />

    <PrescricaoHistoricoModal
        v-if="prescricaoParaVisualizar"
        v-model:open="prescricaoModalOpen"
        :prescricao="prescricaoParaVisualizar"
    />

    <FarmaciaHeader
        v-model="dataSelecionada"
        :mostrar-metricas="mostrarMetricas"
        @dia-anterior="handleDiaAnterior"
        @proximo-dia="handleProximoDia"
        @toggle-metrics="mostrarMetricas = !mostrarMetricas"
    />

    <FarmaciaMetrics
        v-if="mostrarMetricas"
        :metricas="metricas"
    />

    <Card class="overflow-hidden">
      <div class="px-4 pt-4">
        <FarmaciaControls
            v-model="filtros"
            @reset="handleResetFiltros"
        />
      </div>

      <CardContent class="p-0 mt-0">
        <FarmaciaTable
            v-model:expanded-ids="expandedIds"
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
