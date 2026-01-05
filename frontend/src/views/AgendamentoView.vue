<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Button} from '@/components/ui/button'
import {ArrowLeft} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import type {GrupoInfusao, Paciente, Turno} from '@/types'

import AgendamentoBusca from '@/components/agendamento/AgendamentoBusca.vue'
import AgendamentoCalendario from '@/components/agendamento/AgendamentoCalendario.vue'
import AgendamentoResumo from '@/components/agendamento/AgendamentoResumo.vue'
import AgendamentoForm from '@/components/agendamento/AgendamentoForm.vue'
import AgendamentoConfirmacaoModal from '@/components/agendamento/AgendamentoConfirmacaoModal.vue'

const router = useRouter()
const appStore = useAppStore()

const buscaPaciente = ref('')
const pacienteSelecionado = ref<Paciente | null>(null)
const mostrarResultados = ref(false)

const mesSelecionado = ref(String(new Date().getMonth() + 1))
const anoSelecionado = ref(String(new Date().getFullYear()))
const dataSelecionada = ref('')

const horarioInicio = ref('')
const diaCiclo = ref('D1')
const observacoes = ref('')

const confirmacaoOpen = ref(false)
const listaAvisos = ref<string[]>([])

let timeoutBusca: ReturnType<typeof setTimeout>

watch(buscaPaciente, (novoTermo) => {
  clearTimeout(timeoutBusca)
  timeoutBusca = setTimeout(() => {
    appStore.buscarPacientesDropdown(novoTermo)
    mostrarResultados.value = true
  }, 300)
})

const protocolo = computed(() => {
  if (!pacienteSelecionado.value) return null
  return appStore.getProtocoloPeloHistorico(pacienteSelecionado.value.id)
})

const grupoInfusaoAtual = computed((): GrupoInfusao => {
  return protocolo.value?.grupoInfusao || 'medio'
})

const ultimoAgendamento = computed(() => {
  if (!pacienteSelecionado.value) return null
  const agendamentos = appStore.agendamentos
      .filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
  return agendamentos[0] || null
})

const handleSelecionarPaciente = (p: Paciente) => {
  pacienteSelecionado.value = p
  buscaPaciente.value = p.nome
  mostrarResultados.value = false
  if (ultimoAgendamento.value) {
    const lastDayNum = parseInt(ultimoAgendamento.value.diaCiclo?.replace(/\D/g, '') || '0')
    diaCiclo.value = `D${lastDayNum + 7}`
  }
  dataSelecionada.value = ''
  horarioInicio.value = ''
  listaAvisos.value = []
}

const handleSelecionarData = (data: string) => {
  dataSelecionada.value = data
  horarioInicio.value = ''
  listaAvisos.value = []
}

const getVagasInfo = (data: string) => {
  const grupo = grupoInfusaoAtual.value
  const limiteGrupo = appStore.parametros.gruposInfusao[grupo]?.vagas || 4
  const agendamentosNoDia = appStore.getAgendamentosDoDia(data)

  const countNoGrupo = agendamentosNoDia.reduce((acc, ag) => {
    const p = appStore.getPacienteById(ag.pacienteId)
    const prot = appStore.getProtocoloById(p?.protocoloId || '')
    const g = prot?.grupoInfusao || 'medio'
    return g === grupo ? acc + 1 : acc
  }, 0)

  const vagasRestantes = limiteGrupo - countNoGrupo
  return {count: vagasRestantes, full: vagasRestantes <= 0}
}

const preValidarAgendamento = () => {
  listaAvisos.value = []

  if (!pacienteSelecionado.value || !dataSelecionada.value || !horarioInicio.value) {
    toast.error('Preencha todos os campos obrigatórios')
    return
  }

  const agendamentosDia = appStore.getAgendamentosDoDia(dataSelecionada.value)
  if (agendamentosDia.some(a => a.pacienteId === pacienteSelecionado.value?.id)) {
    listaAvisos.value.push(`O paciente já possui um agendamento para esta data (${new Date(dataSelecionada.value).toLocaleDateString('pt-BR')}).`)
  }

  const vagasInfo = getVagasInfo(dataSelecionada.value)
  if (vagasInfo.full) {
    listaAvisos.value.push(`A capacidade para o grupo "${grupoInfusaoAtual.value}" está esgotada neste dia.`)
  }

  const abertura = appStore.parametros.horarioAbertura
  const fechamento = appStore.parametros.horarioFechamento

  const [hIni, mIni] = horarioInicio.value.split(':').map(Number)
  const inicioMin = hIni * 60 + mIni

  const [hAbe, mAbe] = abertura.split(':').map(Number)
  const aberturaMin = hAbe * 60 + mAbe

  const [hFec, mFec] = fechamento.split(':').map(Number)
  const fechamentoMin = hFec * 60 + mFec

  if (inicioMin < aberturaMin) {
    listaAvisos.value.push(`O horário de início (${horarioInicio.value}) é anterior à abertura da clínica (${abertura}).`)
  }

  if (inicioMin > fechamentoMin) {
    listaAvisos.value.push(`O horário de início (${horarioInicio.value}) é após o fechamento da clínica (${fechamento}).`)
  }

  if (listaAvisos.value.length > 0) {
    confirmacaoOpen.value = true
  } else {
    realizarAgendamento()
  }
}

const realizarAgendamento = async () => {
  confirmacaoOpen.value = false

  const [hIni] = horarioInicio.value.split(':').map(Number)
  const turnoInferido: Turno = hIni < 13 ? 'manha' : 'tarde'

  try {
    await appStore.adicionarAgendamento({
      pacienteId: pacienteSelecionado.value!.id,
      data: dataSelecionada.value,
      turno: turnoInferido,
      horarioInicio: horarioInicio.value,
      horarioFim: '00:00',
      status: 'agendado',
      statusFarmacia: 'pendente',
      encaixe: listaAvisos.value.length > 0,
      observacoes: observacoes.value,
      diaCiclo: diaCiclo.value,
      cicloAtual: ultimoAgendamento.value ? (ultimoAgendamento.value.cicloAtual || 1) : 1
    })

    toast.success('Agendamento realizado com sucesso!')
    router.back()

  } catch (error) {
    console.error(error)
  }
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
            v-model:mostrar-resultados="mostrarResultados"
            :resultados="appStore.resultadosBusca"
            @selecionar="handleSelecionarPaciente"
        />

        <AgendamentoCalendario
            v-if="pacienteSelecionado"
            v-model:ano="anoSelecionado"
            v-model:mes="mesSelecionado"
            :data-selecionada="dataSelecionada"
            :grupo-infusao="grupoInfusaoAtual"
            @selecionar-data="handleSelecionarData"
        />
      </div>

      <div class="space-y-6">
        <AgendamentoResumo
            v-if="pacienteSelecionado"
            :paciente="pacienteSelecionado"
            :protocolo="protocolo"
            :ultimo-agendamento="ultimoAgendamento"
        />

        <AgendamentoForm
            v-if="dataSelecionada"
            v-model:dia-ciclo="diaCiclo"
            v-model:horario="horarioInicio"
            v-model:observacoes="observacoes"
            :horario-abertura="appStore.parametros.horarioAbertura"
            :horario-fechamento="appStore.parametros.horarioFechamento"
            :ultimo-agendamento="ultimoAgendamento"
            @confirmar="preValidarAgendamento"
        />
      </div>
    </div>

    <AgendamentoConfirmacaoModal
        v-model:open="confirmacaoOpen"
        :avisos="listaAvisos"
        @confirmar="realizarAgendamento"
    />
  </div>
</template>