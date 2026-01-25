<script lang="ts" setup>
import {computed} from 'vue'
import {useAppStore} from '@/stores/app'
import {useConfiguracaoLocalStore} from '@/stores/configuracaoLocal'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Calendar as CalendarIcon, ChevronDown} from 'lucide-vue-next'
import type {Agendamento, GrupoInfusao, TipoAgendamento} from '@/types'

const props = defineProps<{
  mes: string
  ano: string
  dataSelecionada: string
  tipoAgendamento: TipoAgendamento
  grupoInfusao: GrupoInfusao
}>()

const emit = defineEmits<{
  (e: 'update:mes', value: string): void
  (e: 'update:ano', value: string): void
  (e: 'selecionarData', value: string): void
}>()

const appStore = useAppStore()
const configuracaoLocalStore = useConfiguracaoLocalStore()

const meses = [
  {value: '1', label: 'Janeiro'}, {value: '2', label: 'Fevereiro'}, {value: '3', label: 'Março'},
  {value: '4', label: 'Abril'}, {value: '5', label: 'Maio'}, {value: '6', label: 'Junho'},
  {value: '7', label: 'Julho'}, {value: '8', label: 'Agosto'}, {value: '9', label: 'Setembro'},
  {value: '10', label: 'Outubro'}, {value: '11', label: 'Novembro'}, {value: '12', label: 'Dezembro'}
]

const diasDoMes = computed(() => {
  const year = parseInt(props.ano)
  const month = parseInt(props.mes) - 1
  const date = new Date(year, month, 1)
  const days: Date[] = []
  while (date.getMonth() === month) {
    days.push(new Date(date))
    date.setDate(date.getDate() + 1)
  }
  return days
})

const espacosVazios = computed(() => {
  if (diasDoMes.value.length === 0) return 0
  return diasDoMes.value[0].getDay()
})

const todayStr = new Date().toISOString().split('T')[0]

const isDayDisabled = (date: Date) => {
  const dateStr = date.toISOString().split('T')[0]
  const isPastDate = dateStr < todayStr
  const dayOfWeek = date.getDay()
  const isClosedDay = !appStore.parametros.diasFuncionamento.includes(dayOfWeek)
  return isPastDate || isClosedDay
}

const isConsideradoNaCapacidade = (ag: Agendamento) => {
  return ag.status !== 'remarcado' && ag.status !== 'suspenso'
}

const labelCapacidade = computed(() => {
  if (props.tipoAgendamento === 'infusao') return `grupo: ${props.grupoInfusao}`
  if (props.tipoAgendamento === 'consulta') return 'consulta'
  return 'procedimento'
})

const getVagasInfo = (data: string) => {
  const agendamentosNoDia = appStore.getAgendamentosDoDia(data)

  if (props.tipoAgendamento !== 'infusao') {
    const tipo = props.tipoAgendamento
    const limite = configuracaoLocalStore.getLimite(tipo)
    const countNoTipo = agendamentosNoDia.reduce((acc, ag) => {
      if (!isConsideradoNaCapacidade(ag)) return acc
      return ag.tipo === tipo ? acc + 1 : acc
    }, 0)

    const vagasRestantes = limite - countNoTipo

    return {
      count: vagasRestantes,
      full: vagasRestantes <= 0
    }
  }

  const grupo = props.grupoInfusao
  const limiteGrupo = appStore.parametros.gruposInfusao[grupo]?.vagas || 4

  const countNoGrupo = agendamentosNoDia.reduce((acc, ag) => {
    if (!isConsideradoNaCapacidade(ag)) return acc
    if (ag.tipo !== 'infusao') return acc

    const p = appStore.getPacienteById(ag.pacienteId)
    const prot = appStore.getProtocoloById((p as any)?.protocoloId || '')
    const g = (prot as any)?.grupoInfusao || 'medio'
    return g === grupo ? acc + 1 : acc
  }, 0)

  const vagasRestantes = limiteGrupo - countNoGrupo

  return {
    count: vagasRestantes,
    full: vagasRestantes <= 0
  }
}
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
                class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
                @input="emit('update:mes', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="m in meses" :key="m.value" :value="m.value">{{ m.label }}</option>
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
            v-for="dia in diasDoMes"
            :key="dia.toISOString()"
            :class="[
            'p-2 border rounded flex flex-col items-center justify-center h-20 transition-colors relative',
            dataSelecionada === dia.toISOString().split('T')[0] ? 'border-blue-600 bg-blue-50' : '',
            isDayDisabled(dia) ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-60' : 'hover:border-blue-300 cursor-pointer bg-white'
          ]"
            :disabled="isDayDisabled(dia)"
            @click="!isDayDisabled(dia) && emit('selecionarData', dia.toISOString().split('T')[0])"
        >
          <span class="font-medium">{{ dia.getDate() }}</span>
          <div v-if="!isDayDisabled(dia)" class="mt-1 text-xs">
            <span v-if="getVagasInfo(dia.toISOString().split('T')[0]).full" class="text-red-600 font-bold">Cheio</span>
            <span v-else class="text-green-600 font-medium">{{
                getVagasInfo(dia.toISOString().split('T')[0]).count
              }} vagas</span>
          </div>
        </button>
      </div>
      <div class="mt-2 text-xs text-gray-500 text-right">
        Vagas para <span class="capitalize font-medium">{{ labelCapacidade }}</span>
      </div>
    </CardContent>
  </Card>
</template>