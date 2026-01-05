<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Search} from 'lucide-vue-next'
import type {Paciente} from '@/types'

const props = defineProps<{
  busca: string
  resultados: Paciente[]
  mostrarResultados: boolean
}>()

const emit = defineEmits<{
  (e: 'update:busca', value: string): void
  (e: 'update:mostrarResultados', value: boolean): void
  (e: 'selecionar', paciente: Paciente): void
  (e: 'focus'): void
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <Search class="h-5 w-5"/>
        Buscar Paciente
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="relative">
        <Label>Nome ou CPF</Label>
        <Input
            :model-value="busca"
            class="mt-1"
            placeholder="Digite para buscar..."
            @focus="emit('update:mostrarResultados', true)"
            @update:model-value="(val) => emit('update:busca', String(val))"
        />
        <div v-if="mostrarResultados && resultados.length > 0"
             class="absolute z-10 w-full bg-white border rounded shadow-lg mt-1 max-h-48 overflow-auto">
          <div
              v-for="p in resultados"
              :key="p.id"
              class="p-2 hover:bg-gray-100 cursor-pointer"
              @click="emit('selecionar', p)"
          >
            <div class="font-medium">{{ p.nome }}</div>
            <div class="text-xs text-gray-500">{{ p.cpf }}</div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>