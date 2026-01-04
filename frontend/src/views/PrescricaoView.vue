<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Button} from '@/components/ui/button'
import {ArrowLeft} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import api from '@/services/api'
import type {Medicamento} from '@/types'
import PrescricaoIdentificacao from '@/components/prescricao/PrescricaoIdentificacao.vue'
import PrescricaoProtocolo from '@/components/prescricao/PrescricaoProtocolo.vue'
import PrescricaoPreQt from '@/components/prescricao/PrescricaoPreQt.vue'
import PrescricaoQt from '@/components/prescricao/PrescricaoQt.vue'
import PrescricaoPosQt from '@/components/prescricao/PrescricaoPosQt.vue'
import PrescricaoFooter from '@/components/prescricao/PrescricaoFooter.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const pacienteSelecionado = ref('')
const peso = ref('')
const altura = ref('')
const diagnostico = ref('')
const protocolo = ref('')
const numeroCiclo = ref('1')

const preQt = ref<Medicamento[]>([])
const qt = ref<Medicamento[]>([])
const posQt = ref<Medicamento[]>([])

const prescricaoConcluida = ref(false)
const prescricaoAtualId = ref('')

// Dados do Médico (Mock)
const medicoInfo = {
  nome: 'Dr. João Silva',
  crm: '123.456 - SP'
}

const calcularSC = computed(() => {
  if (peso.value && altura.value) {
    const p = parseFloat(peso.value)
    const a = parseFloat(altura.value)
    return (0.007184 * Math.pow(a, 0.725) * Math.pow(p, 0.425)).toFixed(2)
  }
  return ''
})

const ultimaPrescricao = computed(() => {
  if (!pacienteSelecionado.value) return null
  const lista = appStore.getPrescricoesPorPaciente(pacienteSelecionado.value)
  if (!lista || lista.length === 0) return null

  const ordenada = [...lista].sort((a, b) =>
      new Date(b.dataPrescricao).getTime() - new Date(a.dataPrescricao).getTime()
  )[0]

  if (!ordenada.protocolo && ordenada.protocoloId) {
    const protoOriginal = appStore.protocolos.find(p => p.id === ordenada.protocoloId)
    if (protoOriginal) {
      ordenada.protocolo = protoOriginal.nome
    }
  }
  return ordenada
})

watch(ultimaPrescricao, (ultimo) => {
  if (ultimo) {
    const protocoloExiste = appStore.protocolos.some(p => p.nome === ultimo.protocolo)
    if (protocoloExiste) {
      protocolo.value = ultimo.protocolo || ''
    }
    numeroCiclo.value = String((ultimo.cicloAtual || 0) + 1)
    toast.info(`Protocolo sugerido com base no histórico: Ciclo ${numeroCiclo.value}`)
  } else {
    protocolo.value = ''
    numeroCiclo.value = '1'
  }
})

watch(pacienteSelecionado, async (novoId) => {
  if (novoId) {
    const p = appStore.getPacienteById(novoId)
    if (p) {
      peso.value = p.peso?.toString() || ''
      altura.value = p.altura?.toString() || ''
    }
    await appStore.fetchPrescricoes(novoId)
  } else {
    peso.value = ''
    altura.value = ''
  }
})

onMounted(async () => {
  if (route.query.pacienteId) {
    const pid = route.query.pacienteId as string
    pacienteSelecionado.value = pid

    const p = appStore.getPacienteById(pid)
    if (p) {
      peso.value = p.peso?.toString() || ''
      altura.value = p.altura?.toString() || ''
    }

    await appStore.fetchPrescricoes(pid)
  }
})

const criarMedicamentoVazio = (): Medicamento => ({
  id: `med-${Date.now()}-${Math.random()}`,
  nome: '',
  dose: '',
  unidade: 'mg',
  via: 'IV',
  tempoInfusao: 0,
  veiculo: '',
  volumeVeiculo: '',
  observacoes: ''
})

const adicionarPreQt = () => preQt.value.push(criarMedicamentoVazio())
const adicionarQt = () => qt.value.push(criarMedicamentoVazio())
const adicionarPosQt = () => posQt.value.push(criarMedicamentoVazio())

const removerMedicamento = (lista: Medicamento[], index: number) => {
  lista.splice(index, 1)
}

const repetirUltimaPrescricao = () => {
  if (!ultimaPrescricao.value) {
    toast.error('Não há prescrição anterior para copiar.')
    return
  }

  const ultima = ultimaPrescricao.value
  preQt.value = []
  qt.value = []
  posQt.value = []

  let itensCopiados = 0

  const mapearItem = (item: any, prefixo: string): Medicamento => ({
    id: `${prefixo}-${Date.now()}-${Math.random()}`,
    nome: item.nome || '',
    dose: item.dose || '',
    unidade: item.unidade || 'mg',
    via: item.via || 'IV',
    tempoInfusao: item.tempoInfusao || 0,
    veiculo: item.veiculo || '',
    volumeVeiculo: item.volumeVeiculo || '',
    observacoes: item.observacoes || ''
  })

  if (ultima.qt && ultima.qt.length > 0) {
    qt.value = ultima.qt.map(m => mapearItem(m, 'qt'))
    itensCopiados += qt.value.length
  }

  if (ultima.medicamentos && ultima.medicamentos.length > 0) {
    preQt.value = ultima.medicamentos.map(m => mapearItem(m, 'pre'))
    itensCopiados += preQt.value.length
  }

  if (ultima.posMedicacoes && ultima.posMedicacoes.length > 0) {
    posQt.value = ultima.posMedicacoes.map(m => mapearItem(m, 'pos'))
    itensCopiados += posQt.value.length
  }

  if (itensCopiados === 0) {
    toast.warning('A prescrição anterior está vazia (não possui itens para copiar).')
  } else {
    toast.success(`${itensCopiados} medicamentos copiados com sucesso.`)
  }
}

const carregarPadraoProtocolo = () => {
  if (!protocolo.value) {
    toast.error('Selecione um protocolo primeiro.')
    return
  }
  const protoData = appStore.protocolos.find(p => p.nome === protocolo.value)
  if (!protoData || !protoData.medicamentos) return

  qt.value = []
  protoData.medicamentos.forEach(item => {
    qt.value.push({
      id: `qt-${Date.now()}-${Math.random()}`,
      nome: item.nome,
      dose: item.dosePadrao || '',
      unidade: item.unidadePadrao || 'mg',
      via: item.viaPadrao || 'IV',
      tempoInfusao: 0,
      veiculo: '',
      volumeVeiculo: '',
      observacoes: ''
    })
  })
  toast.success(`Medicamentos do protocolo ${protocolo.value} carregados.`)
}

const carregarListaPadrao = (tipo: 'pre' | 'pos') => {
  if (!protocolo.value) {
    toast.error('Selecione um protocolo primeiro.')
    return
  }
  const protoData = appStore.protocolos.find(p => p.nome === protocolo.value)
  if (!protoData) return

  const listaOrigem = tipo === 'pre' ? protoData.preMedicacoes : protoData.posMedicacoes
  const listaDestino = tipo === 'pre' ? preQt : posQt

  if (!listaOrigem || listaOrigem.length === 0) {
    toast.info(`Não há padrão de ${tipo === 'pre' ? 'Pré-QT' : 'Pós-QT'} cadastrado.`)
    return
  }

  listaDestino.value = []
  listaOrigem.forEach(item => {
    listaDestino.value.push({
      id: `${tipo}-${Date.now()}-${Math.random()}`,
      nome: item.nome,
      dose: item.dosePadrao || '',
      unidade: item.unidadePadrao || 'mg',
      via: item.viaPadrao || (tipo === 'pos' ? 'SC' : 'IV'),
      tempoInfusao: 0,
      veiculo: '',
      volumeVeiculo: '',
      observacoes: ''
    })
  })
  toast.success(`Medicamentos de ${tipo === 'pre' ? 'Pré-QT' : 'Pós-QT'} carregados.`)
}

const confirmarPrescricao = async () => {
  if (!pacienteSelecionado.value) {
    toast.error('Por favor, selecione um paciente.')
    return
  }
  if (!protocolo.value) {
    toast.error('Por favor, selecione um protocolo.')
    return
  }
  if (qt.value.length === 0) {
    toast.error('Erro: Nenhum medicamento de quimioterapia foi adicionado.')
    return
  }
  if (!peso.value || !altura.value) {
    toast.error('Erro: Peso ou Altura não preenchidos.')
    return
  }

  try {
    const protocoloObj = appStore.protocolos.find(p => p.nome === protocolo.value)

    const dadosEnvio = {
      pacienteId: pacienteSelecionado.value,
      medicoNome: medicoInfo.nome,
      protocoloId: protocoloObj?.id,
      protocoloNomeSnapshot: protocolo.value,
      cicloAtual: parseInt(numeroCiclo.value) || 1,
      ciclosTotal: protocoloObj?.numeroCiclos || 0,
      peso: parseFloat(peso.value) || 0,
      altura: parseFloat(altura.value) || 0,
      superficieCorporea: parseFloat(calcularSC.value) || 0,
      diagnostico: diagnostico.value,
      status: 'ativa',
      medicamentos: preQt.value.map((item, index) => ({
        ...item, ordem: index + 1, tipo: 'pre'
      })),
      qt: qt.value.map((item, index) => ({
        ...item, ordem: index + 1, tipo: 'qt'
      })),
      posMedicacoes: posQt.value.map((item, index) => ({
        ...item, ordem: index + 1, tipo: 'pos'
      }))
    }

    const novaPrescricao = await appStore.adicionarPrescricao(dadosEnvio)
    prescricaoAtualId.value = novaPrescricao.id
    prescricaoConcluida.value = true
    toast.success('Prescrição confirmada e salva com sucesso!')
  } catch (e) {
    console.error("Erro ao salvar prescrição:", e)
    // toast.error('Ocorreu um erro ao salvar a prescrição.')
  }
}

const handleImprimir = () => window.print()

const handleBaixar = async () => {
  if (!prescricaoConcluida.value && !ultimaPrescricao.value) {
    toast.error("É necessário confirmar a prescrição antes de baixar.")
    return
  }
  const idParaBaixar = prescricaoAtualId.value || (ultimaPrescricao.value ? ultimaPrescricao.value.id : null)

  if (!idParaBaixar) {
    toast.error("ID da prescrição não encontrado.")
    return
  }

  toast.info('Gerando PDF...')
  try {
    const response = await api.get(`/api/prescricoes/${idParaBaixar}/pdf`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `prescricao_${idParaBaixar}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    toast.success("Download iniciado!")
  } catch (e) {
    toast.error("Erro ao gerar PDF.")
    console.error(e)
  }
}
</script>

<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    <div class="flex items-center gap-4">
      <Button size="icon" variant="outline" @click="router.back()">
        <ArrowLeft class="h-4 w-4"/>
      </Button>
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Nova Prescrição</h1>
      </div>
    </div>

    <PrescricaoIdentificacao
        v-model:altura="altura"
        v-model:diagnostico="diagnostico"
        v-model:pacienteId="pacienteSelecionado"
        v-model:peso="peso"
    />

    <PrescricaoProtocolo
        v-model:numeroCiclo="numeroCiclo"
        v-model:protocolo="protocolo"
        :ultima-prescricao="ultimaPrescricao"
        @repetir="repetirUltimaPrescricao"
    />

    <PrescricaoPreQt
        :medicamentos="preQt"
        :protocolo-selecionado="protocolo"
        @adicionar="adicionarPreQt"
        @remover="(idx) => removerMedicamento(preQt, idx)"
        @carregar-padrao="carregarListaPadrao('pre')"
    />

    <PrescricaoQt
        :medicamentos="qt"
        :protocolo-selecionado="protocolo"
        @adicionar="adicionarQt"
        @remover="(idx) => removerMedicamento(qt, idx)"
        @carregar-padrao="carregarPadraoProtocolo"
    />

    <PrescricaoPosQt
        :medicamentos="posQt"
        :protocolo-selecionado="protocolo"
        @adicionar="adicionarPosQt"
        @remover="(idx) => removerMedicamento(posQt, idx)"
        @carregar-padrao="carregarListaPadrao('pos')"
    />

    <PrescricaoFooter
        :concluida="prescricaoConcluida"
        @baixar="handleBaixar"
        @confirmar="confirmarPrescricao"
        @imprimir="handleImprimir"
    />
  </div>
</template>
