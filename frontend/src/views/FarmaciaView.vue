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

    const medicamentos = listaMedicamentos.map((med, idx) => {
      const key = `${med.tipo}:${med.id ?? idx}:${med.nome}`
      return {
        key,
        nome: med.nome,
        dose: med.dose?.toString() || '',
        unidade: med.unidade || '',
        checked: checklist.value[ag.id]?.[key] || false
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

const allExpanded = computed(() => {
  const ids = viewRows.value.map(r => r.id)
  if (ids.length === 0) return false
  const expanded = new Set(expandedIds.value)
  return ids.every(id => expanded.has(id))
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

const handleToggleExpandAll = () => {
  const ids = viewRows.value.map(r => r.id)
  if (ids.length === 0) {
    expandedIds.value = []
    return
  }
  expandedIds.value = allExpanded.value ? [] : ids
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

const handleToggleCheckItem = (agId: string, itemKey: string, statusAtual: StatusFarmacia) => {
  if (!checklist.value[agId]) checklist.value[agId] = {}
  checklist.value[agId][itemKey] = !checklist.value[agId][itemKey]

  const checks = checklist.value[agId]
  const values = Object.values(checks)
  const totalChecked = values.filter(Boolean).length

  if (statusAtual === 'pendente' && totalChecked > 0) {
    handleAlterarStatus(agId, 'em-preparacao')
  }

  const row = viewRows.value.find(r => r.id === agId)
  if (row && row.medicamentos.length > 0 && totalChecked === row.medicamentos.length) {
    handleAlterarStatus(agId, 'pronta')
  }
}

const metricas = computed(() => {
  const infusoes = agendamentosFiltrados.value.filter(isInfusao)
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
            @reset="handleResetFiltros"
            @toggle-expand-all="handleToggleExpandAll"
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
