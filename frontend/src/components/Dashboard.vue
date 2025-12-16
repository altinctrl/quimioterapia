<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {
  Activity,
  AlertTriangle,
  Ban,
  CalendarDays,
  CheckCircle2,
  FileText,
  Phone,
  Pill,
  PlusCircle,
  User,
  Users
} from 'lucide-vue-next'
import type {Agendamento} from '@/types'

const router = useRouter()
const appStore = useAppStore()

onMounted(async () => {
  const hoje = new Date().toISOString().split('T')[0]
  await appStore.fetchAgendamentos(hoje, hoje)
})

const hoje = new Date().toISOString().split('T')[0]
const agendamentosHoje = computed(() => appStore.getAgendamentosDoDia(hoje))

const totalPacientes = computed(() => agendamentosHoje.value.length)
const emAtendimento = computed(() => agendamentosHoje.value.filter(a => ['em-triagem', 'aguardando-exame', 'aguardando-medicamento', 'em-infusao'].includes(a.status)).length)
const concluidos = computed(() => agendamentosHoje.value.filter(a => a.status === 'concluido').length)

const suspensos = computed(() => agendamentosHoje.value.filter(a => a.status === 'suspenso').length)
const intercorrencias = computed(() => agendamentosHoje.value.filter(a => a.status === 'intercorrencia').length)
const encaixes = computed(() => agendamentosHoje.value.filter(a => a.encaixe).length)

const statusFarmacia = computed(() => {
  const total = totalPacientes.value || 1
  const pendentes = agendamentosHoje.value.filter(a => a.statusFarmacia === 'pendente').length
  const preparando = agendamentosHoje.value.filter(a => a.statusFarmacia === 'em-preparacao').length
  const prontas = agendamentosHoje.value.filter(a => a.statusFarmacia === 'pronta' || a.statusFarmacia === 'enviada').length

  return {
    pendentes,
    preparando,
    prontas,
    progresso: Math.round((prontas / total) * 100)
  }
})

const proximosPacientes = computed(() => {
  return agendamentosHoje.value
      .filter(a => ['agendado', 'em-triagem', 'aguardando-exame'].includes(a.status))
      .sort((a, b) => a.horarioInicio.localeCompare(b.horarioInicio))
      .slice(0, 5)
      .map(a => ({
        ...a,
        paciente: appStore.getPacienteById(a.pacienteId)
      }))
})

const pacientesComAlertas = computed(() => {
  return agendamentosHoje.value
      .map(a => ({agendamento: a, paciente: appStore.getPacienteById(a.pacienteId)}))
      .filter(item => item.paciente?.observacoesClinicas)
})

const formatarStatus = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config ? config.label : statusId
}

const getStatusColor = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config ? config.cor : 'bg-gray-100 text-gray-700'
}

const detalhesOpen = ref(false)
const itemSelecionado = ref<{ agendamento: Agendamento, paciente: any } | null>(null)

const abrirDetalhes = (agendamento: Agendamento) => {
  const paciente = appStore.getPacienteById(agendamento.pacienteId)
  if (paciente) {
    itemSelecionado.value = {agendamento, paciente}
    detalhesOpen.value = true
  }
}

const irParaProntuario = () => {
  if (itemSelecionado.value?.paciente) {
    router.push({
      path: '/pacientes',
      query: {pacienteId: itemSelecionado.value.paciente.id}
    })
    detalhesOpen.value = false
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900">Painel de Controle</h1>
      <Button variant="outline" @click="router.push('/agenda')">
        <CalendarDays class="mr-2 h-4 w-4"/>
        Ver Agenda Completa
      </Button>
    </div>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total Hoje</CardTitle>
          <Users class="h-4 w-4 text-muted-foreground"/>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ totalPacientes }}</div>
          <p class="text-xs text-muted-foreground">Pacientes agendados</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Em Atendimento</CardTitle>
          <Activity class="h-4 w-4 text-blue-600"/>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-blue-600">{{ emAtendimento }}</div>
          <p class="text-xs text-muted-foreground">Infusão ou Triagem</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Concluídos</CardTitle>
          <CheckCircle2 class="h-4 w-4 text-green-600"/>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-600">{{ concluidos }}</div>
          <p class="text-xs text-muted-foreground">Altas do dia</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Farmácia (Prontas)</CardTitle>
          <Pill class="h-4 w-4 text-purple-600"/>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-purple-600">{{ statusFarmacia.prontas }} <span
              class="text-gray-400 text-lg font-normal">/ {{ totalPacientes }}</span></div>
          <p class="text-xs text-muted-foreground">{{ statusFarmacia.preparando }} em manipulação</p>
        </CardContent>
      </Card>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <div class="bg-blue-50 border border-blue-100 rounded-lg p-4 flex items-center justify-between">
        <div>
          <p class="text-xs font-bold text-blue-600 uppercase">Encaixes</p>
          <p class="text-2xl font-bold text-blue-900">{{ encaixes }}</p>
        </div>
        <PlusCircle class="h-8 w-8 text-blue-200"/>
      </div>

      <div class="bg-red-50 border border-red-100 rounded-lg p-4 flex items-center justify-between">
        <div>
          <p class="text-xs font-bold text-red-600 uppercase">Suspensos</p>
          <p class="text-2xl font-bold text-red-900">{{ suspensos }}</p>
        </div>
        <Ban class="h-8 w-8 text-red-200"/>
      </div>

      <div class="bg-orange-50 border border-orange-100 rounded-lg p-4 flex items-center justify-between">
        <div>
          <p class="text-xs font-bold text-orange-600 uppercase">Intercorrências</p>
          <p class="text-2xl font-bold text-orange-900">{{ intercorrencias }}</p>
        </div>
        <AlertTriangle class="h-8 w-8 text-orange-200"/>
      </div>
    </div>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-7">

      <Card class="col-span-4">
        <CardHeader>
          <CardTitle>Próximos Pacientes</CardTitle>
          <CardDescription>Clique no paciente para ver detalhes rápidos</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="proximosPacientes.length === 0" class="text-center py-8 text-gray-500">
            Nenhum paciente na fila imediata.
          </div>
          <div v-else class="space-y-2">
            <div
                v-for="item in proximosPacientes"
                :key="item.id"
                class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors border border-transparent hover:border-gray-100"
                @click="abrirDetalhes(item)"
            >
              <div class="flex items-center gap-4">
                <div class="bg-blue-100 text-blue-700 font-bold px-3 py-1.5 rounded text-sm min-w-[4rem] text-center">
                  {{ item.horarioInicio }}
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ item.paciente?.nome }}</p>
                  <div class="flex items-center gap-2 text-xs text-gray-500 mt-0.5">
                    <span>Ciclo {{ item.cicloAtual }}</span>
                    <span>•</span>
                    <span>{{ item.diaCiclo }}</span>
                    <span v-if="item.encaixe" class="text-blue-600 font-bold">• Encaixe</span>
                  </div>
                </div>
              </div>
              <Badge :class="getStatusColor(item.status)" variant="outline">
                {{ formatarStatus(item.status) }}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <div class="col-span-3 space-y-4">

        <Card class="border-l-4 border-l-yellow-400">
          <CardHeader class="pb-2">
            <CardTitle class="text-base flex items-center gap-2">
              <AlertTriangle class="h-4 w-4 text-yellow-600"/>
              Alertas Clínicos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div v-if="pacientesComAlertas.length === 0" class="text-sm text-gray-500 italic">
              Nenhuma observação crítica hoje.
            </div>
            <div v-else class="space-y-3 max-h-[200px] overflow-y-auto pr-2">
              <div v-for="(item, idx) in pacientesComAlertas" :key="idx"
                   class="bg-yellow-50 p-3 rounded-md text-sm border border-yellow-100 cursor-pointer hover:bg-yellow-100 transition-colors"
                   @click="abrirDetalhes(item.agendamento)"
              >
                <div class="flex justify-between items-start">
                  <p class="font-semibold text-yellow-900">{{ item.paciente?.nome }}</p>
                  <span class="text-[14px] text-yellow-700 font-mono">{{ item.agendamento.horarioInicio }}</span>
                </div>
                <p class="text-yellow-800 mt-1">{{ item.paciente?.observacoesClinicas }}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-base flex items-center gap-2">
              <Pill class="h-4 w-4 text-purple-600"/>
              Fluxo da Farmácia
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div>
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-600">Progresso</span>
                <span class="font-bold">{{ statusFarmacia.progresso }}%</span>
              </div>
              <div class="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                <div :style="`width: ${statusFarmacia.progresso}%`"
                     class="h-full bg-purple-600 transition-all duration-500"></div>
              </div>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center text-sm">
              <div class="bg-gray-50 p-2 rounded">
                <span class="block font-bold text-gray-700">{{ statusFarmacia.pendentes }}</span>
                <span class="text-xs text-gray-500">Pendente</span>
              </div>
              <div class="bg-blue-50 p-2 rounded border border-blue-100">
                <span class="block font-bold text-blue-700">{{ statusFarmacia.preparando }}</span>
                <span class="text-xs text-blue-600">Preparo</span>
              </div>
              <div class="bg-green-50 p-2 rounded border border-green-100">
                <span class="block font-bold text-green-700">{{ statusFarmacia.prontas }}</span>
                <span class="text-xs text-green-600">Prontas</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <Dialog v-model:open="detalhesOpen">
      <DialogContent class="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Resumo do Paciente</DialogTitle>
          <DialogDescription>Dados do agendamento atual</DialogDescription>
        </DialogHeader>

        <div v-if="itemSelecionado" class="grid gap-4 py-2">
          <div class="flex items-start gap-4">
            <div class="bg-blue-100 p-3 rounded-full">
              <User class="h-6 w-6 text-blue-700"/>
            </div>
            <div>
              <h3 class="font-bold text-lg text-gray-900">{{ itemSelecionado.paciente.nome }}</h3>
              <p class="text-sm text-gray-500">Reg: {{ itemSelecionado.paciente.registro }} •
                {{ itemSelecionado.paciente.idade }} anos</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm mt-2">
            <div class="bg-gray-50 p-3 rounded border">
              <p class="text-xs text-gray-500 uppercase font-bold mb-1">Status</p>
              <Badge :class="getStatusColor(itemSelecionado.agendamento.status)">
                {{ formatarStatus(itemSelecionado.agendamento.status) }}
              </Badge>
            </div>
            <div class="bg-gray-50 p-3 rounded border">
              <p class="text-xs text-gray-500 uppercase font-bold mb-1">Horário</p>
              <p class="font-medium flex items-center gap-2">
                {{ itemSelecionado.agendamento.horarioInicio }} - {{ itemSelecionado.agendamento.horarioFim }}
                <span v-if="itemSelecionado.agendamento.encaixe" class="text-xs bg-blue-100 text-blue-700 px-1 rounded">Extra</span>
              </p>
            </div>
          </div>

          <div v-if="itemSelecionado.paciente.observacoesClinicas"
               class="bg-yellow-50 p-3 rounded border border-yellow-200 text-sm">
            <p class="font-bold text-yellow-800 flex items-center gap-2 mb-1">
              <AlertTriangle class="h-3 w-3"/>
              Atenção Clínica
            </p>
            <p class="text-yellow-900">{{ itemSelecionado.paciente.observacoesClinicas }}</p>
          </div>

          <div class="space-y-1">
            <div class="flex items-center gap-2 text-sm text-gray-700">
              <Phone class="h-4 w-4 text-gray-400"/>
              <span>{{ itemSelecionado.paciente.telefone }}</span>
            </div>
            <div v-if="itemSelecionado.paciente.contatosEmergencia?.length" class="text-xs text-gray-500 ml-6">
              Emergência: {{ itemSelecionado.paciente.contatosEmergencia[0].nome }}
              ({{ itemSelecionado.paciente.contatosEmergencia[0].telefone }})
            </div>
          </div>
        </div>

        <DialogFooter class="flex gap-2 sm:justify-start">
          <Button class="flex-1" @click="irParaProntuario">
            <FileText class="mr-2 h-4 w-4"/>
            Prontuário
          </Button>
          <Button variant="outline" @click="detalhesOpen = false">Fechar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
