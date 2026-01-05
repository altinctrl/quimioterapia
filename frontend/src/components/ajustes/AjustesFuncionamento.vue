<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Checkbox} from '@/components/ui/checkbox'
import {Calendar as CalendarIcon} from 'lucide-vue-next'

const props = defineProps<{
  horarioAbertura: string
  horarioFechamento: string
  diasSelecionados: number[]
}>()

const emit = defineEmits<{
  (e: 'update:horarioAbertura', value: string): void
  (e: 'update:horarioFechamento', value: string): void
  (e: 'update:diasSelecionados', value: number[]): void
}>()

const diasSemana = [
  {value: 0, label: 'Domingo'},
  {value: 1, label: 'Segunda'},
  {value: 2, label: 'Terça'},
  {value: 3, label: 'Quarta'},
  {value: 4, label: 'Quinta'},
  {value: 5, label: 'Sexta'},
  {value: 6, label: 'Sábado'}
]

const toggleDia = (dia: number) => {
  let novoArray = [...props.diasSelecionados]
  if (novoArray.includes(dia)) {
    novoArray = novoArray.filter(d => d !== dia)
  } else {
    novoArray = [...novoArray, dia].sort((a, b) => a - b)
  }
  emit('update:diasSelecionados', novoArray)
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-gray-800">
        <CalendarIcon class="h-5 w-5 text-gray-500"/>
        Funcionamento da Clínica
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-gray-50 p-4 rounded-lg border">
          <Label class="text-base text-gray-700 mb-2 block">Horário de Atendimento</Label>
          <div class="flex gap-4 items-center">
            <div class="flex-1">
              <span class="text-xs text-gray-500 uppercase font-bold">Abertura</span>
              <Input
                  :model-value="horarioAbertura"
                  class="mt-1 bg-white"
                  type="time"
                  @update:model-value="(val) => emit('update:horarioAbertura', String(val))"
              />
            </div>
            <div class="flex-1">
              <span class="text-xs text-gray-500 uppercase font-bold">Fechamento</span>
              <Input
                  :model-value="horarioFechamento"
                  class="mt-1 bg-white"
                  type="time"
                  @update:model-value="(val) => emit('update:horarioFechamento', String(val))"
              />
            </div>
          </div>
        </div>

        <div>
          <Label class="text-base text-gray-700 mb-3 block">Dias da Semana</Label>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div v-for="dia in diasSemana" :key="dia.value"
                 :class="[
                  'flex items-center space-x-2 border p-2 rounded-md transition-colors',
                  diasSelecionados.includes(dia.value) ? 'bg-blue-50 border-blue-200' : 'bg-white hover:bg-gray-50'
                ]"
            >
              <Checkbox
                  :id="`dia-${dia.value}`"
                  :checked="diasSelecionados.includes(dia.value)"
                  @update:checked="toggleDia(dia.value)"
              />
              <Label :for="`dia-${dia.value}`" class="cursor-pointer font-normal text-sm w-full py-1">
                {{ dia.label }}
              </Label>
            </div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>