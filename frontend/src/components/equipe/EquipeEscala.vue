<script lang="ts" setup>
import {computed} from 'vue'
import {format} from 'date-fns'
import {ptBR} from 'date-fns/locale'
import {type DateValue, fromDate, getLocalTimeZone} from '@internationalized/date'
import {Button} from '@/components/ui/button'
import {Calendar} from '@/components/ui/calendar'
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {cn} from '@/lib/utils'
import {CalendarIcon, ChevronLeft, ChevronRight, Plus, Trash2} from 'lucide-vue-next'
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {EscalaPlantao, Profissional} from "@/types/typesEquipe.ts";

const props = defineProps<{
  escala: EscalaPlantao[]
  profissionais: Profissional[]
  funcoes: string[]
  data: Date
  formState: {
    profissional_id: string,
    funcao: string,
    turno: string
  }
}>()

const emits = defineEmits<{
  (e: 'update:data', value: Date): void
  (e: 'adicionar'): void
  (e: 'remover', id: string): void
  (e: 'prev-day'): void
  (e: 'next-day'): void
}>()

const calendarValue = computed({
  get: () => props.data ? fromDate(props.data, getLocalTimeZone()) : undefined,
  set: (val: DateValue | undefined) => {
    if (val) emits('update:data', val.toDate(getLocalTimeZone()))
  }
})
</script>

<template>
  <div class="space-y-4">
    <Card>
      <div class="flex flex-col md:flex-row md:items-center gap-4 p-4">
        <div class="flex items-center gap-2">
          <Button size="icon" variant="outline" @click="$emit('prev-day')">
            <ChevronLeft class="h-4 w-4"/>
          </Button>

          <Popover>
            <PopoverTrigger as-child>
              <Button
                  :class="cn('w-[240px] justify-start text-left font-normal', !data && 'text-muted-foreground')"
                  variant="outline">
                <CalendarIcon class="mr-2 h-4 w-4"/>
                {{ data ? format(data, "PPP", {locale: ptBR}) : "Selecione a data" }}
              </Button>
            </PopoverTrigger>
            <PopoverContent align="start" class="w-auto p-0">
              <Calendar v-model="calendarValue" class="rounded-md border" mode="single"/>
            </PopoverContent>
          </Popover>

          <Button size="icon" variant="outline" @click="$emit('next-day')">
            <ChevronRight class="h-4 w-4"/>
          </Button>
        </div>

        <div class="flex-1"></div>

        <div class="flex flex-col md:flex-row gap-2 items-center">
          <Select v-model="formState.profissional_id">
            <SelectTrigger class="w-full md:w-[200px]">
              <SelectValue placeholder="Profissional"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="p in profissionais" :key="p.username" :value="p.username">
                {{ p.nome }}
              </SelectItem>
            </SelectContent>
          </Select>

          <Select v-model="formState.funcao">
            <SelectTrigger class="w-full md:w-[180px]">
              <SelectValue placeholder="Função"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="f in funcoes" :key="f" :value="f">{{ f }}</SelectItem>
            </SelectContent>
          </Select>

          <Select v-model="formState.turno">
            <SelectTrigger class="w-full md:w-[120px]">
              <SelectValue placeholder="Turno"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Manhã">Manhã</SelectItem>
              <SelectItem value="Tarde">Tarde</SelectItem>
              <SelectItem value="Integral">Integral</SelectItem>
            </SelectContent>
          </Select>

          <Button @click="$emit('adicionar')">
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
              <TableRow v-for="item in escala" :key="item.id">
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
              <TableRow v-if="escala.length === 0">
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
