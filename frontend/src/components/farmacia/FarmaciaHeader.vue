<script lang="ts" setup>
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {ChevronLeft, ChevronRight} from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'diaAnterior'): void
  (e: 'proximoDia'): void
}>()
</script>

<template>
  <Card>
    <CardContent class="pt-6">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <Button size="icon" variant="outline" @click="emit('diaAnterior')">
            <ChevronLeft class="h-4 w-4"/>
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
        <div class="ml-auto text-sm text-gray-600">
          {{
            new Date(modelValue).toLocaleDateString('pt-BR', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })
          }}
        </div>
      </div>
    </CardContent>
  </Card>
</template>