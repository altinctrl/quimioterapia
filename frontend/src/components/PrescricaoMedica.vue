<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Textarea} from '@/components/ui/textarea'
import {Alert, AlertDescription} from '@/components/ui/alert'
import {Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList,} from '@/components/ui/command'
import {Popover, PopoverContent, PopoverTrigger,} from '@/components/ui/popover'
import {
  Activity,
  ArrowLeft,
  Check,
  CheckCircle2,
  ChevronsUpDown,
  Clock,
  Copy,
  Download,
  Info,
  ListPlus,
  Pill,
  Plus,
  Printer,
  Trash2,
  User
} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import api from '@/services/api'
import type {Medicamento} from '@/types'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const pacienteSelecionado = ref('')
const peso = ref('')
const altura = ref('')
const diagnostico = ref('')
const protocolo = ref('')
const numeroCiclo = ref('1')
const openCombobox = ref(false)

const preQt = ref<Medicamento[]>([])
const qt = ref<Medicamento[]>([])
const posQt = ref<Medicamento[]>([])

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

const tempoTotalInfusao = computed(() => {
  return qt.value.reduce((acc, med) => acc + (med.tempoInfusao || 0), 0)
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

const removerMedicamento = (lista: Medicamento[], index: number) => {
  lista.splice(index, 1)
}

const prescricaoConcluida = ref(false)

const prescricaoAtualId = ref('')

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
        nome: item.nome,
        dose: item.dose,
        unidade: item.unidade,
        via: item.via,
        tempoInfusao: item.tempoInfusao,
        veiculo: item.veiculo,
        volumeVeiculo: item.volumeVeiculo,
        observacoes: item.observacoes,
        ordem: index + 1,
        tipo: 'pre'
      })),

      qt: qt.value.map((item, index) => ({
        nome: item.nome,
        dose: item.dose,
        unidade: item.unidade,
        via: item.via,
        tempoInfusao: item.tempoInfusao,
        veiculo: item.veiculo,
        volumeVeiculo: item.volumeVeiculo,
        observacoes: item.observacoes,
        ordem: index + 1,
        tipo: 'qt'
      })),

      posMedicacoes: posQt.value.map((item, index) => ({
        nome: item.nome,
        dose: item.dose,
        unidade: item.unidade,
        via: item.via,
        tempoInfusao: item.tempoInfusao,
        veiculo: item.veiculo,
        volumeVeiculo: item.volumeVeiculo,
        observacoes: item.observacoes,
        ordem: index + 1,
        tipo: 'pos'
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

const handleImprimir = () => {
  window.print()
}

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
      responseType: 'blob' // Importante para arquivos binários
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

    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <User class="h-5 w-5"/>
          1. Identificação
        </CardTitle>
      </CardHeader>
      <CardContent class="grid grid-cols-2 gap-4">
        <div class="col-span-2">
          <Label>Paciente *</Label>
          <Select v-model="pacienteSelecionado" :disabled="!!route.query.pacienteId">
            <SelectTrigger>
              <SelectValue placeholder="Selecione..."/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="p in appStore.pacientes" :key="p.id" :value="p.id">
                {{ p.nome }} - {{ p.registro }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div class="col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <Label class="whitespace-nowrap">Peso (kg)</Label>
            <Input v-model="peso" class="min-w-[100px] mt-1.5" placeholder="00.0" type="number"/>
          </div>
          <div>
            <Label class="whitespace-nowrap">Altura (cm)</Label>
            <Input v-model="altura" class="min-w-[100px] mt-1.5" placeholder="000" type="number"/>
          </div>
          <div>
            <Label class="whitespace-nowrap">SC (m²)</Label>
            <Input :value="calcularSC" class="bg-gray-100 font-medium text-gray-700 min-w-[100px] mt-1.5" disabled/>
          </div>
        </div>

        <div class="col-span-2"><Label>Diagnóstico</Label><Textarea v-model="diagnostico" rows="2"/></div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Activity class="h-5 w-5"/>
          2. Ciclo
        </CardTitle>
      </CardHeader>
      <CardContent class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div v-if="ultimaPrescricao"
             class="col-span-1 sm:col-span-4 bg-blue-50 border border-blue-200 rounded-md p-3 flex items-start gap-3 mb-2">
          <Info class="h-5 w-5 text-blue-600 mt-0.5 shrink-0"/>
          <div class="text-sm">
            <p class="font-medium text-blue-900">Último Tratamento Registrado</p>
            <div class="flex flex-wrap gap-x-4 mt-1 text-blue-800">
              <span>Protocolo: <strong>{{ ultimaPrescricao.protocolo }}</strong></span>
              <span>Ciclo Realizado: <strong>{{ ultimaPrescricao.cicloAtual }}</strong></span>
              <span class="text-blue-600 text-xs self-center">({{
                  new Date(ultimaPrescricao.dataPrescricao).toLocaleDateString('pt-BR')
                }})</span>
            </div>
          </div>
        </div>

        <div class="col-span-1 sm:col-span-3 flex flex-col gap-2">
          <Label>Protocolo *</Label>
          <Popover v-model:open="openCombobox">
            <PopoverTrigger as-child>
              <Button :aria-expanded="openCombobox" class="w-full justify-between h-14 px-3 text-left font-normal" role="combobox" type="button"
                      variant="outline">
                <div v-if="protocolo" class="flex flex-col items-start text-left overflow-hidden w-full">
                  <span class="font-semibold leading-tight truncate w-full">{{ protocolo }}</span>
                  <span class="text-xs text-muted-foreground leading-tight truncate w-full">
                    {{ appStore.protocolos.find(p => p.nome === protocolo)?.indicacao }}
                  </span>
                </div>
                <span v-else class="text-muted-foreground">Selecione o protocolo...</span>
                <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50"/>
              </Button>
            </PopoverTrigger>
            <PopoverContent align="start" class="w-[--reka-popover-trigger-width] p-0">
              <Command class="h-auto w-full">
                <CommandInput placeholder="Buscar..."/>
                <CommandEmpty>Nenhum protocolo encontrado.</CommandEmpty>
                <CommandList>
                  <CommandGroup>
                    <CommandItem
                        v-for="p in appStore.protocolos"
                        :key="p.id"
                        :value="p.nome + ' ' + p.indicacao"
                        class="cursor-pointer border-b last:border-0"
                        @select="() => { protocolo = p.nome; openCombobox = false }"
                    >
                      <Check :class="['mr-2 h-4 w-4', protocolo === p.nome ? 'opacity-100' : 'opacity-0']"/>
                      <div class="flex flex-col">
                        <span class="font-medium">{{ p.nome }}</span>
                        <span class="text-xs text-muted-foreground">{{ p.indicacao }} • {{ p.duracao }} min</span>
                      </div>
                    </CommandItem>
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </div>

        <div class="col-span-1 sm:col-span-1 flex flex-col gap-2">
          <Label>Ciclo Nº</Label>
          <Input v-model="numeroCiclo" class="h-14" type="number"/>
        </div>
      </CardContent>
    </Card>

    <div class="flex justify-center py-2">
      <div class="relative inline-block">
        <Button
            :disabled="!ultimaPrescricao || protocolo !== ultimaPrescricao.protocolo"
            class="text-blue-700 border-blue-200 hover:bg-blue-50 bg-white shadow-sm"
            variant="outline"
            @click="repetirUltimaPrescricao"
        >
          <Copy class="h-4 w-4 mr-2"/>
          Repetir Última Prescrição
        </Button>

        <span
            v-if="ultimaPrescricao && protocolo !== ultimaPrescricao.protocolo"
            class="absolute left-1/2 -translate-x-1/2 -top-8 w-max px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 hover:opacity-100 transition-opacity cursor-help"
        >
          Disponível apenas para o mesmo protocolo
        </span>
      </div>
    </div>

    <Card>
      <CardHeader>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <CardTitle class="flex items-center gap-2">
              <Pill class="h-5 w-5 text-gray-600"/>
              3. Pré-Quimioterapia (PRE-QT)
            </CardTitle>
            <CardDescription>Medicações administradas antes (antieméticos, corticoides)</CardDescription>
          </div>
          <Button
              v-if="preQt.length === 0 && protocolo"
              class="bg-white border-blue-200 text-blue-700 hover:bg-blue-50 w-full sm:w-auto" size="sm"
              variant="outline"
              @click="carregarListaPadrao('pre')"
          >
            <ListPlus class="h-4 w-4 mr-2"/>
            Carregar Padrão
          </Button>
        </div>
      </CardHeader>
      <CardContent class="space-y-4">
        <div v-for="(med, idx) in preQt" :key="med.id" class="border rounded-lg p-4 bg-gray-50 relative">
          <Button class="absolute top-2 right-2 text-red-500 hover:bg-red-50" size="sm" variant="ghost"
                  @click="removerMedicamento(preQt, idx)">
            <Trash2 class="h-4 w-4"/>
          </Button>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="col-span-2"><Label>Medicamento</Label><Input v-model="med.nome"/></div>
            <div><Label>Dose</Label><Input v-model="med.dose"/></div>
            <div>
              <Label>Unidade</Label>
              <Select v-model="med.unidade">
                <SelectTrigger>
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mg">mg</SelectItem>
                  <SelectItem value="g">g</SelectItem>
                  <SelectItem value="mcg">mcg</SelectItem>
                  <SelectItem value="UI">UI</SelectItem>
                  <SelectItem value="ml">ml</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Via</Label>
              <Select v-model="med.via">
                <SelectTrigger>
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="IV">IV</SelectItem>
                  <SelectItem value="VO">VO</SelectItem>
                  <SelectItem value="SC">SC</SelectItem>
                  <SelectItem value="IM">IM</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div><Label>Tempo (min)</Label><Input v-model="med.tempoInfusao" type="number"/></div>
            <div><Label>Veículo</Label><Input v-model="med.veiculo" placeholder="Ex: SF 100ml"/></div>
            <div><Label>Volume (ml)</Label><Input v-model="med.volumeVeiculo"/></div>

            <div class="col-span-2 md:col-span-4"><Label>Observações</Label><Input v-model="med.observacoes"/></div>
          </div>
        </div>
        <Button class="w-full" variant="outline" @click="adicionarPreQt">
          <Plus class="h-4 w-4 mr-2"/>
          Adicionar PRE-QT
        </Button>
      </CardContent>
    </Card>

    <Card class="border-blue-200 bg-blue-50/30">
      <CardHeader>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <CardTitle class="flex items-center gap-2 text-blue-900">
              <Pill class="h-5 w-5"/>
              4. Quimioterapia (QT)
            </CardTitle>
            <CardDescription>Fármacos principais do protocolo</CardDescription>
          </div>

          <Button
              v-if="qt.length === 0 && protocolo"
              class="bg-white border-blue-200 text-blue-700 hover:bg-blue-50 w-full sm:w-auto"
              size="sm"
              variant="outline"
              @click="carregarPadraoProtocolo"
          >
            <ListPlus class="h-4 w-4 mr-2"/>
            Carregar Padrão
          </Button>
        </div>
      </CardHeader>
      <CardContent class="space-y-4">
        <div v-for="(med, idx) in qt" :key="med.id"
             class="border border-blue-100 rounded-lg p-4 bg-white relative shadow-sm">
          <Button class="absolute top-2 right-2 text-red-500 hover:text-red-700 hover:bg-red-50" size="sm"
                  variant="ghost"
                  @click="removerMedicamento(qt, idx)">
            <Trash2 class="h-4 w-4"/>
          </Button>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="col-span-2"><Label>Medicamento *</Label><Input v-model="med.nome" placeholder="Ex: Paclitaxel"/>
            </div>
            <div><Label>Dose *</Label><Input v-model="med.dose"/></div>
            <div>
              <Label>Unidade</Label>
              <Select v-model="med.unidade">
                <SelectTrigger>
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mg">mg</SelectItem>
                  <SelectItem value="g">g</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Via</Label>
              <Select v-model="med.via">
                <SelectTrigger>
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="IV">IV</SelectItem>
                  <SelectItem value="SC">SC</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div><Label>Tempo (min)</Label><Input v-model="med.tempoInfusao" type="number"/></div>
            <div><Label>Veículo</Label><Input v-model="med.veiculo" placeholder="SF 0.9%"/></div>
            <div><Label>Vol (ml)</Label><Input v-model="med.volumeVeiculo" placeholder="500"/></div>
          </div>
        </div>

        <Button class="w-full border-blue-300 text-blue-700 hover:bg-blue-50" variant="outline" @click="adicionarQt">
          <Plus class="h-4 w-4 mr-2"/>
          Adicionar QT
        </Button>

        <Alert v-if="qt.length > 0 && tempoTotalInfusao > 0" class="bg-blue-100 border-blue-200">
          <Clock class="h-4 w-4 text-blue-700"/>
          <AlertDescription class="text-blue-800">
            <strong>Tempo total estimado de infusão:</strong> {{ tempoTotalInfusao }} minutos
            ({{ (tempoTotalInfusao / 60).toFixed(1) }}h)
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <CardTitle class="flex items-center gap-2">
              <Pill class="h-5 w-5 text-gray-600"/>
              5. Pós-Quimioterapia (POS-QT)
            </CardTitle>
            <CardDescription>Medicações para casa ou pós-infusão</CardDescription>
          </div>
          <Button
              v-if="posQt.length === 0 && protocolo"
              class="bg-white border-blue-200 text-blue-700 hover:bg-blue-50 w-full sm:w-auto" size="sm"
              variant="outline"
              @click="carregarListaPadrao('pos')"
          >
            <ListPlus class="h-4 w-4 mr-2"/>
            Carregar Padrão
          </Button>
        </div>
      </CardHeader>
      <CardContent class="space-y-4">
        <div v-for="(med, idx) in posQt" :key="med.id" class="border rounded-lg p-4 bg-gray-50 relative">
          <Button class="absolute top-2 right-2 text-red-500 hover:bg-red-50" size="sm" variant="ghost"
                  @click="removerMedicamento(posQt, idx)">
            <Trash2 class="h-4 w-4"/>
          </Button>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="col-span-2"><Label>Medicamento</Label><Input v-model="med.nome"/></div>
            <div><Label>Dose</Label><Input v-model="med.dose"/></div>
            <div>
              <Label>Unidade</Label>
              <Select v-model="med.unidade">
                <SelectTrigger>
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mg">mg</SelectItem>
                  <SelectItem value="g">g</SelectItem>
                  <SelectItem value="mcg">mcg</SelectItem>
                  <SelectItem value="UI">UI</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Via</Label>
              <Select v-model="med.via">
                <SelectTrigger>
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="SC">SC</SelectItem>
                  <SelectItem value="VO">VO</SelectItem>
                  <SelectItem value="IV">IV</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div><Label>Tempo (min)</Label><Input v-model="med.tempoInfusao" type="number"/></div>
            <div><Label>Veículo</Label><Input v-model="med.veiculo"/></div>
            <div><Label>Volume (ml)</Label><Input v-model="med.volumeVeiculo"/></div>
          </div>
        </div>
        <Button class="w-full" variant="outline" @click="adicionarPosQt">
          <Plus class="h-4 w-4 mr-2"/>
          Adicionar POS-QT
        </Button>
      </CardContent>
    </Card>

    <div v-if="prescricaoConcluida"
         class="flex flex-col items-center justify-center py-12 space-y-6 animate-in fade-in slide-in-from-bottom-4">
      <div class="bg-green-100 p-4 rounded-full">
        <CheckCircle2 class="h-16 w-16 text-green-600"/>
      </div>
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900">Prescrição Emitida!</h2>
        <p class="text-gray-500">O documento foi salvo no histórico do paciente.</p>
      </div>

      <div class="flex gap-4">
        <Button class="gap-2" variant="outline" @click="handleImprimir">
          <Printer class="h-4 w-4"/>
          Imprimir
        </Button>
        <Button class="gap-2" variant="outline" @click="handleBaixar">
          <Download class="h-4 w-4"/>
          Baixar PDF
        </Button>
        <Button @click="router.back()">
          Voltar para Lista
        </Button>
      </div>
    </div>

    <div v-else class="space-y-6">

      <div class="flex items-center justify-end gap-4 pt-4 border-t border-gray-200">
        <Button variant="ghost" @click="router.back()">Cancelar</Button>
        <Button class="bg-green-600 hover:bg-green-700 text-white min-w-[200px]" size="lg" @click="confirmarPrescricao">
          <CheckCircle2 class="h-5 w-5 mr-2"/>
          Confirmar Prescrição
        </Button>
      </div>
    </div>
  </div>
</template>
