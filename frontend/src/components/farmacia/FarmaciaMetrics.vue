<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {CheckCircle2, Clock, FlaskConical, Send} from "lucide-vue-next";

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
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
    <Card>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-sm font-medium">Pendentes</CardTitle>
        <Clock class="h-4 w-4 text-slate-500"/>
      </CardHeader>
      <CardContent>
        <div class="text-4xl font-bold text-slate-600">{{ metricas.pendente }}</div>
      </CardContent>
    </Card>
    <Card>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-sm font-medium">Em Preparação</CardTitle>
        <FlaskConical class="h-4 w-4 text-blue-500"/>
      </CardHeader>
      <CardContent>
        <div class="text-4xl font-bold text-blue-600">{{ metricas.emPreparacao }}</div>
      </CardContent>
    </Card>
    <Card>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-sm font-medium">Prontas</CardTitle>
        <CheckCircle2 class="h-4 w-4 text-green-500"/>
      </CardHeader>
      <CardContent>
        <div class="text-4xl font-bold text-green-600">{{ metricas.pronta }}</div>
      </CardContent>
    </Card>
    <Card>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-sm font-medium">Enviadas</CardTitle>
        <Send class="h-4 w-4 text-purple-600"/>
      </CardHeader>
      <CardContent>
        <div class="text-4xl font-bold text-purple-700">{{ metricas.enviada }}</div>
      </CardContent>
    </Card>
  </div>
</template>
