<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Calendar as CalendarIcon, ChevronDown} from 'lucide-vue-next'
import {MESES} from "@/constants/constAgenda.ts";

interface VagasInfo {
  count: number
  full: boolean
  label?: string
  blocked?: boolean
  hidden?: boolean
}

defineProps<{
  mes: string
  ano: string
  dias: Date[]
  espacosVazios: number
  dataSelecionada: string
  getInfoVagas: (dataIso: string) => VagasInfo
  isDiaBloqueado: (data: Date) => boolean
}>()

const emit = defineEmits<{
  (e: 'update:mes', value: string): void
  (e: 'update:ano', value: string): void
  (e: 'selecionarData', value: string): void
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <CalendarIcon class="h-5 w-5"/>
        Selecionar Data
      </CardTitle>
      <div class="flex gap-4 mt-4">
        <div class="w-1/2">
          <Label>Mês</Label>
          <div class="relative">
            <select
                :value="mes"
                class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background
                 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none
                  focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50
                   appearance-none"
                @input="emit('update:mes', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="m in MESES" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
            <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
          </div>
        </div>
        <div class="w-1/2">
          <Label>Ano</Label>
          <Input :model-value="ano" type="number" @update:model-value="(val) => emit('update:ano', String(val))"/>
        </div>
      </div>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-7 gap-2">
        <div v-for="d in ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb']" :key="d"
             class="text-center text-sm text-gray-500">{{ d }}
        </div>

        <div v-for="i in espacosVazios" :key="`empty-${i}`"></div>

        <button
            v-for="dia in dias"
            :key="dia.toISOString()"
            :class="[
            'p-2 border rounded flex flex-col items-center justify-center h-20 transition-colors relative',
            dataSelecionada === dia.toISOString().split('T')[0] ? 'border-blue-600 bg-blue-50' : '',
            isDiaBloqueado(dia) ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-60' : 'hover:border-blue-300 cursor-pointer bg-white'
          ]"
            :disabled="isDiaBloqueado(dia)"
            @click="!isDiaBloqueado(dia) && emit('selecionarData', dia.toISOString().split('T')[0])"
        >
          <span class="font-medium">{{ dia.getDate() }}</span>
          <span v-if="!isDiaBloqueado(dia)" class="mt-1 text-xs">
            <span v-if="getInfoVagas(dia.toISOString().split('T')[0]).hidden"></span>
            <span v-else-if="getInfoVagas(dia.toISOString().split('T')[0]).blocked" class="text-gray-400 font-medium text-[10px] uppercase">
              Não Permitido
            </span>
            <span v-else-if="getInfoVagas(dia.toISOString().split('T')[0]).full" class="text-red-600 font-bold">
              Cheio
            </span>
            <span v-else class="text-green-600 font-medium">
              {{ getInfoVagas(dia.toISOString().split('T')[0]).count }} vagas
            </span>
          </span>
        </button>
      </div>
      <div class="mt-2 text-xs text-gray-500 text-right">
        * Capacidade sujeita a alterações
      </div>
    </CardContent>
  </Card>
</template>
