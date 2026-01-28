<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Clock} from 'lucide-vue-next'

defineProps<{
  vagas: {
    infusao_rapido: number;
    infusao_medio: number;
    infusao_longo: number;
    infusao_extra_longo: number;
    consultas: number;
    procedimentos: number;
  };
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
            <Input v-model="vagas.infusao_rapido" class="bg-white mt-1" type="number"/>
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
            <Input v-model="vagas.infusao_medio" class="bg-white mt-1" type="number"/>
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
            <Input v-model="vagas.infusao_longo" class="bg-white mt-1" type="number"/>
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
            <Input v-model="vagas.infusao_extra_longo" class="bg-white mt-1" type="number"/>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>

  <Card class="mt-6">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-gray-800">
        <Clock class="h-5 w-5 text-gray-500"/>
        Capacidade por Tipo de Agendamento
      </CardTitle>
    </CardHeader>
    <CardContent>
      <p class="text-sm text-gray-500 mb-6">
        Configuração temporária (somente no frontend) enquanto o backend não oferece suporte.
      </p>

      <div class="space-y-4">
        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-slate-50 border border-slate-100">
          <div class="sm:w-1/3">
            <span class="text-slate-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-slate-500"></span> Consulta
            </span>
            <p class="text-xs text-slate-600 mt-1">Vagas para agendamentos do tipo consulta</p>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-slate-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="vagas.consultas" class="bg-white mt-1" type="number" min="0"/>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-slate-50 border border-slate-100">
          <div class="sm:w-1/3">
            <span class="text-slate-800 font-semibold text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-slate-500"></span> Procedimento
            </span>
            <p class="text-xs text-slate-600 mt-1">Vagas para agendamentos do tipo procedimento</p>
          </div>
          <div class="flex-1 w-full">
            <Label class="text-xs text-slate-800 uppercase font-bold">Vagas Totais</Label>
            <Input v-model="vagas.procedimentos" class="bg-white mt-1" type="number" min="0"/>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
