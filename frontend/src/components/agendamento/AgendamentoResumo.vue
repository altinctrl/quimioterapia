<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Label} from '@/components/ui/label'
import {type Paciente} from '@/types'

defineProps<{
  paciente: Paciente
  ultimoAgendamento: any
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Paciente</CardTitle>
    </CardHeader>
    <CardContent class="space-y-3">
      <div>
        <p class="font-medium text-lg">{{ paciente.nome }}</p>
        <p class="text-sm text-gray-600">Registro: {{ paciente.registro }}</p>
      </div>

      <div v-if="ultimoAgendamento" class="pt-3 border-t">
        <Label class="text-sm text-bold text-gray-600">Último Agendamento</Label>
        <p class="text-sm font-medium">{{ new Date(ultimoAgendamento.data).toLocaleDateString('pt-BR') }}</p>
        <p v-if="ultimoAgendamento.prescricao" class="text-sm text-gray-600">
          {{ ultimoAgendamento.prescricao.conteudo.protocolo.nome || '?' }} <br>
          Ciclo {{ ultimoAgendamento.detalhes.infusao.cicloAtual || '?' }} -
          Dia {{ ultimoAgendamento.detalhes.infusao.diaCiclo || '?' }}</p>
        <p v-else class="text-gray-400 italic text-sm capitalize">{{ ultimoAgendamento.tipo }}</p>
      </div>
      <div v-else class="pt-3 border-t">
        <p class="text-sm text-gray-500 italic">Primeiro agendamento</p>
      </div>
    </CardContent>
  </Card>
</template>
