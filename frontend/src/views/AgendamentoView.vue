<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Button} from '@/components/ui/button'
import {ArrowLeft} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import {
  GrupoInfusao,
  TipoAgendamento,
  TipoConsultaEnum,
  TipoProcedimentoEnum,
  Turno
} from "@/types/agendamentoTypes.ts";
import {Paciente} from "@/types/pacienteTypes.ts";
import AgendamentoBusca from '@/components/agendamento/AgendamentoBusca.vue'
import AgendamentoCalendario from '@/components/agendamento/AgendamentoCalendario.vue'
import AgendamentoResumo from '@/components/agendamento/AgendamentoResumo.vue'
import AgendamentoForm, {PrescricaoComLabel} from '@/components/agendamento/AgendamentoForm.vue'
import AgendamentoConfirmacaoModal from '@/components/agendamento/AgendamentoConfirmacaoModal.vue'

const router = useRouter()
const appStore = useAppStore()

onMounted(async () => {
  await Promise.all([
    appStore.fetchConfiguracoes(),
    appStore.fetchProtocolos()
  ])
})

const buscaPaciente = ref('')
const pacienteSelecionado = ref<Paciente | null>(null)
const mostrarResultados = ref(false)

const mesSelecionado = ref(String(new Date().getMonth() + 1))
const anoSelecionado = ref(String(new Date().getFullYear()))
const dataSelecionada = ref('')

const tipoAgendamento = ref<TipoAgendamento>('infusao')
const tipoConsulta = ref<TipoConsultaEnum | ''>('')
const tipoProcedimento = ref<TipoProcedimentoEnum | ''>('')

const horarioInicio = ref('')
const diaCiclo = ref<number | null>(null)
const encaixe = ref(false)
const observacoes = ref('')
const prescricaoSelecionadaId = ref('')

const confirmacaoOpen = ref(false)
const listaAvisos = ref<string[]>([])

let timeoutBusca: ReturnType<typeof setTimeout>

watch(buscaPaciente, (novoTermo) => {
  clearTimeout(timeoutBusca)
  timeoutBusca = setTimeout(() => {
    if (novoTermo.length >= 3) {
      appStore.buscarPacientesDropdown(novoTermo)
      mostrarResultados.value = true
    }
  }, 300)
})

watch(pacienteSelecionado, async (novoPaciente) => {
  if (novoPaciente) {
    await Promise.all([
      appStore.fetchPrescricoes(novoPaciente.id),
      appStore.fetchAgendamentos(undefined, undefined, novoPaciente.id)
    ])
  }
})

const prescricoesDisponiveis = computed(() => {
  if (!pacienteSelecionado.value) return []
  return appStore.prescricoes.filter(p =>
      p.pacienteId === pacienteSelecionado.value?.id &&
      ['pendente', 'em-curso'].includes(p.status)
  )
})

const prescricaoAtual = computed(() => {
  return prescricoesDisponiveis.value.find(p => p.id === prescricaoSelecionadaId.value)
})

const diasPermitidosCiclo = computed(() => {
  if (!prescricaoAtual.value) return []
  const diasTeoricos = new Set<number>()

  prescricaoAtual.value.conteudo.blocos.forEach(bloco => {
    bloco.itens.forEach(item => {
      item.diasDoCiclo.forEach(d => diasTeoricos.add(d))
    })
  })

  const diasJaAgendados = appStore.agendamentos
      .filter(ag =>
          ag.tipo === 'infusao' &&
          ag.detalhes?.infusao?.prescricaoId === prescricaoAtual.value?.id &&
          ag.status !== 'remarcado' &&
          ag.status !== 'suspenso'
      )
      .map(ag => ag.detalhes?.infusao?.diaCiclo)

  diasJaAgendados.forEach(d => diasTeoricos.delete(d || 0))

  return Array.from(diasTeoricos).sort((a, b) => a - b)
})

watch(prescricaoSelecionadaId, () => {
  if (diasPermitidosCiclo.value.length > 0) {
    diaCiclo.value = diasPermitidosCiclo.value[0]
  } else {
    diaCiclo.value = null
  }
})

const grupoInfusaoAtual = computed((): GrupoInfusao => {
  if (tipoAgendamento.value !== 'infusao' || !prescricaoAtual.value) return 'medio'

  const protoNome = prescricaoAtual.value.conteudo.protocolo.nome
  const protocoloFull = appStore.protocolos.find(p => p.nome === protoNome)

  if (protocoloFull && protocoloFull.tempoTotalMinutos) {
    if (protocoloFull.tempoTotalMinutos < 120) return 'rapido'
    if (protocoloFull.tempoTotalMinutos <= 240) return 'medio'
    return 'longo'
  }
  return 'medio'
})

const requisitosTipoOk = computed(() => {
  if (tipoAgendamento.value === 'infusao') return !!prescricaoSelecionadaId.value
  if (tipoAgendamento.value === 'consulta') return !!tipoConsulta.value
  return !!tipoProcedimento.value
})

watch(tipoAgendamento, () => {
  dataSelecionada.value = ''
  horarioInicio.value = ''
  listaAvisos.value = []

  if (tipoAgendamento.value !== 'consulta') tipoConsulta.value = ''
  if (tipoAgendamento.value !== 'procedimento') tipoProcedimento.value = ''
  if (tipoAgendamento.value !== 'infusao') {
    prescricaoSelecionadaId.value = ''
    diaCiclo.value = null
  }
})

watch([prescricaoSelecionadaId, tipoConsulta, tipoProcedimento], () => {
  if (!requisitosTipoOk.value) {
    dataSelecionada.value = ''
    horarioInicio.value = ''
  }
})

const ultimoAgendamento = computed(() => {
  if (!pacienteSelecionado.value) return null
  const agendamentos = appStore.agendamentos
      .filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
  return agendamentos[0] || null
})

const prescricoesFormatadas = computed((): PrescricaoComLabel[] => {
  return prescricoesDisponiveis.value.map(p => ({
    ...p,
    labelFormatado: `${p.conteudo.protocolo.nome} (Ciclo ${p.conteudo.protocolo.cicloAtual}) - ${new Date(p.dataEmissao).toLocaleDateString('pt-BR')}`
  }))
})

const handleSelecionarPaciente = (p: Paciente) => {
  pacienteSelecionado.value = p
  buscaPaciente.value = p.nome
  mostrarResultados.value = false

  dataSelecionada.value = ''
  horarioInicio.value = ''
  prescricaoSelecionadaId.value = ''
  tipoAgendamento.value = 'infusao'
  tipoConsulta.value = ''
  tipoProcedimento.value = ''
  listaAvisos.value = []
}

const handleSelecionarData = (data: string) => {
  dataSelecionada.value = data
  horarioInicio.value = ''
  listaAvisos.value = []
}

const getVagasInfo = (data: string) => {
  const agendamentosNoDia = appStore.getAgendamentosDoDia(data)
  const limiteVagas = appStore.parametros.vagas

  const isConsideradoNaCapacidade = (ag: any) => {
    return ag.status !== 'remarcado' && ag.status !== 'suspenso'
  }

  if (tipoAgendamento.value !== 'infusao') {
    const tipo = tipoAgendamento.value
    const limite = tipo === 'consulta' ? limiteVagas.consultas : limiteVagas.procedimentos
    const countNoTipo = agendamentosNoDia.reduce((acc, ag) => {
      if (!isConsideradoNaCapacidade(ag)) return acc
      return ag.tipo === tipo ? acc + 1 : acc
    }, 0)
    const vagasRestantes = limite - countNoTipo
    return {count: vagasRestantes, full: vagasRestantes <= 0}
  }

  const grupo = grupoInfusaoAtual.value
  const chaveGrupo = `infusao_${grupo}` as keyof typeof limiteVagas
  const limiteGrupo = limiteVagas[chaveGrupo] || 0

  const countNoGrupo = agendamentosNoDia.reduce((acc, ag) => {
    if (!isConsideradoNaCapacidade(ag)) return acc
    if (ag.tipo !== 'infusao') return acc

    const p = appStore.getPacienteById(ag.pacienteId)
    const prot = appStore.getProtocoloById((p as any)?.protocoloId || '')
    const g = (prot as any)?.grupoInfusao || 'medio'
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

  if (tipoAgendamento.value === 'infusao') {
    if (!prescricaoSelecionadaId.value) {
      toast.error('Selecione uma prescrição')
      return
    }
    if (!diaCiclo.value) {
      toast.error('Selecione o dia do ciclo')
      return
    }
  } else if (tipoAgendamento.value === 'consulta') {
    if (!tipoConsulta.value) {
      toast.error('Selecione o tipo de consulta')
      return
    }
  } else if (tipoAgendamento.value === 'procedimento') {
    if (!tipoProcedimento.value) {
      toast.error('Selecione o tipo de procedimento')
      return
    }
  }

  const agendamentosDia = appStore.getAgendamentosDoDia(dataSelecionada.value)
  if (agendamentosDia.some(a => a.pacienteId === pacienteSelecionado.value?.id)) {
    listaAvisos.value.push(`O paciente já possui um agendamento para esta data (${new Date(dataSelecionada.value).toLocaleDateString('pt-BR')}).`)
  }

  if (tipoAgendamento.value === 'infusao') {
    const vagasInfo = getVagasInfo(dataSelecionada.value)
    if (vagasInfo.full) {
      listaAvisos.value.push(`A capacidade para o grupo "${grupoInfusaoAtual.value}" está esgotada neste dia.`)
    }
  } else {
    const vagasInfo = getVagasInfo(dataSelecionada.value)
    if (vagasInfo.full) {
      listaAvisos.value.push(`A capacidade para "${tipoAgendamento.value}" está esgotada neste dia.`)
    }
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
    listaAvisos.value.push(`O horário (${horarioInicio.value}) é anterior à abertura (${abertura}).`)
  }
  if (inicioMin > fechamentoMin) {
    listaAvisos.value.push(`O horário (${horarioInicio.value}) é após o fechamento (${fechamento}).`)
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

  let detalhes = {}

  if (tipoAgendamento.value === 'infusao' && prescricaoAtual.value) {
    detalhes = {
      infusao: {
        prescricao_id: prescricaoAtual.value.id,
        protocolo: prescricaoAtual.value.conteudo.protocolo.nome,
        status_farmacia: 'pendente',
        ciclo_atual: prescricaoAtual.value.conteudo.protocolo.cicloAtual,
        dia_ciclo: diaCiclo.value
      }
    }
  } else if (tipoAgendamento.value === 'consulta') {
    detalhes = {
      consulta: {
        tipo_consulta: tipoConsulta.value
      }
    }
  } else {
    detalhes = {
      procedimento: {
        tipo_procedimento: tipoProcedimento.value
      }
    }
  }

  try {
    await appStore.adicionarAgendamento({
      pacienteId: pacienteSelecionado.value!.id,
      tipo: tipoAgendamento.value,
      data: dataSelecionada.value,
      turno: turnoInferido,
      horarioInicio: horarioInicio.value,
      horarioFim: '00:00', // TODO: Calcular baseado na duração estimada ou tipo de agendamento
      status: 'agendado',
      encaixe: encaixe.value,
      observacoes: observacoes.value,
      detalhes: detalhes,
      prescricao: tipoAgendamento.value === 'infusao' ? prescricaoAtual.value : undefined
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
          :tipo-agendamento="tipoAgendamento"
            :grupo-infusao="grupoInfusaoAtual"
            @selecionar-data="handleSelecionarData"
        />
      </div>

      <div class="space-y-6">
        <AgendamentoResumo
            v-if="pacienteSelecionado"
            :paciente="pacienteSelecionado"
            :ultimo-agendamento="ultimoAgendamento"
        />

        <AgendamentoForm
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
