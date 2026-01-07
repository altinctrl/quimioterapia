<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useAppStore} from '@/stores/app'
import {isInfusao, type StatusFarmacia} from '@/types'
import FarmaciaHeader from '@/components/farmacia/FarmaciaHeader.vue'
import FarmaciaMetrics from '@/components/farmacia/FarmaciaMetrics.vue'
import FarmaciaTable from '@/components/farmacia/FarmaciaTable.vue'

const appStore = useAppStore()
const dataSelecionada = ref(new Date().toISOString().split('T')[0])

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

const agendamentosDoDia = computed(() => {
  return appStore.agendamentos
      .filter(a => a.data === dataSelecionada.value)
      .sort((a, b) => a.horarioInicio.localeCompare(b.horarioInicio))
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

    <FarmaciaTable
        :agendamentos="agendamentosDoDia"
        @alterar-status="handleAlterarStatus"
        @alterar-horario="handleAlterarHorario"
    />
  </div>
</template>