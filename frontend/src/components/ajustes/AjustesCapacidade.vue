<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Clock} from 'lucide-vue-next'

defineProps<{
  grupos: {
    rapido: { vagas: number | string, duracao: string },
    medio: { vagas: number | string, duracao: string },
    longo: { vagas: number | string, duracao: string }
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
        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-green-50/50 border border-green-100">
          <div class="sm:w-1/3">
            <span class="text-green-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-green-500"></span> Rápido
            </span>
            <p class="text-xs text-green-700 mt-1">Infusões de curta duração</p>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-green-800 uppercase font-bold">Descrição (Tempo)</Label>
            <Input v-model="grupos.rapido.duracao" class="bg-white mt-1"/>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-green-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="grupos.rapido.vagas" class="bg-white mt-1" type="number"/>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-blue-50/50 border border-blue-100">
          <div class="sm:w-1/3">
            <span class="text-blue-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-blue-500"></span> Médio
            </span>
            <p class="text-xs text-blue-700 mt-1">Infusões padrão</p>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-blue-800 uppercase font-bold">Descrição (Tempo)</Label>
            <Input v-model="grupos.medio.duracao" class="bg-white mt-1"/>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-blue-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="grupos.medio.vagas" class="bg-white mt-1" type="number"/>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-purple-50/50 border border-purple-100">
          <div class="sm:w-1/3">
            <span class="text-purple-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-purple-500"></span> Longo
            </span>
            <p class="text-xs text-purple-700 mt-1">Infusões extensas</p>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-purple-800 uppercase font-bold">Descrição (Tempo)</Label>
            <Input v-model="grupos.longo.duracao" class="bg-white mt-1"/>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-purple-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="grupos.longo.vagas" class="bg-white mt-1" type="number"/>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>