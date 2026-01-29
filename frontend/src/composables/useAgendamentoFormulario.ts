import {computed, ref, watch} from 'vue'
import {useAppStore} from '@/stores/storeGeral.ts'
import {useRouter} from 'vue-router'
import {toast} from 'vue-sonner'
import {
  GrupoInfusao,
  TipoAgendamento,
  TipoConsultaEnum,
  TipoProcedimentoEnum,
  Turno
} from "@/types/typesAgendamento.ts";
import {Paciente} from "@/types/typesPaciente.ts";
import {PrescricaoComLabel} from '@/components/agendamento/AgendamentoFormulario.vue'
import {
  DURACAO_CONSULTA_PADRAO,
  DURACAO_PROCEDIMENTO_PADRAO,
  DURACOES_CONSULTA,
  DURACOES_PROCEDIMENTO
} from "@/constants/constAgenda.ts";
import {somarMinutosAoHorario} from "@/utils/utilsAgenda.ts";

export function useAgendamentoFormulario() {
  const appStore = useAppStore()
  const router = useRouter()

  const buscaPaciente = ref('')
  const pacienteSelecionado = ref<Paciente | null>(null)
  const mostrarResultadosBusca = ref(false)
  const dataSelecionada = ref('')
  const horarioInicio = ref('')
  const encaixe = ref(false)
  const observacoes = ref('')

  const tipoAgendamento = ref<TipoAgendamento>('infusao')
  const tipoConsulta = ref<TipoConsultaEnum | ''>('')
  const tipoProcedimento = ref<TipoProcedimentoEnum | ''>('')
  const prescricaoSelecionadaId = ref('')
  const diaCiclo = ref<number | null>(null)

  const confirmacaoOpen = ref(false)
  const listaAvisos = ref<string[]>([])

  const prescricoesDisponiveis = computed(() => {
    if (!pacienteSelecionado.value) return []
    return appStore.prescricoes.filter(p =>
      p.pacienteId === pacienteSelecionado.value?.id &&
      ['pendente', 'em-curso'].includes(p.status)
    )
  })

  const prescricoesFormatadas = computed((): PrescricaoComLabel[] => {
    return prescricoesDisponiveis.value.map(p => ({
      ...p,
      labelFormatado: `${p.conteudo.protocolo.nome} (Ciclo ${p.conteudo.protocolo.cicloAtual}) - ${new Date(p.dataEmissao).toLocaleDateString('pt-BR')}`
    }))
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

  const grupoInfusaoAtual = computed((): GrupoInfusao => {
    if (tipoAgendamento.value !== 'infusao' || !prescricaoAtual.value) return 'medio'
    const protoNome = prescricaoAtual.value.conteudo.protocolo.nome
    const protocoloFull = appStore.protocolos.find(p => p.nome === protoNome)

    if (protocoloFull && protocoloFull.tempoTotalMinutos) {
      if (protocoloFull.tempoTotalMinutos < 30) return 'rapido'
      if (protocoloFull.tempoTotalMinutos <= 120) return 'medio'
      if (protocoloFull.tempoTotalMinutos <= 240) return 'longo'
      return 'extra_longo'
    }
    return 'medio'
  })

  const requisitosTipoOk = computed(() => {
    if (tipoAgendamento.value === 'infusao') return !!prescricaoSelecionadaId.value
    if (tipoAgendamento.value === 'consulta') return !!tipoConsulta.value
    return !!tipoProcedimento.value
  })

  const duracaoEstimadaMinutos = computed(() => {
    if (tipoAgendamento.value === 'infusao') {
      if (!prescricaoAtual.value) return 0
      const protoNome = prescricaoAtual.value.conteudo.protocolo.nome
      const protocoloFull = appStore.protocolos.find(p => p.nome === protoNome)
      return protocoloFull?.tempoTotalMinutos || 120 // 120 default
    }

    if (tipoAgendamento.value === 'consulta') {
      if (!tipoConsulta.value) return DURACAO_CONSULTA_PADRAO
      return DURACOES_CONSULTA[tipoConsulta.value] || DURACAO_CONSULTA_PADRAO
    }

    if (tipoAgendamento.value === 'procedimento') {
      if (!tipoProcedimento.value) return DURACAO_PROCEDIMENTO_PADRAO
      return DURACOES_PROCEDIMENTO[tipoProcedimento.value] || DURACAO_PROCEDIMENTO_PADRAO
    }
    return 0
  })

  const horarioFimCalculado = computed(() => {
    if (!horarioInicio.value) return ''
    return somarMinutosAoHorario(horarioInicio.value, duracaoEstimadaMinutos.value)
  })

  const ultimoAgendamento = computed(() => {
    if (!pacienteSelecionado.value) return null
    const agendamentos = appStore.agendamentos
      .filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
    return agendamentos[0] || null
  })

  let timeoutBusca: ReturnType<typeof setTimeout>
  watch(buscaPaciente, (novoTermo) => {
    clearTimeout(timeoutBusca)
    timeoutBusca = setTimeout(async () => {
      if (novoTermo.length >= 3) {
        await appStore.buscarPacientesDropdown(novoTermo)
        mostrarResultadosBusca.value = true
      }
    }, 300)
  })

  watch(prescricaoSelecionadaId, () => {
    if (diasPermitidosCiclo.value.length > 0) {
      diaCiclo.value = diasPermitidosCiclo.value[0]
    } else {
      diaCiclo.value = null
    }
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

  watch(pacienteSelecionado, async (novoPaciente) => {
    if (novoPaciente) {
      await Promise.all([
        appStore.fetchPrescricoes(novoPaciente.id),
        appStore.fetchAgendamentos(undefined, undefined, novoPaciente.id)
      ])
    }
  })

  const handleSelecionarPaciente = (p: Paciente) => {
    pacienteSelecionado.value = p
    buscaPaciente.value = p.nome
    mostrarResultadosBusca.value = false
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

  const preValidarAgendamento = (vagasInfo: { full: boolean, label: string }) => {
    listaAvisos.value = []

    if (!pacienteSelecionado.value || !dataSelecionada.value || !horarioInicio.value) {
      toast.error('Preencha todos os campos obrigatórios')
      return
    }

    if (tipoAgendamento.value === 'infusao' && (!prescricaoSelecionadaId.value || !diaCiclo.value)) {
      toast.error('Selecione a prescrição e o dia do ciclo') // Msg ajustada
      return
    }
    if (tipoAgendamento.value === 'consulta' && !tipoConsulta.value) {
      toast.error('Selecione o tipo de consulta')
      return
    }
    if (tipoAgendamento.value === 'procedimento' && !tipoProcedimento.value) {
      toast.error('Selecione o tipo de procedimento')
      return
    }

    if (vagasInfo.full) {
      listaAvisos.value.push(`A capacidade para "${vagasInfo.label}" está esgotada neste dia.`)
    }

    const agendamentosDia = appStore.getAgendamentosDoDia(dataSelecionada.value)
    if (agendamentosDia.some(a => a.pacienteId === pacienteSelecionado.value?.id)) {
      listaAvisos.value.push(`O paciente já possui um agendamento nesta data.`)
    }

    const abertura = appStore.parametros.horarioAbertura
    const fechamento = appStore.parametros.horarioFechamento
    const [hIni, mIni] = horarioInicio.value.split(':').map(Number)
    const inicioMin = hIni * 60 + mIni
    const [hAbe, mAbe] = abertura.split(':').map(Number)
    const aberturaMin = hAbe * 60 + mAbe
    const [hFec, mFec] = fechamento.split(':').map(Number)
    const fechamentoMin = hFec * 60 + mFec
    const [hEnd, mEnd] = horarioFimCalculado.value.split(':').map(Number)
    const fimMin = hEnd * 60 + mEnd

    if (inicioMin < aberturaMin) {
      listaAvisos.value.push(`O horário (${horarioInicio.value}) é anterior à abertura (${abertura}).`)
    }
    if (inicioMin > fechamentoMin) {
      listaAvisos.value.push(`O horário de início é após o fechamento.`)
    }
    if (fimMin > fechamentoMin) {
      listaAvisos.value.push(`O término previsto (${horarioFimCalculado.value}) excede o horário de fechamento (${fechamento}).`)
    }

    if (listaAvisos.value.length > 0) {
      confirmacaoOpen.value = true
    } else {
      void realizarAgendamento()
    }
  }

  const realizarAgendamento = async () => {
    confirmacaoOpen.value = false
    const [hIni] = horarioInicio.value.split(':').map(Number)
    const turnoInferido: Turno = hIni < 13 ? 'manha' : 'tarde'

    let detalhes: {}

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
      detalhes = {consulta: {tipo_consulta: tipoConsulta.value}}
    } else {
      detalhes = {procedimento: {tipo_procedimento: tipoProcedimento.value}}
    }

    try {
      await appStore.adicionarAgendamento({
        pacienteId: pacienteSelecionado.value!.id,
        tipo: tipoAgendamento.value,
        data: dataSelecionada.value,
        turno: turnoInferido,
        horarioInicio: horarioInicio.value,
        horarioFim: horarioFimCalculado.value || appStore.parametros.horarioFechamento, // Usa o calculado
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

  return {
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
    ultimoAgendamento,
    duracaoEstimadaMinutos,
    horarioFimCalculado,
    handleSelecionarPaciente,
    handleSelecionarData,
    preValidarAgendamento,
    realizarAgendamento,
  }
}
