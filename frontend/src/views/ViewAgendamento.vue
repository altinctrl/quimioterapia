<script lang="ts" setup>
import {onMounted} from 'vue'
import {useAppStore} from '@/stores/storeGeral.ts'
import {Button} from '@/components/ui/button'
import {ArrowLeft} from 'lucide-vue-next'
import {useRouter} from 'vue-router'
import AgendamentoBusca from '@/components/agendamento/AgendamentoBusca.vue'
import AgendamentoCalendario from '@/components/agendamento/AgendamentoCalendario.vue'
import AgendamentoResumo from '@/components/agendamento/AgendamentoResumo.vue'
import AgendamentoFormulario from '@/components/agendamento/AgendamentoFormulario.vue'
import AgendamentoModalConfirmacao from '@/components/agendamento/AgendamentoModalConfirmacao.vue'
import {useAgendamentoFormulario} from "@/composables/useAgendamentoFormulario.ts";
import {useAgendamentoCalendario} from "@/composables/useAgendamentoCalendario.ts";

const router = useRouter()
const appStore = useAppStore()

const {
  buscaPaciente,
  pacienteSelecionado,
  mostrarResultadosBusca,
  dataSelecionada,
  horarioInicio,
  encaixe,
  observacoes,
  tipoAgendamento,
  tipoConsulta,
  tipoProcedimento,
  prescricaoSelecionadaId,
  diaCiclo,
  confirmacaoOpen,
  listaAvisos,
  prescricoesFormatadas,
  diasPermitidosCiclo,
  grupoInfusaoAtual,
  diasSemanaPermitidosProtocolo,
  ultimoAgendamento,
  handleSelecionarPaciente,
  handleSelecionarData,
  preValidarAgendamento,
  realizarAgendamento
} = useAgendamentoFormulario()

const {
  mesSelecionado,
  anoSelecionado,
  diasDoMes,
  espacosVazios,
  isDiaBloqueado,
  getStatusVagas
} = useAgendamentoCalendario(tipoAgendamento, grupoInfusaoAtual, prescricaoSelecionadaId, diasSemanaPermitidosProtocolo)

onMounted(async () => {
  await Promise.all([
    appStore.fetchConfiguracoes(),
    appStore.fetchProtocolos()
  ])
})

const handleConfirmar = () => {
  const vagasInfo = getStatusVagas(dataSelecionada.value)
  preValidarAgendamento(vagasInfo)
}

const handlePrescricaoFisica = () => {
  if (!pacienteSelecionado.value) return
  router.push({
    name: 'Prescricao',
    query: {
      pacienteId: pacienteSelecionado.value.id,
      retorno: 'agendamento'
    }
  })
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div class="flex items-center gap-3">
      <Button size="icon" variant="ghost" @click="router.back()">
        <ArrowLeft class="h-5 w-5"/>
      </Button>
      <h1 class="text-2xl font-medium">Novo Agendamento</h1>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <AgendamentoBusca
            v-model:busca="buscaPaciente"
            v-model:mostrar-resultados="mostrarResultadosBusca"
            :resultados="appStore.resultadosBusca"
            @selecionar="handleSelecionarPaciente"
        />

        <AgendamentoCalendario
            v-if="pacienteSelecionado"
            v-model:ano="anoSelecionado"
            v-model:mes="mesSelecionado"
            :data-selecionada="dataSelecionada"
            :dias="diasDoMes"
            :espacos-vazios="espacosVazios"
            :get-info-vagas="getStatusVagas"
            :is-dia-bloqueado="isDiaBloqueado"
            @selecionar-data="handleSelecionarData"
        />
      </div>

      <div class="space-y-6">
        <AgendamentoResumo
            v-if="pacienteSelecionado"
            :paciente="pacienteSelecionado"
            :ultimo-agendamento="ultimoAgendamento"
        />

        <AgendamentoFormulario
            v-if="pacienteSelecionado"
            v-model:dia-ciclo="diaCiclo"
            v-model:encaixe="encaixe"
            v-model:horario="horarioInicio"
            v-model:observacoes="observacoes"
            v-model:prescricao-selecionada-id="prescricaoSelecionadaId"
            v-model:tipo="tipoAgendamento"
            v-model:tipo-consulta="tipoConsulta"
            v-model:tipo-procedimento="tipoProcedimento"
            :data-selecionada="dataSelecionada"
            :dias-permitidos="diasPermitidosCiclo"
            :horario-abertura="appStore.parametros.horarioAbertura"
            :horario-fechamento="appStore.parametros.horarioFechamento"
            :prescricoes-disponiveis="prescricoesFormatadas"
            @confirmar="handleConfirmar"
            @solicitar-prescricao-fisica="handlePrescricaoFisica"
        />
      </div>
    </div>

    <AgendamentoModalConfirmacao
        v-model:open="confirmacaoOpen"
        :avisos="listaAvisos"
        @confirmar="realizarAgendamento"
    />
  </div>
</template>
