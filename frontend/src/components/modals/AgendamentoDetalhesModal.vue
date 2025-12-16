<script lang="ts" setup>
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {AlertCircle, Calendar, Clock, FileText, Tag} from 'lucide-vue-next'
import type {Agendamento} from '@/types'

defineProps<{
  open: boolean
  agendamento: Agendamento | null
  pacienteNome?: string
}>()

const emit = defineEmits(['update:open'])

const formatarData = (data: string) => {
  return new Date(data).toLocaleDateString('pt-BR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-2xl">
      <DialogHeader>
        <DialogTitle>Detalhes do Agendamento</DialogTitle>
        <DialogDescription v-if="pacienteNome">Paciente: {{ pacienteNome }}</DialogDescription>
      </DialogHeader>

      <div v-if="agendamento" class="space-y-6">
        <div class="flex flex-wrap gap-2">
          <Badge class="text-sm px-3 py-1 capitalize" variant="outline">
            {{ agendamento.status.replace('-', ' ') }}
          </Badge>
          <Badge v-if="agendamento.encaixe" class="text-sm px-3 py-1" variant="destructive">
            Encaixe
          </Badge>
          <Badge v-if="agendamento.statusFarmacia" class="text-sm px-3 py-1 capitalize" variant="secondary">
            Farmácia: {{ agendamento.statusFarmacia.replace('-', ' ') }}
          </Badge>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <Calendar class="h-5 w-5 text-gray-500 mt-0.5"/>
              <div>
                <p class="text-sm text-gray-500 font-medium">Data</p>
                <p class="text-gray-900 font-medium capitalize">{{ formatarData(agendamento.data) }}</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <Clock class="h-5 w-5 text-gray-500 mt-0.5"/>
              <div>
                <p class="text-sm text-gray-500 font-medium">Horário</p>
                <p class="text-gray-900">{{ agendamento.horarioInicio }} - {{ agendamento.horarioFim }}</p>
                <p class="text-xs text-gray-500 capitalize">Turno: {{ agendamento.turno }}</p>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <FileText class="h-5 w-5 text-gray-500 mt-0.5"/>
              <div>
                <p class="text-sm text-gray-500 font-medium">Ciclo / Dia</p>
                <p v-if="agendamento.cicloAtual || agendamento.diaCiclo" class="text-gray-900">
                  {{ agendamento.cicloAtual ? `Ciclo ${agendamento.cicloAtual}` : '' }}
                  {{ agendamento.diaCiclo ? ` - ${agendamento.diaCiclo}` : '' }}
                </p>
                <p v-else class="text-gray-400 italic">Não informado</p>
              </div>
            </div>

            <div v-if="agendamento.horarioPrevisaoEntrega" class="flex items-start gap-3">
              <Clock class="h-5 w-5 text-blue-600 mt-0.5"/>
              <div>
                <p class="text-sm text-blue-600 font-medium">Previsão Farmácia</p>
                <p class="text-blue-900 font-bold">{{ agendamento.horarioPrevisaoEntrega }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="agendamento.tags && agendamento.tags.length > 0">
          <p class="text-sm text-gray-500 font-medium mb-2 flex items-center gap-2">
            <Tag class="h-4 w-4"/>
            Tags de Observação
          </p>
          <div class="flex flex-wrap gap-2">
            <Badge v-for="tag in agendamento.tags" :key="tag" variant="outline">{{ tag }}</Badge>
          </div>
        </div>

        <div v-if="agendamento.observacoes">
          <p class="text-sm text-gray-500 font-medium mb-2 flex items-center gap-2">
            <AlertCircle class="h-4 w-4"/>
            Observações
          </p>
          <div class="bg-gray-50 p-3 rounded-md text-sm text-gray-700 whitespace-pre-wrap border">
            {{ agendamento.observacoes }}
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="emit('update:open', false)">Fechar</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
