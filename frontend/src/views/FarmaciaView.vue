<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {isInfusao, type StatusFarmacia} from '@/types'
import {Card, CardContent} from '@/components/ui/card'
import FarmaciaHeader from '@/components/farmacia/FarmaciaHeader.vue'
import FarmaciaMetrics from '@/components/farmacia/FarmaciaMetrics.vue'
import FarmaciaTable, {type FarmaciaTableRow} from '@/components/farmacia/FarmaciaTable.vue'
import FarmaciaControls, {type FiltrosFarmacia} from '@/components/farmacia/FarmaciaControls.vue'
import {getDataLocal} from '@/lib/utils.ts'
import {somarDias} from '@/utils/agendaUtils.ts'

const router = useRouter()
const appStore = useAppStore()
const dataSelecionada = ref(getDataLocal())

const STATUS_ORDER: Record<string, number> = {
  'pendente': 0,
  'em-preparacao': 1,
  'pronta': 2,
  'enviada': 3
}

const filtros = ref<FiltrosFarmacia>({
  ordenacao: 'horario',
  turno: 'todos',
  status: []
})

const mostrarMetricas = ref(true)
const expandedIds = ref<string[]>([])
const checklist = ref<Record<string, Record<string, boolean>>>({})

const getStatusDotColor = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config ? config.cor.split(' ')[0] : 'bg-gray-200'
}

const agendamentosFiltrados = computed(() => {
  let lista = [...appStore.agendamentos]

  if (filtros.value.turno !== 'todos') {
    lista = lista.filter(a => a.turno === filtros.value.turno)
  }

  if (filtros.value.status.length > 0) {
    lista = lista.filter(a => {
      if (!isInfusao(a)) return false
      return filtros.value.status.includes(a.detalhes.infusao.status_farmacia)
    })
  }

  return lista.sort((a, b) => {
    if (filtros.value.ordenacao === 'horario') {
      return a.horarioInicio.localeCompare(b.horarioInicio)
    }
    if (filtros.value.ordenacao === 'status') {
      const sa = isInfusao(a) ? a.detalhes.infusao.status_farmacia : 'pendente'
      const sb = isInfusao(b) ? b.detalhes.infusao.status_farmacia : 'pendente'
      if (STATUS_ORDER[sa] !== STATUS_ORDER[sb]) return STATUS_ORDER[sa] - STATUS_ORDER[sb]
      return a.horarioInicio.localeCompare(b.horarioInicio)
    }
    return a.horarioInicio.localeCompare(b.horarioInicio)
  })
})

const viewRows = computed<FarmaciaTableRow[]>(() => {
  return agendamentosFiltrados.value.map(ag => {
    const listaMedicamentos = ag.prescricao?.qt || []
    const hasMedicamentos = listaMedicamentos.length > 0
    const savedChecklist = (isInfusao(ag) ? ag.detalhes.infusao.checklist_farmacia : {}) || {}

    const medicamentos = listaMedicamentos.map((med, idx) => {
      const key = `${med.tipo}:${med.id ?? idx}:${med.nome}`
      return {
        key,
        nome: med.nome,
        dose: med.dose?.toString() || '',
        unidade: med.unidade || '',
        checked: savedChecklist[key] || false
      }
    })

    let checklistLabel = ''
    if (hasMedicamentos) {
      const checks = checklist.value[ag.id] || {}
      let checkedCount = 0
      medicamentos.forEach(m => {
        if (checks[m.key]) checkedCount++
      })
      checklistLabel = `${checkedCount}/${medicamentos.length}`
    }

    const protocolo = appStore.getProtocoloPeloHistorico(ag.pacienteId)
    const statusFarmacia = isInfusao(ag) ? ag.detalhes.infusao.status_farmacia : 'pendente'
    const bloqueado = ['suspenso', 'remarcado'].includes(ag.status)

    return {
      id: ag.id,
      pacienteId: ag.pacienteId,
      horario: ag.horarioInicio,
      pacienteNome: ag.paciente?.nome || 'Paciente não carregado',
      pacienteRegistro: ag.paciente?.registro || '',
      observacoesClinicas: ag.paciente?.observacoesClinicas,
      protocoloNome: ag.prescricao?.protocolo || protocolo?.nome || '-',
      statusTexto: ag.status ? ag.status.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '',
      statusBloqueado: bloqueado,
      statusFarmacia: statusFarmacia,
      statusFarmaciaCor: getStatusDotColor(bloqueado ? 'pendente' : statusFarmacia),
      previsaoEntrega: isInfusao(ag) ? ag.detalhes.infusao.horario_previsao_entrega || '' : '',
      medicamentos,
      checklistLabel,
      hasMedicamentos
    }
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

const handleAlterarStatus = (agendamentoId: string, novoStatus: StatusFarmacia) => {
  appStore.atualizarStatusFarmacia(agendamentoId, novoStatus)
}

const handleAlterarHorario = (agendamentoId: string, novoHorario: string) => {
  appStore.atualizarHorarioPrevisao(agendamentoId, novoHorario)
}

const handleNavigatePaciente = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const handleToggleCheckItem = async (agId: string, itemKey: string, statusAtual: StatusFarmacia) => {
  const agendamento = appStore.agendamentos.find(a => a.id === agId)
  if (!agendamento || !isInfusao(agendamento)) return

  const currentChecklist = agendamento.detalhes.infusao.checklist_farmacia || {}
  const novoValor = !currentChecklist[itemKey]
  const novoChecklist = {...currentChecklist, [itemKey]: novoValor}
  agendamento.detalhes.infusao.checklist_farmacia = novoChecklist

  const values = Object.values(novoChecklist)
  const totalChecked = values.filter(Boolean).length
  const totalItens = agendamento.prescricao?.qt?.length || Object.keys(currentChecklist).length || 0

  let proximoStatus: StatusFarmacia | null = null
  if (statusAtual === 'pendente' && totalChecked > 0) {
    proximoStatus = 'em-preparacao'
  } else if (totalChecked === totalItens && totalItens > 0 && statusAtual !== 'pronta') {
    proximoStatus = 'pronta'
  } else if (totalChecked < totalItens && statusAtual === 'pronta') {
    proximoStatus = 'em-preparacao'
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
  const infusoes = appStore.agendamentos.filter(isInfusao)
  const total = infusoes.length
  const pendente = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'pendente').length
  const emPreparacao = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'em-preparacao').length
  const pronta = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'pronta').length
  const enviada = infusoes.filter(a => a.detalhes.infusao.status_farmacia === 'enviada').length
  return {total, pendente, emPreparacao, pronta, enviada}
})

const opcoesStatusFarmacia = computed(() => {
  return appStore.statusConfig.filter(s => s.tipo === 'farmacia')
})

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
}, {immediate: true})

watch(agendamentosFiltrados, (lista) => {
  const ids = new Set(lista.map(a => a.id))
  expandedIds.value = expandedIds.value.filter(id => ids.has(id))
})
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Farmácia</h1>

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
            @click-paciente="handleNavigatePaciente"
            @toggle-check-item="handleToggleCheckItem"
        />
      </CardContent>
    </Card>
  </div>
</template>
