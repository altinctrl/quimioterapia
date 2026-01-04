<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {ChevronDown, ClipboardList} from 'lucide-vue-next'

const props = defineProps<{
  filtros: {
    tipoRelatorio: string
    periodoTipo: 'dia' | 'mes'
    diaSelecionado: string
    mesSelecionado: string
    anoSelecionado: string
    dataInicio: string
    dataFim: string
  }
  opcoesRelatorio: Array<{ value: string, label: string }>
  usaRangeDatas: boolean
}>()

const meses = [
  {value: '1', label: 'Janeiro'}, {value: '2', label: 'Fevereiro'}, {value: '3', label: 'Março'},
  {value: '4', label: 'Abril'}, {value: '5', label: 'Maio'}, {value: '6', label: 'Junho'},
  {value: '7', label: 'Julho'}, {value: '8', label: 'Agosto'}, {value: '9', label: 'Setembro'},
  {value: '10', label: 'Outubro'}, {value: '11', label: 'Novembro'}, {value: '12', label: 'Dezembro'}
]
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <ClipboardList class="h-6 w-6"/>
        Relatórios Gerenciais
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div>
        <Label>Tipo de Relatório</Label>
        <div class="relative">
          <select
              v-model="filtros.tipoRelatorio"
              class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
          >
            <option v-for="op in opcoesRelatorio" :key="op.value" :value="op.value">
              {{ op.label }}
            </option>
          </select>
          <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <template v-if="!usaRangeDatas">
          <div>
            <Label>Período</Label>
            <div class="relative">
              <select
                  v-model="filtros.periodoTipo"
                  class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
              >
                <option value="dia">Dia Específico</option>
                <option value="mes">Mês Específico</option>
              </select>
              <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
            </div>
          </div>

          <div v-if="filtros.periodoTipo === 'dia'">
            <Label>Data</Label>
            <Input v-model="filtros.diaSelecionado" type="date"/>
          </div>

          <div v-else class="grid grid-cols-2 gap-2">
            <div class="flex flex-col gap-1.5">
              <Label>Mês</Label>
              <div class="relative">
                <select
                    v-model="filtros.mesSelecionado"
                    class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
                >
                  <option v-for="mes in meses" :key="mes.value" :value="mes.value">
                    {{ mes.label }}
                  </option>
                </select>
                <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
              </div>
            </div>
            <div>
              <Label>Ano</Label>
              <Input v-model="filtros.anoSelecionado" type="number"/>
            </div>
          </div>
        </template>

        <template v-else>
          <div><Label>Data Início</Label><Input v-model="filtros.dataInicio" type="date"/></div>
          <div><Label>Data Fim</Label><Input v-model="filtros.dataFim" type="date"/></div>
        </template>
      </div>
    </CardContent>
  </Card>
</template>