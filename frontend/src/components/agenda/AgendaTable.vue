<script lang="ts" setup>
import {computed} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {Button} from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {CalendarClock, ChevronDown, Clock, MoreVertical, Tag} from 'lucide-vue-next'
import type {Agendamento} from '@/types'

defineProps<{
  agendamentos: Agendamento[]
}>()

const emit = defineEmits<{
  (e: 'abrir-tags', agendamento: any): void
  (e: 'abrir-remarcar', agendamento: Agendamento): void
  (e: 'alterar-status', agendamento: Agendamento, novoStatus: string): void
}>()

const router = useRouter()
const appStore = useAppStore()

const getPaciente = (id: string) => appStore.getPacienteById(id)
const getProtocoloInferido = (pid: string) => appStore.getProtocoloPeloHistorico(pid)

const irParaProntuario = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const handleAlterarStatusPaciente = (agendamento: Agendamento, event: Event) => {
  const select = event.target as HTMLSelectElement
  const novoStatus = select.value
  const statusAntigo = agendamento.status
  emit('alterar-status', agendamento, novoStatus)
  select.value = statusAntigo
}

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
</script>

<template>
  <Table>
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
      <div v-if="agendamentos.length === 0" class="contents">
        <TableRow>
          <TableCell class="text-center py-12 text-gray-500" colspan="9">
            Nenhum agendamento para este dia
          </TableCell>
        </TableRow>
      </div>

      <TableRow
          v-for="ag in agendamentos"
          v-else
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
                  class="flex h-9 w-full items-center justify-between rounded-md border border-input bg-background
                         px-3 py-1 pr-8 text-sm ring-offset-background placeholder:text-muted-foreground
                         focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2
                         disabled:cursor-not-allowed disabled:opacity-50 appearance-none truncate"
                  @change="(e) => handleAlterarStatusPaciente(ag, e)"
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
            <Button class="h-6 w-6" size="icon" variant="ghost" @click="$emit('abrir-tags', ag)">
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
              <DropdownMenuItem @click="$emit('abrir-remarcar', ag)">
                <CalendarClock class="mr-2 h-4 w-4"/>
                Remarcar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>
</template>