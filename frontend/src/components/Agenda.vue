<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {
  Calendar as CalendarIcon,
  CalendarClock,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Clock,
  MoreVertical,
  Plus,
  Tag
} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import type {StatusPaciente} from '@/types'

import TagsModal from './modals/TagsModal.vue'

const router = useRouter()
const appStore = useAppStore()
const dataSelecionada = ref(new Date().toISOString().split('T')[0])

const tagsModalOpen = ref(false)
const tagsModalData = ref<{ id: string; tags: string[] } | null>(null)

const agendamentosDoDia = computed(() => {
  return appStore.getAgendamentosDoDia(dataSelecionada.value)
      .sort((a, b) => a.horarioInicio.localeCompare(b.horarioInicio))
})

const metricas = computed(() => {
  const list = agendamentosDoDia.value
  return {
    total: list.length,
    manha: list.filter(a => a.turno === 'manha').length,
    tarde: list.filter(a => a.turno === 'tarde').length,
    emAndamento: list.filter(a => ['em-infusao', 'aguardando-medicamento'].includes(a.status)).length,
    concluidos: list.filter(a => a.status === 'concluido').length
  }
})

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

const irParaProntuario = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const abrirTagsModal = (agendamento: any) => {
  tagsModalData.value = {id: agendamento.id, tags: agendamento.tags || []}
  tagsModalOpen.value = true
}

const salvarTags = (id: string, tags: string[]) => {
  const agendamento = appStore.agendamentos.find(a => a.id === id)
  if (agendamento) {
    agendamento.tags = tags
  }
  tagsModalOpen.value = false
}

const handleAlterarStatusPaciente = (agendamentoId: string, event: Event) => {
  const novoStatus = (event.target as HTMLSelectElement).value as StatusPaciente
  appStore.atualizarStatusAgendamento(agendamentoId, novoStatus)
}

const getPaciente = (id: string) => appStore.getPacienteById(id)
const getProtocolo = (id?: string) => id ? appStore.protocolos.find(p => p.id === id) : null

const opcoesStatusPaciente = computed(() => {
  return appStore.statusConfig.filter(s =>
      s.tipo === 'paciente' &&
      s.id !== 'remarcado'
  )
})

const getStatusDotColor = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config.cor.split(' ')[0]
}

const formatarStatus = (status: string) => {
  if (!status) return ''
  return status.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const modalRemarcarOpen = ref(false)
const dadosRemarcar = ref({
  idOriginal: '',
  pacienteNome: '',
  dataAtual: '',
  horarioAtual: '',
  novaData: '',
  novoHorario: '',
  motivo: ''
})

const abrirModalRemarcar = (agendamento: any) => {
  const paciente = getPaciente(agendamento.pacienteId)

  dadosRemarcar.value = {
    idOriginal: agendamento.id,
    pacienteNome: paciente?.nome || 'Desconhecido',
    dataAtual: agendamento.data.split('-').reverse().join('/'),
    horarioAtual: agendamento.horarioInicio,
    novaData: '',
    novoHorario: agendamento.horarioInicio,
    motivo: ''
  }
  modalRemarcarOpen.value = true
}

const confirmarRemarcacao = () => {
  if (!dadosRemarcar.value.novaData || !dadosRemarcar.value.novoHorario || !dadosRemarcar.value.motivo) {
    toast.error("Preencha todos os campos")
    alert("Preencha data, horário e motivo.")
    return
  }

  appStore.remarcarAgendamento(
      dadosRemarcar.value.idOriginal,
      dadosRemarcar.value.novaData,
      dadosRemarcar.value.novoHorario,
      dadosRemarcar.value.motivo
  )

  modalRemarcarOpen.value = false
  toast.success("Agendamento remarcado com sucesso!")
}

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
  const pacientesIds = [...new Set(appStore.agendamentos.map(a => a.pacienteId))]
  if (pacientesIds.length > 0) {
    await Promise.all(pacientesIds.map(id => appStore.fetchPrescricoes(id)))
  }
}, {immediate: true})

const getProtocoloInferido = (pid: string) => appStore.getProtocoloPeloHistorico(pid)
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">

    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900">Agenda</h1>
    </div>

    <TagsModal
        :agendamento-id="tagsModalData?.id || ''"
        :open="tagsModalOpen"
        :tags-atuais="tagsModalData?.tags || []"
        @salvar="salvarTags"
        @update:open="tagsModalOpen = $event"
    />

    <Dialog v-model:open="modalRemarcarOpen">
      <DialogContent class="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Remarcar Agendamento</DialogTitle>
          <DialogDescription>
            O agendamento original será mantido como histórico.
          </DialogDescription>
        </DialogHeader>

        <div class="bg-blue-50 p-3 rounded-md border border-blue-100 mb-2 text-sm">
          <p class="font-bold text-blue-900">{{ dadosRemarcar.pacienteNome }}</p>
          <div class="flex gap-4 text-blue-700 mt-1">
            <span>De: <strong>{{ dadosRemarcar.dataAtual }}</strong></span>
            <span>às <strong>{{ dadosRemarcar.horarioAtual }}</strong></span>
          </div>
        </div>

        <div class="grid gap-4 py-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label>Nova Data</Label>
              <Input v-model="dadosRemarcar.novaData" type="date"/>
            </div>
            <div class="space-y-2">
              <Label>Novo Horário</Label>
              <Input v-model="dadosRemarcar.novoHorario" type="time"/>
            </div>
          </div>

          <div class="space-y-2">
            <Label>Motivo</Label>
            <Textarea
                v-model="dadosRemarcar.motivo"
                placeholder="Ex: Paciente gripado, solicitou adiamento..."
            />
          </div>
        </div>

        <div class="flex justify-end gap-2">
          <Button variant="outline" @click="modalRemarcarOpen = false">Cancelar</Button>
          <Button @click="confirmarRemarcacao">Confirmar Remarcação</Button>
        </div>
      </DialogContent>
    </Dialog>

    <Card>
      <CardContent class="pt-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <Button size="icon" variant="outline" @click="handleDiaAnterior">
              <ChevronLeft class="h-4 w-4"/>
            </Button>
            <div class="flex items-center gap-2">
              <CalendarIcon class="h-5 w-5 text-gray-500"/>
              <Input v-model="dataSelecionada" class="w-auto" type="date"/>
            </div>
            <Button size="icon" variant="outline" @click="handleProximoDia">
              <ChevronRight class="h-4 w-4"/>
            </Button>
          </div>
          <Button class="flex items-center gap-2" @click="router.push('/agendamento')">
            <Plus class="h-4 w-4"/>
            Novo Agendamento
          </Button>
        </div>
      </CardContent>
    </Card>

    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <Card class="p-4 bg-white shadow-sm rounded-xl">
        <div class="text-sm text-gray-500">Total</div>
        <div class="text-2xl font-bold">{{ metricas.total }}</div>
      </Card>
      <Card class="p-4 bg-white shadow-sm rounded-xl">
        <div class="text-sm text-gray-500">Manhã</div>
        <div class="text-2xl font-bold text-blue-600">{{ metricas.manha }}</div>
      </Card>
      <Card class="p-4 bg-white shadow-sm rounded-xl">
        <div class="text-sm text-gray-500">Tarde</div>
        <div class="text-2xl font-bold text-purple-600">{{ metricas.tarde }}</div>
      </Card>
      <Card class="p-4 bg-white shadow-sm rounded-xl">
        <div class="text-sm text-gray-500">Andamento</div>
        <div class="text-2xl font-bold text-green-600">{{ metricas.emAndamento }}</div>
      </Card>
      <Card class="p-4 bg-white shadow-sm rounded-xl">
        <div class="text-sm text-gray-500">Concluídos</div>
        <div class="text-2xl font-bold text-gray-600">{{ metricas.concluidos }}</div>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Agendamentos</CardTitle>
      </CardHeader>
      <CardContent>
        <div v-if="agendamentosDoDia.length === 0" class="text-center py-12 text-gray-500">
          <p>Nenhum agendamento para este dia</p>
        </div>
        <Table v-else>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[100px]">Horário</TableHead>
              <TableHead class="min-w-[150px]">Paciente</TableHead>
              <TableHead class="min-w-[100px]">Protocolo</TableHead>
              <TableHead class="min-w-[85px]">Ciclo / Dia</TableHead>
              <TableHead class="min-w-[240px]">Status Paciente</TableHead>
              <TableHead class="min-w-[140px]">Status Farmácia</TableHead>
              <TableHead class="min-w-[120px]">Previsão</TableHead>
              <TableHead class="min-w-[100px]">Tags</TableHead>
              <TableHead class="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow
                v-for="ag in agendamentosDoDia"
                :key="ag.id"
                :class="{ 'bg-gray-50 opacity-60 grayscale': ag.status === 'remarcado' }"
            >
              <TableCell>
                <div class="font-mono text-sm">{{ ag.horarioInicio }}</div>
                <div class="text-xs text-muted-foreground capitalize">{{ ag.turno }}</div>
              </TableCell>

              <TableCell>
                <button
                  class="text-left font-medium hover:text-blue-600 underline truncate max-w-[180px]"
                  @click="irParaProntuario(ag.pacienteId)"
                >
                  {{ ag.paciente?.nome || getPaciente(ag.pacienteId)?.nome || 'Paciente não encontrado' }}
                </button>
                <div class="text-xs text-gray-500">
                   {{ ag.paciente?.registro || getPaciente(ag.pacienteId)?.registro }}
                </div>
              </TableCell>

              <TableCell>
                <span class="text-sm font-medium text-gray-700 block">
                  {{ getProtocoloInferido(ag.pacienteId)?.nome || '-' }}
                </span>
              </TableCell>

              <TableCell>
                <div v-if="ag.diaCiclo" class="text-sm">
                  <span class="font-medium block">Ciclo {{ ag.cicloAtual }}</span>
                  <span class="text-gray-500">{{ ag.diaCiclo }}</span>
                </div>
                <span v-else>-</span>
              </TableCell>

              <TableCell>
                <div class="flex items-center gap-2">
                  <div :class="['h-2.5 w-2.5 rounded-full flex-shrink-0', getStatusDotColor(ag.status)]"/>

                  <div class="relative w-full">
                    <select
                        :disabled="ag.status === 'remarcado'"
                        :value="ag.status"
                        class="flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-1 pr-8 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none truncate"
                        @change="(e) => handleAlterarStatusPaciente(ag.id, e)"
                    >
                      <option
                          v-for="opcao in opcoesStatusPaciente"
                          :key="opcao.id"
                          :value="opcao.id"
                      >
                        {{ opcao.label }}
                      </option>
                    </select>
                    <ChevronDown class="absolute right-2 top-2.5 h-4 w-4 opacity-50 pointer-events-none"/>
                  </div>
                </div>
              </TableCell>

              <TableCell>
                <span class="text-sm text-gray-600">{{ formatarStatus(ag.statusFarmacia) }}</span>
              </TableCell>

              <TableCell>
                <div v-if="ag.horarioPrevisaoEntrega"
                     class="flex items-center gap-1 text-blue-700 font-medium bg-blue-50 px-2 py-1 rounded w-fit">
                  <Clock class="h-3 w-3"/>
                  {{ ag.horarioPrevisaoEntrega }}
                </div>
                <span v-else class="text-gray-400 text-xs">-</span>
              </TableCell>

              <TableCell>
                <div class="flex flex-wrap gap-1 items-center">
                  <Badge v-for="(tag, i) in (ag.tags || []).slice(0, 2)" :key="i" class="text-[10px] px-1 h-5"
                         variant="outline">
                    {{ tag }}
                  </Badge>
                  <Button class="h-6 w-6" size="icon" variant="ghost" @click="abrirTagsModal(ag)">
                    <Tag class="h-3 w-3"/>
                  </Button>
                </div>
              </TableCell>
              <TableCell>
                <span v-if="ag.status === 'remarcado'" class="text-xs font-medium italic text-gray-400">
                  Remarcado
                </span>

                <DropdownMenu v-else>
                  <DropdownMenuTrigger as-child>
                    <Button class="h-8 w-8" size="icon" variant="ghost">
                      <MoreVertical class="h-4 w-4"/>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Ações</DropdownMenuLabel>
                    <DropdownMenuItem @click="abrirModalRemarcar(ag)">
                      <CalendarClock class="mr-2 h-4 w-4"/>
                      Remarcar
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
</template>
