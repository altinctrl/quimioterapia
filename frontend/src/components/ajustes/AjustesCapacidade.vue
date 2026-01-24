<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Clock} from 'lucide-vue-next'

defineProps<{
  grupos: {
    rapido: { vagas: number | string, duracao: string },
    medio: { vagas: number | string, duracao: string },
    longo: { vagas: number | string, duracao: string },
    extra_longo: { vagas: number | string, duracao: string }
  }
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-gray-800">
        <Clock class="h-5 w-5 text-gray-500"/>
        Capacidade por Tempo de Infusão
      </CardTitle>
    </CardHeader>
    <CardContent>
      <p class="text-sm text-gray-500 mb-6">Defina quantas vagas simultâneas ou diárias existem para cada categoria
        de duração.</p>

      <div class="space-y-4">
        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-blue-50/50 border border-blue-100">
          <div class="sm:w-1/3">
            <span class="text-blue-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-blue-500"></span> Rápido
            </span>
            <div class="pl-5 text-sm font-medium text-gray-700 mt-1">Até 30 min</div>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-blue-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="grupos.rapido.vagas" class="bg-white mt-1" type="number"/>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-emerald-50/50 border border-emerald-100">
          <div class="sm:w-1/3">
            <span class="text-emerald-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-emerald-500"></span> Médio
            </span>
             <div class="pl-5 text-sm font-medium text-gray-700 mt-1">30 min - 2 horas</div>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-emerald-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="grupos.medio.vagas" class="bg-white mt-1" type="number"/>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-amber-50/50 border border-amber-100">
          <div class="sm:w-1/3">
            <span class="text-amber-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-amber-500"></span> Longo
            </span>
            <div class="pl-5 text-sm font-medium text-gray-700 mt-1">2 horas - 4 horas</div>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-amber-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="grupos.longo.vagas" class="bg-white mt-1" type="number"/>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-rose-50/50 border border-rose-100">
          <div class="sm:w-1/3">
            <span class="text-rose-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-rose-600"></span> Extra Longo
            </span>
            <div class="pl-5 text-sm font-medium text-gray-700 mt-1">Acima de 4 horas</div>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-rose-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="grupos.extra_longo.vagas" class="bg-white mt-1" type="number"/>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
