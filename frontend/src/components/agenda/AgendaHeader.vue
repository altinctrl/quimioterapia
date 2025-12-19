<script lang="ts" setup>
import {computed} from 'vue'
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Calendar as CalendarIcon, ChevronLeft, ChevronRight, Eye, EyeOff, Plus} from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string
  mostrarMetricas?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'navigate-prev'): void
  (e: 'navigate-next'): void
  (e: 'new-appointment'): void
  (e: 'toggle-metrics'): void
}>()

const data = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>

<template>
  <Card>
    <CardContent class="pt-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <Button size="icon" variant="outline" @click="$emit('navigate-prev')">
            <ChevronLeft class="h-4 w-4"/>
          </Button>
          <div class="flex items-center gap-2">
            <CalendarIcon class="h-5 w-5 text-gray-500"/>
            <Input v-model="data" class="w-auto" type="date"/>
          </div>
          <Button size="icon" variant="outline" @click="$emit('navigate-next')">
            <ChevronRight class="h-4 w-4"/>
          </Button>
        </div>
        <div class="flex items-center gap-2">
          <Button
              :title="mostrarMetricas ? 'Esconder Métricas' : 'Mostrar Métricas'"
              variant="outline"
              @click="$emit('toggle-metrics')"
          >
            <Eye v-if="mostrarMetricas" class="h-4 w-4 text-gray-500"/>
            <EyeOff v-else class="h-4 w-4 text-gray-500"/>
            Métricas
          </Button>

          <Button class="flex items-center gap-2" @click="$emit('new-appointment')">
            <Plus class="h-4 w-4"/>
            Novo Agendamento
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>