<script lang="ts" setup>
import {Card, CardContent} from '@/components/ui/card'

defineProps<{
  metricas: {
    total: number
    pendente: number
    emPreparacao: number
    pronta: number
    enviada: number
  }
}>()
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
    <Card>
      <CardContent class="pt-6"><p class="text-3xl font-bold">{{ metricas.total }}</p>
        <p class="text-xs">Total</p></CardContent>
    </Card>
    <Card>
      <CardContent class="pt-6"><p class="text-3xl font-bold text-yellow-600">{{ metricas.pendente }}</p>
        <p class="text-xs">Pendentes</p></CardContent>
    </Card>
    <Card>
      <CardContent class="pt-6"><p class="text-3xl font-bold text-blue-600">{{ metricas.emPreparacao }}</p>
        <p class="text-xs">Preparando</p></CardContent>
    </Card>
    <Card>
      <CardContent class="pt-6"><p class="text-3xl font-bold text-green-600">{{ metricas.pronta }}</p>
        <p class="text-xs">Prontas</p></CardContent>
    </Card>
    <Card>
      <CardContent class="pt-6"><p class="text-3xl font-bold text-gray-600">{{ metricas.enviada }}</p>
        <p class="text-xs">Enviadas</p></CardContent>
    </Card>
  </div>
</template>