<script lang="ts" setup>
import {computed} from 'vue'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {Button} from '@/components/ui/button'
import {Checkbox} from '@/components/ui/checkbox'
import {AlertTriangle, ChevronDown, ChevronRight, Clock} from 'lucide-vue-next'
import type {StatusFarmacia} from '@/types'
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from "@/components/ui/tooltip";

export interface FarmaciaTableRow {
  id: string
  pacienteId: string
  horario: string
  pacienteNome: string
  pacienteRegistro: string
  observacoesClinicas: string | undefined
  protocoloNome: string
  statusTexto: string
  statusBloqueado: boolean
  statusFarmacia: StatusFarmacia
  statusFarmaciaCor: string
  previsaoEntrega: string
  medicamentos: Array<{
    key: string
    nome: string
    dose: string
    unidade: string
    checked: boolean
  }>
  checklistLabel: string
  hasMedicamentos: boolean
}

const props = defineProps<{
  rows: FarmaciaTableRow[]
  expandedIds: string[]
  opcoesStatus: { id: string, label: string }[]
}>()

const emit = defineEmits<{
  (e: 'alterarStatus', id: string, novoStatus: StatusFarmacia): void
  (e: 'alterarHorario', id: string, novoHorario: string): void
  (e: 'update:expandedIds', value: string[]): void
  (e: 'clickPaciente', pacienteId: string): void
  (e: 'toggleCheckItem', id: string, itemKey: string, statusAtual: StatusFarmacia): void
}>()

const expandedSet = computed(() => new Set(props.expandedIds))

const toggleExpand = (id: string) => {
  const next = new Set(props.expandedIds)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  emit('update:expandedIds', [...next])
}

const onStatusChange = (id: string, event: Event) => {
  const val = (event.target as HTMLSelectElement).value as StatusFarmacia
  emit('alterarStatus', id, val)
}
</script>

<template>
  <div>
    <Table>
      <TableHeader>
        <TableRow class="hover:bg-transparent">
          <TableHead class="w-[50px]"></TableHead>
          <TableHead class="w-[100px]">Horário</TableHead>
          <TableHead class="min-w-[150px]">Paciente</TableHead>
          <TableHead class="min-w-[100px]">Protocolo</TableHead>
          <TableHead class="w-[140px]">Status Paciente</TableHead>
          <TableHead class="w-[220px]">Status Farmácia</TableHead>
          <TableHead class="w-[140px]">Previsão</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-if="rows.length === 0">
          <TableCell class="text-center py-12 text-gray-500" colspan="7">
            Nenhuma preparação corresponde aos filtros.
          </TableCell>
        </TableRow>
        <template v-for="row in rows" :key="row.id">
          <TableRow
              :class="{'bg-gray-50 opacity-75': row.statusBloqueado}"
              class="group transition-colors hover:bg-gray-50/50"
          >
            <TableCell class="p-2 text-center">
              <Button
                  class="h-8 w-8 text-gray-400 hover:text-gray-900"
                  size="icon"
                  variant="ghost"
                  @click="toggleExpand(row.id)"
              >
                <ChevronDown v-if="expandedSet.has(row.id)" class="h-4 w-4"/>
                <ChevronRight v-else class="h-4 w-4"/>
              </Button>
            </TableCell>

            <TableCell>
              <div class="text-md">{{ row.horario }}</div>
              <div v-if="row.checklistLabel" class="text-xs font-medium text-gray-500">
                Checklist: {{ row.checklistLabel }}
              </div>
            </TableCell>

            <TableCell>
              <div class="flex items-center gap-1.5">
                <button
                    class="text-left font-medium hover:text-blue-600 hover:underline truncate max-w-[180px] text-gray-900"
                    @click="emit('clickPaciente', row.pacienteId)"
                >
                  {{ row.pacienteNome }}
                </button>
                <TooltipProvider v-if="row.observacoesClinicas">
                  <Tooltip :delay-duration="200">
                    <TooltipTrigger as-child>
                      <div class="cursor-help flex-shrink-0">
                        <AlertTriangle class="h-4 w-4 text-amber-500 hover:text-amber-600 transition-colors"/>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent
                        class="max-w-[300px] p-3 bg-amber-50 border border-amber-200 text-black"
                        side="right"
                    >
                      <p class="font-semibold text-xs mb-1 uppercase tracking-wide">Observações Clínicas</p>
                      <p class="text-sm leading-relaxed">
                        {{ row.observacoesClinicas }}
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <div class="text-xs text-gray-500">{{ row.pacienteRegistro }}</div>
            </TableCell>

            <TableCell>
              <span
                  :title="row.protocoloNome"
                  class="text-sm font-medium text-gray-700 block whitespace-normal break-words"
              >
                {{ row.protocoloNome }}
              </span>
            </TableCell>

            <TableCell>
              <Badge :variant="row.statusBloqueado ? 'destructive' : 'outline'"
                     class="font-normal capitalize">
                {{ row.statusTexto }}
              </Badge>
            </TableCell>

            <TableCell>
              <div class="flex items-center gap-2">
                <div
                    :class="[
                    'h-2.5 w-2.5 rounded-full flex-shrink-0 shadow-sm transition-colors',
                    row.statusFarmaciaCor
                  ]"
                />
                <div class="relative w-full max-w-[150px]">
                  <select
                      :disabled="row.statusBloqueado"
                      :value="row.statusFarmacia"
                      class="flex h-8 w-full items-center justify-between rounded-md border border-input bg-transparent
                      px-2 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none
                      focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50
                      appearance-none truncate font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                      @change="(e) => onStatusChange(row.id, e)"
                  >
                    <option
                        v-for="opcao in opcoesStatus"
                        :key="opcao.id"
                        :value="opcao.id"
                    >
                      {{ opcao.label }}
                    </option>
                  </select>
                  <ChevronDown class="absolute right-2 top-2.5 h-3 w-3 opacity-50 pointer-events-none"/>
                </div>
              </div>
            </TableCell>

            <TableCell>
              <div class="flex items-center gap-1.5">
                <Clock class="h-3.5 w-3.5 text-gray-400"/>
                <input
                    :disabled="row.statusBloqueado"
                    :value="row.previsaoEntrega"
                    class="w-24 h-8 text-sm bg-transparent border-b border-transparent hover:border-gray-300
                    focus:border-primary focus:outline-none transition-colors"
                    type="time"
                    @input="(e) => emit('alterarHorario', row.id, (e.target as HTMLInputElement).value)"
                />
              </div>
            </TableCell>
          </TableRow>

          <TableRow
              v-if="expandedSet.has(row.id)"
              :class="{'bg-gray-50 opacity-75': row.statusBloqueado}"
              class="bg-gray-50/80 border-t-0 shadow-inner"
          >
            <TableCell class="p-0" colspan="3"></TableCell>
            <TableCell class="p-0" colspan="1">
              <div class="pt-4 pb-4 animate-in slide-in-from-top-1 duration-200">
                <div
                    v-if="!row.hasMedicamentos"
                    class="text-muted-foreground text-sm">
                  Nenhuma medicação encontrada para este agendamento.
                </div>

                <template v-else>
                  <div class="space-y-2">
                    <div
                        v-for="med in row.medicamentos"
                        :key="med.key"
                        class="flex items-start gap-2 bg-white p-2 rounded border border-gray-100 shadow-sm">
                      <Checkbox
                          :id="`qt-${row.id}-${med.key}`"
                          :checked="med.checked"
                          :disabled="row.statusBloqueado"
                          class="mt-0.5"
                          @update:checked="() => emit('toggleCheckItem', row.id, med.key, row.statusFarmacia)"
                      />
                      <label
                          :for="`qt-${row.id}-${med.key}`"
                          class="text-sm leading-tight font-semibold block cursor-pointer w-full"
                      >
                        {{ med.nome }} - {{ med.dose }} {{ med.unidade }}
                      </label>
                    </div>
                  </div>
                </template>
              </div>
            </TableCell>
            <TableCell class="p-0" colspan="3"></TableCell>
          </TableRow>
        </template>
      </TableBody>
    </Table>
  </div>
</template>
