<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'

const props = defineProps<{
  horario: string
  diaCiclo: string
  observacoes: string
  ultimoAgendamento: any
  horarioAbertura: string
  horarioFechamento: string
}>()

const emit = defineEmits<{
  (e: 'update:horario', value: string): void
  (e: 'update:diaCiclo', value: string): void
  (e: 'update:observacoes', value: string): void
  (e: 'confirmar'): void
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Detalhes</CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">

      <div>
        <Label>Horário</Label>
        <Input :model-value="horario" type="time" @update:model-value="(val) => emit('update:horario', String(val))"/>
        <p class="text-xs text-gray-500 mt-1">
          Funcionamento: {{ horarioAbertura }} às {{ horarioFechamento }}
        </p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <Label>Ciclo Atual</Label>
          <Input :model-value="ultimoAgendamento?.cicloAtual ? ultimoAgendamento.cicloAtual + 1 : 1"
                 class="bg-gray-50"
                 readonly type="number"/>
        </div>
        <div>
          <Label>Dia do Ciclo</Label>
          <Input :model-value="diaCiclo" @update:model-value="(val) => emit('update:diaCiclo', String(val))"/>
        </div>
      </div>

      <div>
        <Label>Observações</Label>
        <Textarea :model-value="observacoes"
                  @update:model-value="(val) => emit('update:observacoes', String(val))"/>
      </div>
      <Button class="w-full" @click="emit('confirmar')">Confirmar Agendamento</Button>
    </CardContent>
  </Card>
</template>