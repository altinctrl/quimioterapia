<script lang="ts" setup>
import {computed} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {Button} from '@/components/ui/button'
import {ChevronDown, Clock, Tag} from 'lucide-vue-next'
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip'
import {type Agendamento, isInfusao} from '@/types'
import {formatarDuracao, getBadgeGrupo, getCorGrupo, getDuracaoAgendamento, getGrupoInfusao} from '@/utils/agendaUtils'
import {Checkbox} from "@/components/ui/checkbox";
import PacienteCell from '@/components/common/PacienteCell.vue'

defineProps<{
  agendamentos: Agendamento[]
}>()

const emit = defineEmits<{
  (e: 'abrir-detalhes', agendamento: Agendamento): void
  (e: 'abrir-prescricao', agendamento: Agendamento): void
  (e: 'abrir-tags', agendamento: any): void
  (e: 'abrir-remarcar', agendamento: Agendamento): void
  (e: 'alterar-checkin', agendamento: Agendamento, checkin: boolean): void
  (e: 'alterar-status', agendamento: Agendamento, novoStatus: string): void
}>()

const statusPermitidosSemCheckin = [
  'agendado',
  'aguardando-consulta',
  'aguardando-exame',
  'aguardando-medicamento',
  'internado',
  'suspenso',
  'remarcado'
]

const router = useRouter()
const appStore = useAppStore()

const getPaciente = (id: string) => appStore.getPacienteById(id)

const irParaProntuario = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const handleAlterarStatusPaciente = (agendamento: Agendamento, event: Event) => {
  const select = event.target as HTMLSelectElement
  const novoStatus = select.value
  const statusAntigo = agendamento.status
  if (novoStatus === 'remarcado') {
    emit('abrir-remarcar', agendamento)
    select.value = statusAntigo
  } else {
    emit('alterar-status', agendamento, novoStatus)
  }
  select.value = statusAntigo
}

const opcoesStatusPaciente = computed(() => {
  return appStore.statusConfig.filter(s => s.tipo === 'paciente')
})

const getOpcoesStatus = (ag: Agendamento) => {
  if (ag.checkin) {
    return opcoesStatusPaciente.value
  }
  return opcoesStatusPaciente.value.filter(op => statusPermitidosSemCheckin.includes(op.id))
}

const getStatusDotColor = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config.cor.split(' ')[0]
}

const getAgendamentoInfo = (ag: Agendamento) => {
  const duracaoMin = getDuracaoAgendamento(ag)
  const grupo = getGrupoInfusao(duracaoMin)
  return {
    duracaoTexto: formatarDuracao(duracaoMin),
    corBorda: getCorGrupo(grupo),
    corBadge: getBadgeGrupo(grupo),
    grupoLabel: grupo === 'rapido' ? 'Rápida' : grupo === 'medio' ? 'Média' : 'Longa'
  }
}

const getObservacoesClinicas = (ag: Agendamento) => {
  return ag.paciente?.observacoesClinicas || getPaciente(ag.pacienteId)?.observacoesClinicas
}
</script>

<template>
  <div class="rounded-md border">
    <Table>
      <TableHeader>
        <TableRow class="hover:bg-transparent">
          <TableHead class="pl-5 w-[100px]">Horário</TableHead>
          <TableHead class="min-w-[150px]">Paciente</TableHead>
          <TableHead class="min-w-[100px]">Prescrição</TableHead>
          <TableHead class="w-[80px] text-center">Check-in</TableHead>
          <TableHead class="min-w-[240px]">Status Paciente</TableHead>
          <TableHead class="min-w-[140px]">Status Farmácia</TableHead>
          <TableHead class="w-fit">Tags</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-if="agendamentos.length === 0">
          <TableCell class="text-center py-12 text-gray-500" colspan="9">
            Nenhum agendamento corresponde aos filtros.
          </TableCell>
        </TableRow>

        <TableRow
            v-for="ag in agendamentos"
            v-else
            :key="ag.id"
            :class="{ 'bg-gray-50 opacity-60 grayscale': ag.status === 'remarcado' }"
        >
          <TableCell class="p-0 relative">
            <div :class="['h-full w-[4px] absolute left-0 top-0 bottom-0', getAgendamentoInfo(ag).corBorda]"></div>
            <div class="px-4 pl-5">
              <button
                  class="text-md hover:text-blue-600 hover:underline"
                  @click="emit('abrir-detalhes', ag)"
              >
                {{ ag.horarioInicio }}
              </button>
              <div class="flex items-center gap-1.5 mt-1">
                <Clock class="h-3 w-3 text-gray-400"/>
                <span class="text-xs font-medium text-gray-500">
                  {{ getAgendamentoInfo(ag).duracaoTexto }}
                </span>
              </div>
            </div>
          </TableCell>

          <TableCell>
            <PacienteCell
                :nome="(ag.paciente?.nome || getPaciente(ag.pacienteId)?.nome) as string"
                :observacoesClinicas="getObservacoesClinicas(ag)"
                :paciente-id="ag.pacienteId"
                :registro="ag.paciente?.registro || getPaciente(ag.pacienteId)?.registro"
                @click="irParaProntuario"
            />
          </TableCell>

          <TableCell class="align-top">
            <div class="flex flex-col truncate">
              <button
                  :title="ag.prescricao?.conteudo?.protocolo?.nome || '-'"
                  class="font-medium text-gray-700 block hover:text-blue-600 hover:underline text-left truncate"
                  @click.stop="emit('abrir-prescricao', ag)"
              >
                {{ ag.prescricao?.conteudo?.protocolo?.nome || '-' }}
              </button>

              <div class="flex items-center gap-2 mt-1 text-xs text-gray-800">
                <template v-if="isInfusao(ag)">
                    <span v-if="ag.detalhes.infusao.cicloAtual"
                          class="bg-blue-50 text-blue-700 px-1.5 rounded border border-blue-100">
                        Ciclo {{ ag.detalhes.infusao.cicloAtual }}
                    </span>
                  <span v-if="ag.detalhes.infusao.diaCiclo" class="text-gray-800 px-1.5 rounded border">
                        Dia {{ ag.detalhes.infusao.diaCiclo }}
                    </span>
                </template>
              </div>
            </div>
          </TableCell>

          <TableCell class="text-center p-0 align-midle">
            <div class="flex items-center justify-center">
              <Checkbox
                  :checked="ag.checkin"
                  :disabled="ag.status === 'remarcado'"
                  @update:checked="(val) => emit('alterar-checkin', ag, val as boolean)"
              />
            </div>
          </TableCell>

          <TableCell>
            <div class="flex items-center gap-2">
              <div :class="['h-2.5 w-2.5 rounded-full flex-shrink-0', getStatusDotColor(ag.status)]"/>

              <div class="relative w-full">
                <select
                    :disabled="ag.status === 'remarcado'"
                    :value="ag.status"
                    class="flex h-8 w-full items-center justify-between rounded-md border border-input bg-background
                         px-3 py-1 pr-8 text-sm ring-offset-background placeholder:text-muted-foreground
                         focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2
                         disabled:cursor-not-allowed disabled:opacity-50 appearance-none truncate"
                    @change="(e) => handleAlterarStatusPaciente(ag, e)"
                >
                  <option
                      v-for="opcao in getOpcoesStatus(ag)"
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

          <TableCell class="align-top">
            <div class="flex flex-col gap-1">
              <Badge
                  :class="{
                    'bg-green-100 text-green-800 border-green-200': isInfusao(ag) && ag.detalhes.infusao.statusFarmacia === 'pronta',
                    'bg-yellow-100 text-yellow-800 border-yellow-200': isInfusao(ag) && ag.detalhes.infusao.statusFarmacia === 'pendente',
                    'bg-blue-100 text-blue-800 border-blue-200': isInfusao(ag) && ag.detalhes.infusao.statusFarmacia === 'em-preparacao',
                    'bg-purple-100 text-purple-800 border-purple-200': isInfusao(ag) && ag.detalhes.infusao.statusFarmacia === 'enviada'
                  }"
                  class="w-fit font-semibold px-2 border"
                  variant="secondary"
              >
                {{
                  isInfusao(ag) && ag.detalhes.infusao.statusFarmacia ?
                      ag.detalhes.infusao.statusFarmacia.toUpperCase().replace('-', ' ') : 'PENDENTE'
                }}
              </Badge>

              <div class="pl-1 flex items-center gap-1.5 text-xs">
                <Clock class="h-3.5 w-3.5 text-gray-400"/>
                <span v-if="isInfusao(ag) && ag.detalhes.infusao.horarioPrevisaoEntrega"
                      class="text-blue-600 font-medium">
                    {{ ag.detalhes.infusao.horarioPrevisaoEntrega }}
                </span>
                <span v-else class="text-gray-400 italic">
                  --:--
                </span>
              </div>
            </div>
          </TableCell>

          <TableCell class="pr-4">
            <div class="flex items-center justify-center w-full">
              <TooltipProvider>
                <Tooltip :delay-duration="300">
                  <TooltipTrigger as-child>
                    <Button
                        class="h-7 w-7 rounded-full p-0 relative"
                        size="icon"
                        variant="ghost"
                        @click="$emit('abrir-tags', ag)"
                    >
                      <Tag
                          :class="(ag.tags && ag.tags.length > 0) ? 'text-blue-600' : 'text-gray-300'"
                          class="transition-colors"
                      />

                      <span
                          v-if="ag.tags && ag.tags.length > 0"
                          class="absolute -top-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-blue-600 text-[9px] font-bold text-white ring-2 ring-white"
                      >
                          {{ ag.tags.length }}
                        </span>
                    </Button>
                  </TooltipTrigger>

                  <TooltipContent v-if="ag.tags && ag.tags.length > 0">
                    <div class="flex flex-col gap-1">
                      <p class="font-semibold text-xs border-b pb-1 mb-1">Tags</p>
                      <ul class="list-disc pl-3">
                        <li v-for="t in ag.tags" :key="t" class="text-xs">{{ t }}</li>
                      </ul>
                    </div>
                  </TooltipContent>
                  <TooltipContent v-else>
                    <p class="text-xs">Nenhuma tag</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>
