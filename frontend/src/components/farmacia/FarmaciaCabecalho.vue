<script lang="ts" setup>
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {ChevronLeft, ChevronRight, Eye, EyeOff} from 'lucide-vue-next'

defineProps<{
  modelValue: string
  mostrarMetricas: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'diaAnterior'): void
  (e: 'proximoDia'): void
  (e: 'go-today'): void
  (e: 'toggle-metrics'): void
}>()
</script>

<template>
  <Card>
    <CardContent class="pt-6">
      <div class="flex items-center">
        <div class="flex items-center gap-2">
          <Button size="icon" variant="outline" @click="emit('diaAnterior')">
            <ChevronLeft class="h-4 w-4"/>
          </Button>

          <Button size="icon" title="Hoje" variant="outline" @click="emit('go-today')">
            <CalendarArrowDown class="h-4 w-4"/>
          </Button>

          <Input
              :model-value="modelValue"
              class="w-auto"
              type="date"
              @update:model-value="(val) => emit('update:modelValue', String(val))"
          />

          <Button size="icon" variant="outline" @click="emit('proximoDia')">
            <ChevronRight class="h-4 w-4"/>
          </Button>
        </div>

        <div class="flex-grow"></div>

        <div class="text-sm text-gray-600">
          {{
            (() => {
              const [ano, mes, dia] = modelValue.split('-').map(Number);
              const dataLocal = new Date(ano, mes - 1, dia);

              return dataLocal.toLocaleDateString('pt-BR', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              });
            })()
          }}
        </div>

        <div class="w-3"></div>

        <Button
            class="flex items-center gap-2"
            variant="outline"
            @click="emit('toggle-metrics')"
        >
          <Eye v-if="mostrarMetricas" class="h-4 w-4 text-gray-500"/>
          <EyeOff v-else class="h-4 w-4 text-gray-500"/>
          Métricas
        </Button>
      </div>
    </CardContent>
  </Card>
</template>