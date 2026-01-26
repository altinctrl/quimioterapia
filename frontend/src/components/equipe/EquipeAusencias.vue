<script lang="ts" setup>
import {computed, defineEmits, defineProps, ref} from 'vue'
import {addMonths, format} from 'date-fns'
import {ptBR} from 'date-fns/locale'
import {AusenciaProfissional, Profissional} from "@/types/equipeTypes.ts";
import {Button} from '@/components/ui/button'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {ChevronLeft, ChevronRight, Trash2} from "lucide-vue-next";
import {toast} from 'vue-sonner'
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";

const props = defineProps<{
  ausencias: AusenciaProfissional[]
  profissionais: Profissional[]
  mesReferencia: Date
}>()

const emits = defineEmits<{
  (e: 'update:mesReferencia', value: Date): void
  (e: 'registrar', dados: Partial<AusenciaProfissional>): void
  (e: 'remover', id: string): void
}>()

const isModalOpen = ref(false)
const motivos = ['Folga', 'LTS', 'Banco de Horas', 'Férias', 'Atestado', 'Outro']

const form = ref({
  profissional_id: '',
  data_inicio: format(new Date(), 'yyyy-MM-dd'),
  data_fim: format(new Date(), 'yyyy-MM-dd'),
  motivo: 'Folga',
  observacao: ''
})

function mudarMes(delta: number) {
  const novaData = addMonths(props.mesReferencia, delta)
  emits('update:mesReferencia', novaData)
}

function onSubmit() {
  if (!form.value.profissional_id || !form.value.data_inicio || !form.value.data_fim || !form.value.motivo) {
    toast.error('Preencha os campos obrigatórios.')
    return
  }

  emits('registrar', {...form.value})
  isModalOpen.value = false
  // Reset form
  form.value = {
    profissional_id: '',
    data_inicio: format(new Date(), 'yyyy-MM-dd'),
    data_fim: format(new Date(), 'yyyy-MM-dd'),
    motivo: 'Folga',
    observacao: ''
  }
}

function onRemove(id: string) {
  if (confirm('Tem certeza que deseja remover este registro?')) {
    emits('remover', id)
  }
}

const ausenciasOrdenadas = computed(() => {
  return [...props.ausencias].sort((a, b) => {
    const dateA = new Date(a.data_inicio).getTime()
    const dateB = new Date(b.data_inicio).getTime()
    if (dateA !== dateB) return dateA - dateB

    const dateFimA = new Date(a.data_fim).getTime()
    const dateFimB = new Date(b.data_fim).getTime()
    if (dateFimA !== dateFimB) return dateFimA - dateFimB

    const nomeA = a.profissional?.nome || ''
    const nomeB = b.profissional?.nome || ''
    return nomeA.localeCompare(nomeB)
  })
})
</script>

<template>
  <div class="space-y-4">
    <Card>
      <div class="flex justify-between items-center gap-4 p-4">
        <div class="flex items-center space-x-2">
          <Button size="icon" variant="outline" @click="mudarMes(-1)">
            <ChevronLeft class="h-4 w-4"/>
          </Button>
          <span class="font-medium min-w-[150px] text-center capitalize">
            {{ format(props.mesReferencia, 'MMMM yyyy', {locale: ptBR}) }}
        </span>
          <Button size="icon" variant="outline" @click="mudarMes(1)">
            <ChevronRight class="h-4 w-4"/>
          </Button>
        </div>
        <Button @click="isModalOpen = true">Novo Registro</Button>
      </div>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Ausências do Mês</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow class="hover:bg-transparent">
                <TableHead class="pl-4">Nome</TableHead>
                <TableHead>Início</TableHead>
                <TableHead>Fim</TableHead>
                <TableHead>Motivo</TableHead>
                <TableHead>Observações</TableHead>
                <TableHead class="text-right pr-4"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="item in ausenciasOrdenadas" :key="item.id">
                <TableCell class="font-medium pl-4">{{ item.profissional?.nome }}</TableCell>
                <TableCell>{{ format(new Date(item.data_inicio), 'dd/MM/yyyy') }}</TableCell>
                <TableCell>{{ format(new Date(item.data_fim), 'dd/MM/yyyy') }}</TableCell>
                <TableCell>{{ item.motivo }}</TableCell>
                <TableCell :title="item.observacao" class="max-w-[200px] truncate">{{ item.observacao }}</TableCell>
                <TableCell class="text-right">
                  <Button
                      class="h-6 w-6 hover:text-destructive hover:bg-transparent"
                      size="icon"
                      variant="ghost"
                      @click="onRemove(item.id)">
                    <Trash2 class="h-4 w-4"/>
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow v-if="props.ausencias.length === 0">
                <TableCell class="text-center h-24" colspan="6">
                  Nenhuma ausência registrada neste mês.
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <Dialog :open="isModalOpen" @update:open="isModalOpen = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Registrar Ausência</DialogTitle>
        </DialogHeader>
        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label>Profissional *</Label>
            <Select v-model="form.profissional_id">
              <SelectTrigger>
                <SelectValue placeholder="Selecione"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="p in props.profissionais" :key="p.username" :value="p.username">
                  {{ p.nome }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="grid gap-2">
              <Label>Data Início *</Label>
              <Input v-model="form.data_inicio" type="date"/>
            </div>
            <div class="grid gap-2">
              <Label>Data Fim *</Label>
              <Input v-model="form.data_fim" type="date"/>
            </div>
          </div>
          <div class="grid gap-2">
            <Label>Motivo *</Label>
            <Select v-model="form.motivo">
              <SelectTrigger>
                <SelectValue placeholder="Selecione"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="m in motivos" :key="m" :value="m">{{ m }}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="grid gap-2">
            <Label>Observações</Label>
            <Textarea v-model="form.observacao"/>
          </div>
        </div>
        <DialogFooter>
          <Button @click="onSubmit">Salvar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
