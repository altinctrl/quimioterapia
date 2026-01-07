<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Label} from '@/components/ui/label'
import {isInfusao, type Paciente} from '@/types'

defineProps<{
  paciente: Paciente
  protocolo: any
  ultimoAgendamento: any
}>()
</script>

<template>
  <Card class="bg-blue-50 border-blue-200">
    <CardHeader>
      <CardTitle>Resumo do Paciente</CardTitle>
    </CardHeader>
    <CardContent class="space-y-3">
      <div>
        <p class="font-medium text-lg">{{ paciente.nome }}</p>
        <p class="text-sm text-gray-600">Reg: {{ paciente.registro }}</p>
      </div>

      <div v-if="protocolo" class="pt-3 border-t border-blue-200">
        <Label class="text-xs text-gray-500">Protocolo</Label>
        <p class="font-medium">{{ protocolo.nome }}</p>
        <p class="text-sm text-gray-600">{{ protocolo.duracao }} min • Grupo {{ protocolo.grupoInfusao }}</p>
      </div>

      <div v-if="ultimoAgendamento" class="pt-3 border-t border-blue-200 bg-white/50 p-3 rounded">
        <Label class="text-xs text-gray-500">Último Agendamento</Label>
        <p class="text-sm font-medium">{{ new Date(ultimoAgendamento.data).toLocaleDateString('pt-BR') }}</p>
        <p v-if="isInfusao(ultimoAgendamento)" class="text-sm text-gray-600">
          Ciclo {{ ultimoAgendamento.detalhes.infusao.ciclo_atual || '?' }} -
          {{ ultimoAgendamento.detalhes.infusao.dia_ciclo || '?' }}</p>
        <p v-else class="text-gray-400 italic">Não informado</p>
      </div>
      <div v-else class="pt-3 border-t border-blue-200">
        <p class="text-sm text-gray-500 italic">Primeiro agendamento</p>
      </div>
    </CardContent>
  </Card>
</template>