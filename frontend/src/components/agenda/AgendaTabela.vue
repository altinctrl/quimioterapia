<script lang="ts" setup>
import {computed} from 'vue'
import {useRouter} from 'vue-router'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {Button} from '@/components/ui/button'
import {ChevronDown, Clock, Tag, Pill} from 'lucide-vue-next'
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip'
import {Agendamento, TipoAgendamento} from "@/types/typesAgendamento.ts";
import {
  formatarConsulta,
  formatarProcedimento,
  getAgendamentoInfo,
  getFarmaciaStatusConfig,
  getObservacoesClinicas,
  getOpcoesStatus,
  getStatusDotColor
} from '@/utils/utilsAgenda.ts'
import {Checkbox} from "@/components/ui/checkbox";
import PacienteCelula from '@/components/comuns/PacienteCelula.vue'

const props = defineProps<{
  agendamentos: Agendamento[]
  tipo: TipoAgendamento
  selectedIds: string[]
}>()

const emit = defineEmits<{
  (e: 'abrir-detalhes', agendamento: Agendamento): void
  (e: 'abrir-prescricao', agendamento: Agendamento): void
  (e: 'abrir-tags', agendamento: any): void
  (e: 'abrir-remarcar', agendamento: Agendamento): void
  (e: 'alterar-checkin', agendamento: Agendamento, checkin: boolean): void
  (e: 'alterar-status', agendamento: Agendamento, novoStatus: string): void
  (e: 'update:selectedIds', value: string[]): void
}>()

const router = useRouter()

const selectedSet = computed(() => new Set(props.selectedIds))

const areAllSelected = computed(() => {
  return props.agendamentos.length > 0 && props.agendamentos.every(ag => selectedSet.value.has(ag.id))
})

const toggleAll = (checked: boolean) => {
  if (!checked) {
    emit('update:selectedIds', [])
    return
  }
  emit('update:selectedIds', props.agendamentos.map(a => a.id))
}

const toggleSelect = (id: string, checked: boolean) => {
  const next = new Set(props.selectedIds)
  if (checked) next.add(id)
  else next.delete(id)
  emit('update:selectedIds', [...next])
}

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

const getChecklistLabel = (agendamento: Agendamento) => {
  if (agendamento.tipo !== 'infusao') return ''
  const infoInfusao = agendamento.detalhes?.infusao
  if (!infoInfusao) return ''

  const itensPreparados = new Set(infoInfusao.itensPreparados || [])
  const diaCicloAtual = infoInfusao.diaCiclo || 1
  const prescricao = agendamento.prescricao

  let totalMeds = 0
  let totalChecked = 0

  if (prescricao?.conteudo?.blocos?.length) {
    prescricao.conteudo.blocos.forEach(bloco => {
      bloco.itens.forEach(item => {
        if (item.diasDoCiclo.includes(diaCicloAtual)) {
          totalMeds += 1
          const key = item.idItem || `${bloco.ordem}-${item.medicamento}`
          if (itensPreparados.has(key)) totalChecked += 1
        }
      })
    })
  }

  if (totalMeds === 0) return ''
  return `${totalChecked}/${totalMeds}`
}

</script>

<template>
  <div class="rounded-md border">
    <Table>
      <TableHeader>
        <TableRow class="hover:bg-transparent">
          <TableHead class="w-[40px] text-center">
            <div class="flex items-center justify-center">
              <Checkbox
                  :checked="areAllSelected"
                  @update:checked="(val) => toggleAll(val as boolean)"
              />
            </div>
          </TableHead>
          <TableHead class="pl-5 w-[100px]">Horário</TableHead>
          <TableHead class="min-w-[150px]">Paciente</TableHead>
          <TableHead class="min-w-[100px]">
            {{ tipo == 'infusao' ? 'Prescrição' : tipo == 'consulta' ? 'Consulta' : 'Procedimento'}}
          </TableHead>
          <TableHead class="w-[80px] text-center">Em Sala</TableHead>
          <TableHead class="min-w-[240px]">Status Paciente</TableHead>
          <TableHead v-if="tipo == 'infusao'" class="min-w-[140px]">Status Farmácia</TableHead>
          <TableHead class="w-fit">Tags</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-if="agendamentos.length === 0">
          <TableCell
              class="text-center py-12 text-gray-500"
              :colspan="tipo == 'infusao' ? 8 : 7"
          >
            Nenhum agendamento corresponde aos filtros.
          </TableCell>
        </TableRow>

        <TableRow
            v-for="ag in agendamentos"
            v-else
            :key="ag.id"
            :class="{ 'bg-gray-50 opacity-60 grayscale': ag.status === 'remarcado' }"
        >
          <TableCell class="text-center p-0 pl-2 align-middle relative">
            <div v-if="tipo == 'infusao'" :class="['h-full w-[4px] absolute left-0 top-0 bottom-0', getAgendamentoInfo(ag).corBorda]"></div>
            <div class="flex items-center justify-center">
              <Checkbox
                  :checked="selectedSet.has(ag.id)"
                  @update:checked="(val) => toggleSelect(ag.id, val as boolean)"
              />
            </div>
          </TableCell>
          <TableCell class="p-0">
            <div class="px-4 pl-5">
              <button
                  class="text-md hover:text-blue-600 hover:underline"
                  @click="emit('abrir-detalhes', ag)"
              >
                {{ ag.horarioInicio }}
              </button>
              <div v-if="tipo == 'infusao'" class="flex items-center gap-1.5 mt-1">
                <Clock class="h-3 w-3 text-gray-400"/>
                <span class="text-xs font-medium text-gray-500">
                  {{ getAgendamentoInfo(ag).duracaoTexto }}
                </span>
              </div>
            </div>
          </TableCell>

          <TableCell class="py-0">
            <PacienteCelula
                :nome="(ag.paciente?.nome) as string"
                :observacoesClinicas="getObservacoesClinicas(ag)"
                :paciente-id="ag.pacienteId"
                :registro="ag.paciente?.registro"
                @click="irParaProntuario"
            />
          </TableCell>

          <TableCell class="align-center py-0">
            <div v-if="tipo == 'infusao'" class="flex flex-col truncate">
              <button
                  :title="ag.prescricao?.conteudo?.protocolo?.nome || '-'"
                  class="font-medium text-gray-700 block hover:text-blue-600 hover:underline text-left truncate"
                  @click.stop="emit('abrir-prescricao', ag)"
              >
                {{ ag.prescricao?.conteudo?.protocolo?.nome || '-' }}
              </button>

              <div class="flex items-center gap-2 mt-1 text-xs text-gray-800">
                <template>
                    <span v-if="ag.detalhes?.infusao?.cicloAtual"
                          class="bg-blue-50 text-blue-700 px-1.5 rounded border border-blue-100">
                        Ciclo {{ ag.detalhes.infusao.cicloAtual }}
                    </span>
                    <span v-if="ag.detalhes?.infusao?.diaCiclo" class="text-gray-800 px-1.5 rounded border">
                        Dia {{ ag.detalhes.infusao.diaCiclo }}
                    </span>
                </template>
              </div>
            </div>
            <div v-else-if="tipo == 'consulta'">
              {{ formatarConsulta(ag.detalhes?.consulta?.tipoConsulta) }}
            </div>
            <div v-else-if="tipo == 'procedimento'">
              {{ formatarProcedimento(ag.detalhes?.procedimento?.tipoProcedimento) }}
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

          <TableCell class="py-0">
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

          <TableCell v-if="tipo=='infusao'" class="align-top py-1.5">
            <div class="flex flex-col gap-0.5">
              <Badge
                  :class="[getFarmaciaStatusConfig(ag.detalhes?.infusao?.statusFarmacia).corBadge]"
                  class="w-fit font-semibold px-2 border uppercase hover:bg-opacity-100"
                  variant="secondary"
              >
                {{ getFarmaciaStatusConfig(ag.detalhes?.infusao?.statusFarmacia).label }}
              </Badge>

              <div class="flex items-center gap-1 text-xs">
                <Pill class="h-3 w-3 text-gray-400"/>
                <span
                    v-if="getChecklistLabel(ag)"
                    class="font-medium text-gray-700 pr-1"
                >
                  {{ getChecklistLabel(ag) }}
                </span>
                <Clock class="h-3.5 w-3.5 text-gray-400"/>
                <span v-if="ag.detalhes?.infusao?.horarioPrevisaoEntrega" class="text-gray-700 font-medium">
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
