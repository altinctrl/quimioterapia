<script lang="ts" setup>
import {AlertTriangle} from 'lucide-vue-next'
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip'

defineProps<{
  nome: string
  registro?: string
  pacienteId: string
  observacoesClinicas?: string
}>()

const emit = defineEmits<{
  (e: 'click', pacienteId: string): void
}>()
</script>

<template>
  <div class="flex-col items-center gap-1.5">
    <div class="flex items-center gap-1.5 max-w-[200px]">
      <button
          class="text-left font-medium hover:text-blue-600 hover:underline truncate max-w-[180px] text-gray-900"
          @click="emit('click', pacienteId)"
      >
        {{ nome || 'Paciente não identificado' }}
      </button>

      <TooltipProvider v-if="observacoesClinicas">
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
            <p class="text-sm leading-relaxed">{{ observacoesClinicas }}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
    <div v-if="registro" class="text-xs text-gray-500">{{ registro }}</div>
  </div>
</template>
