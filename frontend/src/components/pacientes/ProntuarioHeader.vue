<script lang="ts" setup>
import { CardHeader, CardTitle } from '@/components/ui/card'
import { Activity } from 'lucide-vue-next'
import {Paciente} from "@/types/pacienteTypes.ts";

defineProps<{
  paciente: Paciente
  protocoloNome?: string
  cicloAtual?: string | number
  diaCiclo?: string | number
}>()
</script>

<template>
  <CardHeader>
    <div class="flex flex-col gap-4">
      <div>
        <CardTitle class="text-2xl">{{ paciente.nome }}</CardTitle>
        <div class="flex items-center gap-4 mt-2 text-sm text-gray-600">
          <span><span class="font-medium text-gray-900">Prontuário:</span> {{ paciente.registro }}</span>
          <span><span class="font-medium text-gray-900">CPF:</span> {{ paciente.cpf }}</span>
        </div>
      </div>

      <div class="bg-blue-50 border border-blue-100 rounded-lg p-4 flex flex-wrap gap-6 items-center">
        <div class="flex items-center gap-2">
          <Activity class="h-5 w-5 text-blue-600" />
          <span class="text-sm font-medium text-blue-900">Status Atual do Tratamento</span>
        </div>
        <div class="h-8 w-px bg-blue-200 hidden sm:block"></div>

        <div>
          <p class="text-xs text-blue-700 uppercase tracking-wide">Protocolo</p>
          <p class="font-medium text-blue-950">{{ protocoloNome || 'Nenhum definido' }}</p>
        </div>

        <div>
          <p class="text-xs text-blue-700 uppercase tracking-wide">Ciclo Atual</p>
          <p class="font-medium text-blue-950">{{ cicloAtual || '-' }}</p>
        </div>

        <div>
          <p class="text-xs text-blue-700 uppercase tracking-wide">Dia do Ciclo</p>
          <p class="font-medium text-blue-950">{{ diaCiclo || '-' }}</p>
        </div>
      </div>
    </div>
  </CardHeader>
</template>