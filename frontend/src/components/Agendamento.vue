<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {AlertTriangle, ArrowLeft, Calendar as CalendarIcon, ChevronDown, Search} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import type {GrupoInfusao, Paciente, Turno} from '@/types'

const router = useRouter()
const appStore = useAppStore()

const buscaPaciente = ref('')
const pacienteSelecionado = ref<Paciente | null>(null)
const mesSelecionado = ref(String(new Date().getMonth() + 1))
const anoSelecionado = ref(String(new Date().getFullYear()))
const dataSelecionada = ref('')
const horarioInicio = ref('')
const diaCiclo = ref('D1')
const observacoes = ref('')
const mostrarResultados = ref(false)

const confirmacaoOpen = ref(false)
const listaAvisos = ref<string[]>([])

const meses = [
  {value: '1', label: 'Janeiro'}, {value: '2', label: 'Fevereiro'}, {value: '3', label: 'Março'},
  {value: '4', label: 'Abril'}, {value: '5', label: 'Maio'}, {value: '6', label: 'Junho'},
  {value: '7', label: 'Julho'}, {value: '8', label: 'Agosto'}, {value: '9', label: 'Setembro'},
  {value: '10', label: 'Outubro'}, {value: '11', label: 'Novembro'}, {value: '12', label: 'Dezembro'}
]

let timeoutBusca: ReturnType<typeof setTimeout>

watch(buscaPaciente, (novoTermo) => {
  clearTimeout(timeoutBusca)

  timeoutBusca = setTimeout(() => {
    appStore.buscarPacientesDropdown(novoTermo)
    mostrarResultados.value = true
  }, 300)
})

const handleInputBusca = async () => {
  await appStore.buscarPacientesDropdown(buscaPaciente.value)
  mostrarResultados.value = true
}

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

const diasDoMes = computed(() => {
  const year = parseInt(anoSelecionado.value)
  const month = parseInt(mesSelecionado.value) - 1
  const date = new Date(year, month, 1)
  const days: Date[] = []
  while (date.getMonth() === month) {
    days.push(new Date(date))
    date.setDate(date.getDate() + 1)
  }
  return days
})

const espacosVazios = computed(() => {
  if (diasDoMes.value.length === 0) return 0
  return diasDoMes.value[0].getDay()
})

const todayStr = new Date().toISOString().split('T')[0]

const isDayDisabled = (date: Date) => {
  const dateStr = date.toISOString().split('T')[0]
  const isPastDate = dateStr < todayStr
  const dayOfWeek = date.getDay()
  const isClosedDay = !appStore.parametros.diasFuncionamento.includes(dayOfWeek)
  return isPastDate || isClosedDay
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

  return {
    count: vagasRestantes,
    full: vagasRestantes <= 0
  }
}

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
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <Search class="h-5 w-5"/>
              Buscar Paciente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="relative">
              <Label>Nome ou CPF</Label>
              <Input v-model="buscaPaciente" class="mt-1" placeholder="Digite para buscar..."
                     @focus="mostrarResultados = true"/>
              <div v-if="mostrarResultados && appStore.resultadosBusca.length > 0"
                   class="absolute z-10 w-full bg-white border rounded shadow-lg mt-1 max-h-48 overflow-auto">
                <div
                    v-for="p in appStore.resultadosBusca"
                    :key="p.id"
                    class="p-2 hover:bg-gray-100 cursor-pointer"
                    @click="handleSelecionarPaciente(p)"
                >
                  <div class="font-medium">{{ p.nome }}</div>
                  <div class="text-xs text-gray-500">{{ p.cpf }}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card v-if="pacienteSelecionado">
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <CalendarIcon class="h-5 w-5"/>
              Selecionar Data
            </CardTitle>
            <div class="flex gap-4 mt-4">
              <div class="w-1/2">
                <Label>Mês</Label>
                <div class="relative">
                  <select
                      v-model="mesSelecionado"
                      class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
                  >
                    <option v-for="mes in meses" :key="mes.value" :value="mes.value">{{ mes.label }}</option>
                  </select>
                  <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
                </div>
              </div>
              <div class="w-1/2">
                <Label>Ano</Label>
                <Input v-model="anoSelecionado" type="number"/>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-7 gap-2">
              <div v-for="d in ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb']" :key="d"
                   class="text-center text-sm text-gray-500">{{ d }}
              </div>

              <div v-for="i in espacosVazios" :key="`empty-${i}`"></div>

              <button
                  v-for="dia in diasDoMes"
                  :key="dia.toISOString()"
                  :class="[
                  'p-2 border rounded flex flex-col items-center justify-center h-20 transition-colors relative',
                  dataSelecionada === dia.toISOString().split('T')[0] ? 'border-blue-600 bg-blue-50' : '',
                  isDayDisabled(dia) ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-60' : 'hover:border-blue-300 cursor-pointer bg-white'
                ]"
                  :disabled="isDayDisabled(dia)"
                  @click="!isDayDisabled(dia) && handleSelecionarData(dia.toISOString().split('T')[0])"
              >
                <span class="font-medium">{{ dia.getDate() }}</span>
                <div v-if="!isDayDisabled(dia)" class="mt-1 text-xs">
                  <span v-if="getVagasInfo(dia.toISOString().split('T')[0]).full"
                        class="text-red-600 font-bold">Cheio</span>
                  <span v-else class="text-green-600 font-medium">{{
                      getVagasInfo(dia.toISOString().split('T')[0]).count
                    }} vagas</span>
                </div>
              </button>
            </div>
            <div class="mt-2 text-xs text-gray-500 text-right">
              Vagas para grupo: <span class="capitalize font-medium">{{ grupoInfusaoAtual }}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="space-y-6">
        <Card v-if="pacienteSelecionado" class="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle>Resumo do Paciente</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <p class="font-medium text-lg">{{ pacienteSelecionado.nome }}</p>
              <p class="text-sm text-gray-600">Reg: {{ pacienteSelecionado.registro }}</p>
            </div>

            <div v-if="protocolo" class="pt-3 border-t border-blue-200">
              <Label class="text-xs text-gray-500">Protocolo</Label>
              <p class="font-medium">{{ protocolo.nome }}</p>
              <p class="text-sm text-gray-600">{{ protocolo.duracao }} min • Grupo {{ protocolo.grupoInfusao }}</p>
            </div>

            <div v-if="ultimoAgendamento" class="pt-3 border-t border-blue-200 bg-white/50 p-3 rounded">
              <Label class="text-xs text-gray-500">Último Agendamento</Label>
              <p class="text-sm font-medium">{{ new Date(ultimoAgendamento.data).toLocaleDateString('pt-BR') }}</p>
              <p class="text-sm text-gray-600">Ciclo {{ ultimoAgendamento.cicloAtual }} - {{
                  ultimoAgendamento.diaCiclo
                }}</p>
            </div>
            <div v-else class="pt-3 border-t border-blue-200">
              <p class="text-sm text-gray-500 italic">Primeiro agendamento</p>
            </div>
          </CardContent>
        </Card>

        <Card v-if="dataSelecionada">
          <CardHeader>
            <CardTitle>Detalhes</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">

            <div>
              <Label>Horário</Label>
              <Input v-model="horarioInicio" type="time"/>
              <p class="text-xs text-gray-500 mt-1">
                Funcionamento: {{ appStore.parametros.horarioAbertura }} às {{ appStore.parametros.horarioFechamento }}
              </p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <Label>Ciclo Atual</Label>
                <Input :model-value="ultimoAgendamento?.cicloAtual ? ultimoAgendamento.cicloAtual + 1 : 1"
                       class="bg-gray-50"
                       readonly type="number"/>
              </div>
              <div>
                <Label>Dia do Ciclo</Label>
                <Input v-model="diaCiclo"/>
              </div>
            </div>

            <div><Label>Observações</Label><Textarea v-model="observacoes"/></div>
            <Button class="w-full" @click="preValidarAgendamento">Confirmar Agendamento</Button>
          </CardContent>
        </Card>
      </div>
    </div>

    <Dialog v-model:open="confirmacaoOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2 text-amber-600">
            <AlertTriangle class="h-5 w-5"/>
            Atenção Necessária
          </DialogTitle>
          <DialogDescription>
            O agendamento apresenta os seguintes alertas. Como enfermeiro(a), você tem autonomia para prosseguir se
            julgar necessário.
          </DialogDescription>
        </DialogHeader>

        <div class="py-4">
          <ul class="list-disc list-inside space-y-2 text-sm text-gray-700">
            <li v-for="(aviso, idx) in listaAvisos" :key="idx">
              {{ aviso }}
            </li>
          </ul>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="confirmacaoOpen = false">Cancelar</Button>
          <Button variant="destructive" @click="realizarAgendamento">Agendar Mesmo Assim</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
