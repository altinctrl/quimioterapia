<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {useAuthStore} from '@/stores/auth'
import type {Paciente} from '@/types'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Badge} from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import {
  Activity,
  AlertCircle,
  ArrowLeft,
  Check,
  Edit,
  FileText,
  Phone,
  Save,
  Search,
  UserPlus,
  X
} from 'lucide-vue-next'
import AgendamentoDetalhesModal from './modals/AgendamentoDetalhesModal.vue'
import PrescricaoHistoricoModal from './modals/PrescricaoHistoricoModal.vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()

const page = ref(1)
const perPage = ref(10)
const termoBusca = ref('')
const pacienteSelecionado = ref<Paciente | null>(null)
const modoEdicao = ref(false)
const dadosEditados = ref<Partial<Paciente>>({})
const dialogNovoPaciente = ref(false)

const podeEditar = computed(() => {
  return authStore.user?.role !== 'farmacia'
})

const agendamentoDetalhesOpen = ref(false)
const prescricaoDetalhesOpen = ref(false)
const agendamentoSelecionado = ref<any>(null)
const prescricaoSelecionada = ref<any>(null)


const termoExterno = ref('')
const resultadosExternos = ref<Paciente[]>([])
const buscandoExterno = ref(false)

const carregarPacienteDaUrl = async () => {
  if (route.query.pacienteId) {
    const pid = route.query.pacienteId as string
    const p = appStore.getPacienteById(pid)
    if (p) {
      pacienteSelecionado.value = p
      dadosEditados.value = JSON.parse(JSON.stringify(p))

      await appStore.fetchPrescricoes(pid)
      await appStore.fetchAgendamentos(pid)
    }
  } else {
    pacienteSelecionado.value = null
  }
}

const carregarDadosPagina = async () => {
  await appStore.fetchPacientes(page.value, perPage.value, termoBusca.value)
  const promises = appStore.pacientes.map(p => appStore.fetchPrescricoes(p.id))
  await Promise.all(promises)
}

watch([page, termoBusca], () => {
  carregarDadosPagina()
}, {immediate: true})

const getProtocoloLista = (pid: string) => {
  const lista = appStore.getPrescricoesPorPaciente(pid)
  if (!lista.length) return '-'

  const ultima = lista.sort((a, b) => new Date(b.dataPrescricao).getTime() - new Date(a.dataPrescricao).getTime())[0]

  if (ultima.protocoloId) {
    return appStore.protocolos.find(p => p.id === ultima.protocoloId)?.nome || '-'
  }
  return ultima.protocolo || '-'
}

onMounted(() => {
  carregarPacienteDaUrl()
})

watch(() => route.query.pacienteId, () => {
  carregarPacienteDaUrl()
})

const calcularIdade = (dataNasc: string | Date | undefined) => {
  if (!dataNasc) return 0
  const hoje = new Date()
  const nasc = new Date(dataNasc)
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const m = hoje.getMonth() - nasc.getMonth()
  if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) {
    idade--
  }
  return idade
}

const handleVerDetalhesAgendamento = (agendamento: any) => {
  agendamentoSelecionado.value = agendamento
  agendamentoDetalhesOpen.value = true
}

const handleVerDetalhesPrescricao = (prescricao: any) => {
  prescricaoSelecionada.value = prescricao
  prescricaoDetalhesOpen.value = true
}

const pacientesFiltrados = computed(() => {
  if (!termoBusca.value || termoBusca.value.length < 2) return appStore.pacientes
  const termo = termoBusca.value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  return appStore.pacientes.filter((paciente) => {
    const nomeNormalizado = paciente.nome.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    const cpfLimpo = paciente.cpf?.replace(/[.\-]/g, '') || ''
    const termoBuscaLimpo = termo.replace(/[.\-]/g, '')
    return (
        nomeNormalizado.includes(termo) ||
        paciente.registro.toLowerCase().includes(termo) ||
        cpfLimpo.includes(termoBuscaLimpo)
    )
  })
})

const handleBuscarExterno = async () => {
  if (termoExterno.value.length < 3) {
    toast.warning("Digite pelo menos 3 caracteres")
    return
  }

  buscandoExterno.value = true
  try {
    const res = await api.get('/api/pacientes/externo/buscar', {
      params: {termo: termoExterno.value}
    })
    resultadosExternos.value = res.data
    if (res.data.length === 0) toast.info("Nenhum paciente encontrado no sistema externo.")
  } catch (e) {
    toast.error("Erro ao buscar no sistema externo")
  } finally {
    buscandoExterno.value = false
  }
}

const verificarCadastroLocal = (cpfExterno: string) => {
  return appStore.pacientes.some(p => p.cpf === cpfExterno)
}

const handleImportarPaciente = async (pacienteExterno: Paciente) => {
  const jaEstavaCadastrado = verificarCadastroLocal(pacienteExterno.cpf)

  try {
    const pacienteRetornado = await appStore.adicionarPaciente(pacienteExterno)

    if (jaEstavaCadastrado) {
      pacienteSelecionado.value = pacienteRetornado
      dialogNovoPaciente.value = false
      termoExterno.value = ''
      resultadosExternos.value = []
    } else {
      toast.success(`Paciente ${pacienteExterno.nome} importado com sucesso!`)
    }

  } catch (e) {
    console.error(e)
  }
}

watch(dialogNovoPaciente, async (estaAberto) => {
  if (!estaAberto) {
    await appStore.fetchPacientes()
  }
})

const handleSelecionarPaciente = (paciente: Paciente) => {
  router.push({query: {pacienteId: paciente.id}})
}

const handleVoltar = () => {
  if (route.query.pacienteId) {
    router.push({query: {}})
  } else {
    pacienteSelecionado.value = null
    modoEdicao.value = false
  }
}

const handleSalvarEdicao = () => {
  if (pacienteSelecionado.value && pacienteSelecionado.value.id) {
    const idx = appStore.pacientes.findIndex(p => p.id === pacienteSelecionado.value?.id)
    if (idx !== -1) {
      appStore.pacientes[idx] = {...appStore.pacientes[idx], ...dadosEditados.value} as Paciente
      pacienteSelecionado.value = appStore.pacientes[idx]
    }
  }
  modoEdicao.value = false
}

const handleCancelarEdicao = () => {
  dadosEditados.value = JSON.parse(JSON.stringify(pacienteSelecionado.value))
  modoEdicao.value = false
}

const agendamentosDoPaciente = computed(() => {
  return pacienteSelecionado.value
      ? appStore.agendamentos.filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      : []
})

const prescricoesDoPaciente = computed(() => {
  return pacienteSelecionado.value
      ? appStore.prescricoes.filter(p => p.pacienteId === pacienteSelecionado.value?.id)
      : []
})

const protocoloAtual = computed(() => {
  if (!pacienteSelecionado.value) return null

  const prescricoes = appStore.prescricoes.filter(p => p.pacienteId === pacienteSelecionado.value?.id)

  if (prescricoes.length > 0) {
    const ultima = prescricoes.sort((a, b) => new Date(b.dataPrescricao).getTime() - new Date(a.dataPrescricao).getTime())[0]

    if (ultima.protocoloId) {
      const proto = appStore.protocolos.find(p => p.id === ultima.protocoloId)
      if (proto) return proto
    }
    if (ultima.protocolo) {
      return {nome: ultima.protocolo} as any
    }
  }
  return null
})

const ultimoAgendamento = computed(() => {
  if (!pacienteSelecionado.value) return null
  const agendamentos = appStore.agendamentos
      .filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())

  return agendamentos[0] || null
})

const getStatusBadge = (status: string) => {
  if (!status) return 'bg-gray-100 text-gray-700'
  return appStore.getStatusConfig(status).cor
}

const getStatusLabel = (status: string) => {
  if (!status) return '-'
  return appStore.getStatusConfig(status).label
}

const formatarStatusPrescricao = (status: string) => {
  const mapa: Record<string, string> = {
    'ativa': 'Ativa',
    'concluida': 'Concluída',
    'pausada': 'Pausada',
    'cancelada': 'Cancelada'
  }
  return mapa[status] || status.charAt(0).toUpperCase() + status.slice(1)
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Pacientes</h1>
    <AgendamentoDetalhesModal
        :agendamento="agendamentoSelecionado"
        :open="agendamentoDetalhesOpen"
        :paciente-nome="pacienteSelecionado?.nome"
        @update:open="agendamentoDetalhesOpen = $event"
    />

    <PrescricaoHistoricoModal
        :open="prescricaoDetalhesOpen"
        :paciente-nome="pacienteSelecionado?.nome"
        :prescricao="prescricaoSelecionada"
        @update:open="prescricaoDetalhesOpen = $event"
    />

    <div v-if="!pacienteSelecionado" class="space-y-6">
      <Card>
        <CardContent class="pt-6">
          <div class="flex gap-3">
            <div class="flex-1 relative">
              <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"/>
              <Input
                  v-model="termoBusca"
                  class="pl-10"
                  placeholder="Buscar por nome, CPF ou prontuário..."
              />
            </div>

            <Dialog v-if="podeEditar" v-model:open="dialogNovoPaciente">
              <DialogTrigger as-child>
                <Button class="flex items-center gap-2">
                  <UserPlus class="h-4 w-4"/>
                  Novo Paciente
                </Button>
              </DialogTrigger>
              <DialogContent class="max-w-3xl">
                <DialogHeader>
                  <DialogTitle>Importar Paciente do AGHU</DialogTitle>
                  <DialogDescription>
                    Busque na base legado para cadastrar no sistema de Quimioterapia.
                  </DialogDescription>
                </DialogHeader>

                <div class="space-y-4">
                  <div class="flex gap-2">
                    <Input
                        v-model="termoExterno"
                        placeholder="Nome, CPF ou Prontuário..."
                        @keyup.enter="handleBuscarExterno"
                    />
                    <Button :disabled="buscandoExterno" @click="handleBuscarExterno">
                      <Search class="h-4 w-4 mr-2"/>
                      {{ buscandoExterno ? 'Buscando...' : 'Buscar' }}
                    </Button>
                  </div>

                  <!-- Lista de Resultados -->
                  <div class="border rounded-md max-h-[300px] overflow-y-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Nome</TableHead>
                          <TableHead>CPF</TableHead>
                          <TableHead>Nascimento</TableHead>
                          <TableHead class="text-right">Ação</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow v-if="resultadosExternos.length === 0">
                          <TableCell class="text-center text-gray-500 py-4" colspan="4">
                            {{ buscandoExterno ? 'Pesquisando...' : 'Faça uma busca para ver os resultados.' }}
                          </TableCell>
                        </TableRow>

                        <TableRow v-for="p in resultadosExternos" :key="p.registro"
                                  :class="verificarCadastroLocal(p.cpf) ? 'bg-blue-50/50' : ''">
                          <TableCell>
                            <div class="flex items-center gap-2">
                              {{ p.nome }}
                              <!-- INDICADOR VISUAL -->
                              <Badge v-if="verificarCadastroLocal(p.cpf)"
                                     class="h-5 px-1.5 text-[10px] bg-green-100 text-green-700 border-green-200 gap-1 hover:bg-green-100"
                                     variant="secondary">
                                <Check class="h-3 w-3"/>
                                Cadastrado
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell>{{ p.cpf }}</TableCell>
                          <TableCell>{{ new Date(p.dataNascimento).toLocaleDateString() }}</TableCell>
                          <TableCell class="text-right">
                            <!-- Botão muda de texto dependendo se já existe -->
                            <Button
                                :variant="verificarCadastroLocal(p.cpf) ? 'outline' : 'secondary'"
                                size="sm"
                                @click="handleImportarPaciente(p)"
                            >
                              {{ verificarCadastroLocal(p.cpf) ? 'Selecionar' : 'Importar' }}
                            </Button>
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            {{ termoBusca ? `${pacientesFiltrados.length} paciente(s) encontrado(s)` : 'Todos os Pacientes' }}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Registro</TableHead>
                <TableHead>CPF</TableHead>
                <TableHead>Idade</TableHead>
                <TableHead>Telefone</TableHead>
                <TableHead>Protocolo Atual</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="pacientesFiltrados.length === 0">
                <TableCell class="text-center text-gray-500" colspan="6">
                  Nenhum paciente encontrado
                </TableCell>
              </TableRow>
              <TableRow
                  v-for="paciente in pacientesFiltrados"
                  v-else
                  :key="paciente.id"
                  class="cursor-pointer hover:bg-gray-50"
                  @click="handleSelecionarPaciente(paciente)"
              >
                <TableCell>{{ paciente.nome }}</TableCell>
                <TableCell>{{ paciente.registro }}</TableCell>
                <TableCell>{{ paciente.cpf }}</TableCell>
                <TableCell>{{ calcularIdade(paciente.dataNascimento) }} anos</TableCell>
                <TableCell>{{ paciente.telefone }}</TableCell>
                <TableCell>
                  <Badge class="font-normal" variant="outline">
                    {{ getProtocoloLista(paciente.id) }}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <div class="relative flex items-center justify-center pt-4 mt-4 border-t">

            <div class="absolute left-0 text-sm text-gray-500">
              Total de Pacientes: <strong>{{ appStore.totalPacientes }}</strong>
            </div>

            <div class="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                :disabled="page === 1"
                @click="page--"
              >
                Anterior
              </Button>

              <span class="text-sm font-medium mx-4">
                Página {{ page }} de {{ Math.ceil(appStore.totalPacientes / perPage) || 1 }}
              </span>

              <Button
                variant="outline"
                size="sm"
                :disabled="page >= (Math.ceil(appStore.totalPacientes / perPage) || 1)"
                @click="page++"
              >
                Próxima
              </Button>
            </div>

          </div>
        </CardContent>
      </Card>
    </div>

    <div v-else class="space-y-6">
      <div class="flex items-center justify-between">
        <Button class="flex items-center gap-2" variant="outline" @click="handleVoltar">
          <ArrowLeft class="h-4 w-4"/>
          Voltar
        </Button>

        <div class="flex items-center gap-3">
          <Button
              v-if="authStore.user?.role === 'medico'"
              class="flex items-center gap-2"
              @click="router.push({ name: 'Prescricao', query: { pacienteId: pacienteSelecionado.id } })"
          >
            <FileText class="h-4 w-4"/>
            Nova Prescrição
          </Button>

          <template v-if="podeEditar">
            <Button
                v-if="!modoEdicao"
                class="flex items-center gap-2"
                variant="outline"
                @click="modoEdicao = true"
            >
              <Edit class="h-4 w-4"/>
              Editar
            </Button>
            <div v-else class="flex gap-2">
              <Button class="flex items-center gap-2" variant="outline" @click="handleCancelarEdicao">
                <X class="h-4 w-4"/>
                Cancelar
              </Button>
              <Button class="flex items-center gap-2" @click="handleSalvarEdicao">
                <Save class="h-4 w-4"/>
                Salvar
              </Button>
            </div>
          </template>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div class="flex flex-col gap-4">
            <div>
              <CardTitle class="text-2xl">{{ pacienteSelecionado.nome }}</CardTitle>
              <div class="flex items-center gap-4 mt-2 text-sm text-gray-600">
                <span><span class="font-medium text-gray-900">Registro:</span> {{ pacienteSelecionado.registro }}</span>
                <span><span class="font-medium text-gray-900">CPF:</span> {{ pacienteSelecionado.cpf }}</span>
              </div>
            </div>

            <div class="bg-blue-50 border border-blue-100 rounded-lg p-4 flex flex-wrap gap-6 items-center">
              <div class="flex items-center gap-2">
                <Activity class="h-5 w-5 text-blue-600"/>
                <span class="text-sm font-medium text-blue-900">Status Atual do Tratamento</span>
              </div>
              <div class="h-8 w-px bg-blue-200 hidden sm:block"></div>

              <div>
                <p class="text-xs text-blue-700 uppercase tracking-wide">Protocolo</p>
                <p class="font-medium text-blue-950">{{ protocoloAtual?.nome || 'Nenhum definido' }}</p>
              </div>

              <div>
                <p class="text-xs text-blue-700 uppercase tracking-wide">Ciclo Atual</p>
                <p class="font-medium text-blue-950">{{ ultimoAgendamento?.cicloAtual || '-' }}</p>
              </div>

              <div>
                <p class="text-xs text-blue-700 uppercase tracking-wide">Dia do Ciclo</p>
                <p class="font-medium text-blue-950">{{ ultimoAgendamento?.diaCiclo || '-' }}</p>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent class="space-y-8">
          <div>
            <h3 class="text-gray-900 mb-4 font-medium text-lg border-b pb-2">Dados Cadastrais</h3>

            <div class="grid grid-cols-1 gap-6">
              <div class="grid grid-cols-2 gap-4">
                <div><Label>Peso (kg)</Label><Input v-model.number="dadosEditados.peso" :disabled="!modoEdicao"
                                                    class="mt-1" type="number"/></div>
                <div><Label>Altura (cm)</Label><Input v-model.number="dadosEditados.altura" :disabled="!modoEdicao"
                                                      class="mt-1" type="number"/></div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div><Label>Data de Nascimento</Label><Input v-model="dadosEditados.dataNascimento"
                                                             :disabled="!modoEdicao"
                                                             class="mt-1" type="date"/></div>
                <div><Label>Idade</Label><Input :model-value="`${pacienteSelecionado.idade} anos`"
                                                class="mt-1 bg-gray-50"
                                                disabled/></div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div><Label>Telefone</Label><Input v-model="dadosEditados.telefone" :disabled="!modoEdicao"
                                                   class="mt-1"/></div>
                <div><Label>Email</Label><Input v-model="dadosEditados.email" :disabled="!modoEdicao" class="mt-1"
                                                type="email"/></div>
              </div>
            </div>
          </div>

          <div>
            <h3 class="text-gray-900 mb-4 font-medium text-lg border-b pb-2 flex items-center gap-2">
              <Phone class="h-5 w-5"/>
              Contatos de Emergência
            </h3>

            <div v-if="dadosEditados.contatosEmergencia && dadosEditados.contatosEmergencia.length > 0"
                 class="space-y-4">
              <div v-for="(contato, idx) in dadosEditados.contatosEmergencia" :key="idx"
                   class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg border">
                <div><Label class="text-xs text-gray-500 mb-1 block">Nome</Label><Input v-model="contato.nome"
                                                                                        :disabled="!modoEdicao"/></div>
                <div><Label class="text-xs text-gray-500 mb-1 block">Parentesco</Label><Input
                    v-model="contato.parentesco"
                    :disabled="!modoEdicao"/>
                </div>
                <div><Label class="text-xs text-gray-500 mb-1 block">Telefone</Label><Input v-model="contato.telefone"
                                                                                            :disabled="!modoEdicao"/>
                </div>
              </div>
            </div>
            <div v-else class="text-gray-500 text-sm italic py-2">
              Nenhum contato de emergência cadastrado.
            </div>
          </div>

          <div>
            <h3 class="text-red-700 mb-2 font-medium text-lg flex items-center gap-2">
              <AlertCircle class="h-5 w-5"/>
              Observações Clínicas / Alergias
            </h3>
            <Textarea
                v-model="dadosEditados.observacoesClinicas"
                :disabled="!modoEdicao"
                class="mt-1 min-h-[100px] border-red-200 focus:border-red-400 bg-red-50/30"
                placeholder="Registre alergias e observações importantes..."
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Histórico Clínico</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="agendamentos">
            <TabsList class="grid w-full grid-cols-2">
              <TabsTrigger value="agendamentos">Agendamentos</TabsTrigger>
              <TabsTrigger value="prescricoes">Prescrições</TabsTrigger>
            </TabsList>

            <TabsContent class="mt-4" value="agendamentos">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Turno</TableHead>
                    <TableHead>Horário</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead class="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-if="agendamentosDoPaciente.length === 0">
                    <TableCell class="text-center text-gray-500 py-8" colspan="5">Nenhum agendamento encontrado
                    </TableCell>
                  </TableRow>
                  <TableRow
                      v-for="ag in agendamentosDoPaciente"
                      v-else
                      :key="ag.id"
                      class="cursor-pointer hover:bg-gray-50"
                      @click="handleVerDetalhesAgendamento(ag)"
                  >
                    <TableCell>{{ new Date(ag.data).toLocaleDateString('pt-BR') }}</TableCell>
                    <TableCell class="capitalize">{{ ag.turno }}</TableCell>
                    <TableCell>{{ ag.horarioInicio }}</TableCell>
                    <TableCell>
                      <Badge :class="getStatusBadge(ag.status)" variant="outline">
                        {{ getStatusLabel(ag.status) }}
                      </Badge>
                    </TableCell>
                    <TableCell class="text-right">
                      <Button size="sm" variant="ghost" @click.stop="handleVerDetalhesAgendamento(ag)">Ver Detalhes
                      </Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TabsContent>

            <TabsContent class="mt-4" value="prescricoes">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Protocolo</TableHead>
                    <TableHead>Ciclo</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead class="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-if="prescricoesDoPaciente.length === 0">
                    <TableCell class="text-center text-gray-500 py-8" colspan="5">Nenhuma prescrição encontrada
                    </TableCell>
                  </TableRow>

                  <TableRow
                      v-for="p in prescricoesDoPaciente"
                      v-else
                      :key="p.id"
                      class="cursor-pointer hover:bg-gray-50"
                      @click="handleVerDetalhesPrescricao(p)"
                  >
                    <TableCell>{{ new Date(p.dataPrescricao).toLocaleDateString('pt-BR') }}</TableCell>
                    <TableCell>{{ p.protocolo || 'N/A' }}</TableCell>
                    <TableCell>{{ p.cicloAtual }} / {{ p.ciclosTotal }}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{{ formatarStatusPrescricao(p.status) }}</Badge>
                    </TableCell>
                    <TableCell class="text-right">
                      <Button size="sm" variant="ghost" @click.stop="handleVerDetalhesPrescricao(p)">Ver</Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
