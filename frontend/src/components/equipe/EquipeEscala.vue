<script lang="ts" setup>
import {computed, ref, watchEffect} from 'vue'
import {addDays, format} from 'date-fns'
import {ptBR} from 'date-fns/locale'
import {type DateValue, fromDate, getLocalTimeZone} from '@internationalized/date'
import {EscalaPlantao, Profissional} from "@/types/typesEquipe.ts";
import {Button} from '@/components/ui/button'
import {Calendar} from '@/components/ui/calendar'
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {cn} from '@/lib/utils'
import {CalendarIcon, ChevronLeft, ChevronRight, Plus, Trash2} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";

const props = defineProps<{
  escala: EscalaPlantao[]
  profissionais: Profissional[]
  funcoes: string[]
  data: Date
}>()

const emits = defineEmits<{
  (e: 'update:data', value: Date): void
  (e: 'adicionar', dados: Partial<EscalaPlantao>): void
  (e: 'remover', id: string): void
}>()

const calendarValue = computed({
  get: () => props.data ? fromDate(props.data, getLocalTimeZone()) : undefined,
  set: (val: DateValue | undefined) => {
    if (val) emits('update:data', val.toDate(getLocalTimeZone()))
  }
})

const form = ref({
  profissional_id: '',
  funcao: '',
  turno: 'Integral' as 'Manhã' | 'Tarde' | 'Integral'
})

watchEffect(() => {
  if (props.funcoes.length > 0 && !form.value.funcao) {
    form.value.funcao = props.funcoes[0]
  }
})

const escalaOrdenada = computed(() => {
  return [...props.escala].sort((a, b) => {
    const funcA = a.funcao || ''
    const funcB = b.funcao || ''
    const compareFuncao = funcA.localeCompare(funcB)
    if (compareFuncao !== 0) return compareFuncao

    const turnoA = a.turno || ''
    const turnoB = b.turno || ''
    const compareTurno = turnoA.localeCompare(turnoB)
    if (compareTurno !== 0) return compareTurno

    const nomeA = a.profissional?.nome || ''
    const nomeB = b.profissional?.nome || ''
    return nomeA.localeCompare(nomeB)
  })
})

const profissionaisDisponiveis = computed(() => {
  return props.profissionais.filter(p =>
      p.ativo && (p.cargo.includes('Enfermeiro') || p.cargo.includes('Técnico'))
  )
})

function onAdd() {
  if (!form.value.profissional_id) {
    toast.error('Selecione um profissional para adicionar à escala.')
    return
  }
  emits('adicionar', {
    data: format(props.data, 'yyyy-MM-dd'),
    ...form.value
  })
  form.value.profissional_id = ''
}

function diaAnterior() {
  const novaData = addDays(props.data, -1)
  emits('update:data', novaData)
}

function proximoDia() {
  const novaData = addDays(props.data, 1)
  emits('update:data', novaData)
}
</script>

<template>
  <div class="space-y-4">
    <Card>
      <div class="flex flex-col md:flex-row md:items-center gap-4 p-4">
        <div class="flex items-center gap-2">
          <Button size="icon" variant="outline" @click="diaAnterior">
            <ChevronLeft class="h-4 w-4"/>
          </Button>

          <Popover>
            <PopoverTrigger as-child>
              <Button
                  :class="cn('w-[240px] justify-start text-left font-normal', !props.data && 'text-muted-foreground')"
                  variant="outline">
                <CalendarIcon class="mr-2 h-4 w-4"/>
                {{ props.data ? format(props.data, "PPP", {locale: ptBR}) : "Selecione a data" }}
              </Button>
            </PopoverTrigger>
            <PopoverContent align="start" class="w-auto p-0">
              <Calendar v-model="calendarValue" class="rounded-md border" mode="single"/>
            </PopoverContent>
          </Popover>

          <Button size="icon" variant="outline" @click="proximoDia">
            <ChevronRight class="h-4 w-4"/>
          </Button>
        </div>

        <div class="flex-1"></div>

        <div class="flex flex-col md:flex-row gap-2 items-center">
          <Select v-model="form.profissional_id">
            <SelectTrigger class="w-full md:w-[200px]">
              <SelectValue placeholder="Profissional"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="p in profissionaisDisponiveis" :key="p.username" :value="p.username">
                {{ p.nome }}
              </SelectItem>
            </SelectContent>
          </Select>

          <Select v-model="form.funcao">
            <SelectTrigger class="w-full md:w-[180px]">
              <SelectValue placeholder="Função"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="f in props.funcoes" :key="f" :value="f">{{ f }}</SelectItem>
            </SelectContent>
          </Select>

          <Select v-model="form.turno">
            <SelectTrigger class="w-full md:w-[120px]">
              <SelectValue placeholder="Turno"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Manhã">Manhã</SelectItem>
              <SelectItem value="Tarde">Tarde</SelectItem>
              <SelectItem value="Integral">Integral</SelectItem>
            </SelectContent>
          </Select>

          <Button @click="onAdd">
            <Plus class="h-4 w-4 mr-2"/>
            Adicionar
          </Button>
        </div>
      </div>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Escala do Dia</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow class="hover:bg-transparent">
                <TableHead class="pl-4">Função</TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Turno</TableHead>
                <TableHead class="text-right pr-4"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="item in escalaOrdenada" :key="item.id">
                <TableCell class="font-medium pl-4">{{ item.funcao }}</TableCell>
                <TableCell>{{ item.profissional?.nome }}</TableCell>
                <TableCell>{{ item.turno }}</TableCell>
                <TableCell class="text-right">
                  <Button class="h-6 w-6 hover:text-destructive hover:bg-transparent"
                          size="icon" variant="ghost" @click="$emit('remover', item.id)">
                    <Trash2 class="h-4 w-4"/>
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow v-if="escalaOrdenada.length === 0">
                <TableCell class="text-center h-24 text-muted-foreground" colspan="4">
                  Nenhum profissional escalado para este dia.
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
