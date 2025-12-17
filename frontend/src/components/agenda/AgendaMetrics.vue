<script lang="ts" setup>
import {Card} from '@/components/ui/card'

defineProps<{
  metricas: {
    total: number
    manha: number
    tarde: number
    emAndamento: number
    concluidos: number
  }
}>()
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
    <Card class="p-4 bg-white shadow-sm rounded-xl">
      <div class="text-sm text-gray-500">Total</div>
      <div class="text-2xl font-bold">{{ metricas.total }}</div>
    </Card>
    <Card class="p-4 bg-white shadow-sm rounded-xl">
      <div class="text-sm text-gray-500">Manhã</div>
      <div class="text-2xl font-bold text-blue-600">{{ metricas.manha }}</div>
    </Card>
    <Card class="p-4 bg-white shadow-sm rounded-xl">
      <div class="text-sm text-gray-500">Tarde</div>
      <div class="text-2xl font-bold text-purple-600">{{ metricas.tarde }}</div>
    </Card>
    <Card class="p-4 bg-white shadow-sm rounded-xl">
      <div class="text-sm text-gray-500">Andamento</div>
      <div class="text-2xl font-bold text-green-600">{{ metricas.emAndamento }}</div>
    </Card>
    <Card class="p-4 bg-white shadow-sm rounded-xl">
      <div class="text-sm text-gray-500">Concluídos</div>
      <div class="text-2xl font-bold text-gray-600">{{ metricas.concluidos }}</div>
    </Card>
  </div>
</template>