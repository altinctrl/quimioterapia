<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Activity, AlertTriangle, Ban, CheckCircle2, Clock2, Sun, Users} from "lucide-vue-next";

defineProps<{
  metricas: {
    total: number
    encaixes: number
    manha: number
    tarde: number
    emAndamento: number
    concluidos: number
    rapido: number
    medio: number
    longo: number
    extraLongo: number
    intercorrencias: number
    suspensos: number
    farmaciaPendentes: number
    farmaciaPreparando: number
    farmaciaProntas: number
  }
}>()
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
    <Card>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-sm font-medium">Agendamentos</CardTitle>
        <Users class="h-4 w-4 text-muted-foreground"/>
      </CardHeader>
      <CardContent>
        <div class="flex items-baseline gap-2">
          <div class="text-4xl font-bold">{{ metricas.total }}</div>
          <span class="text-sm text-muted-foreground">Total</span>
          <span class="text-gray-300">|</span>
          <div class="text-3xl font-bold">{{ metricas.encaixes }}</div>
          <span class="text-sm text-muted-foreground">Encaixes</span>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-sm font-medium">Agendamentos por Turno</CardTitle>
        <Sun class="h-4 w-4 text-yellow-500"/>
      </CardHeader>
      <CardContent>
        <div class="flex items-baseline gap-2">
          <div class="text-4xl font-bold">{{ metricas.manha }}</div>
          <span class="text-sm text-muted-foreground">Manhã</span>
          <span class="text-gray-300">|</span>
          <div class="text-4xl font-bold">{{ metricas.tarde }}</div>
          <span class="text-sm text-muted-foreground">Tarde</span>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-sm font-medium">Agendamentos por Duração</CardTitle>
        <Clock2 class="h-4 w-4 text-blue-600"/>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="grid grid-cols-4 gap-2 text-center text-sm">
          <div class="bg-blue-50 p-2 rounded border border-blue-100">
            <span class="text-2xl block font-bold text-blue-700">{{ metricas.rapido }}</span>
            <span class="text-xs text-blue-600">Rápido</span>
          </div>
          <div class="bg-emerald-50 p-2 rounded border border-emerald-100">
            <span class="text-2xl block font-bold text-emerald-700">{{ metricas.medio }}</span>
            <span class="text-xs text-emerald-600">Médio</span>
          </div>
          <div class="bg-amber-50 p-2 rounded border border-amber-100">
            <span class="text-2xl block font-bold text-amber-700">{{ metricas.longo }}</span>
            <span class="text-xs text-amber-600">Longo</span>
          </div>
          <div class="bg-rose-50 p-2 rounded border border-rose-100">
            <span class="text-2xl block font-bold text-rose-700">{{ metricas.extraLongo }}</span>
            <span class="text-xs text-rose-600">Extra Longo</span>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>

  <div class="grid grid-cols-4 gap-4">
    <div class="bg-blue-50 border border-blue-100 rounded-lg p-4 flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-blue-600 uppercase">Em Atendimento</p>
        <p class="text-2xl font-bold text-blue-900">{{ metricas.emAndamento }}</p>
      </div>
      <Activity class="h-8 w-8 text-blue-200"/>
    </div>
    <div class="bg-red-50 border border-red-100 rounded-lg p-4 flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-red-600 uppercase">Suspensos</p>
        <p class="text-2xl font-bold text-red-900">{{ metricas.suspensos }}</p>
      </div>
      <Ban class="h-8 w-8 text-red-200"/>
    </div>
    <div class="bg-orange-50 border border-orange-100 rounded-lg p-4 flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-orange-600 uppercase">Intercorrências</p>
        <p class="text-2xl font-bold text-orange-900">{{ metricas.intercorrencias }}</p>
      </div>
      <AlertTriangle class="h-8 w-8 text-orange-200"/>
    </div>

    <div class="bg-green-50 border border-green-100 rounded-lg p-4 flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-green-600 uppercase">Concluídos</p>
        <p class="text-2xl font-bold text-green-900">{{ metricas.concluidos }}</p>
      </div>
      <CheckCircle2 class="h-8 w-8 text-green-200"/>
    </div>
  </div>
</template>