<script lang="ts" setup>
import {format} from 'date-fns'
import {ptBR} from 'date-fns/locale'
import {Button} from '@/components/ui/button'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {ChevronLeft, ChevronRight, Trash2} from "lucide-vue-next";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {AusenciaProfissional, Profissional} from "@/types/typesEquipe.ts";
import {motivos} from "@/constants/constEquipe.ts";

defineProps<{
  ausencias: AusenciaProfissional[]
  profissionais: Profissional[]
  mes: Date
  modalOpen: boolean
  formState: { profissional_id: string, data_inicio: string, data_fim: string, motivo: string, observacao: string }
}>()

defineEmits<{
  (e: 'update:modalOpen', value: boolean): void
  (e: 'abrirModal'): void
  (e: 'salvar'): void
  (e: 'remover', id: string): void
  (e: 'prev-month'): void
  (e: 'next-month'): void
}>()
</script>

<template>
  <div class="space-y-4">
    <Card>
      <div class="flex justify-between items-center gap-4 p-4">
        <div class="flex items-center space-x-2">
          <Button size="icon" variant="outline" @click="$emit('prev-month')">
            <ChevronLeft class="h-4 w-4"/>
          </Button>
          <span class="font-medium min-w-[150px] text-center capitalize">
            {{ format(mes, 'MMMM yyyy', {locale: ptBR}) }}
        </span>
          <Button size="icon" variant="outline" @click="$emit('next-month')">
            <ChevronRight class="h-4 w-4"/>
          </Button>
        </div>
        <Button @click="$emit('abrirModal')">Novo Registro</Button>
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
              <TableRow v-for="item in ausencias" :key="item.id">
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
                      @click="$emit('remover', item.id)">
                    <Trash2 class="h-4 w-4"/>
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow v-if="ausencias.length === 0">
                <TableCell class="text-center h-24" colspan="6">
                  Nenhuma ausência registrada neste mês.
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <Dialog :open="modalOpen" @update:open="$emit('update:modalOpen', $event)">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Registrar Ausência</DialogTitle>
        </DialogHeader>
        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label>Profissional *</Label>
            <Select v-model="formState.profissional_id">
              <SelectTrigger>
                <SelectValue placeholder="Selecione"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="p in profissionais" :key="p.username" :value="p.username">
                  {{ p.nome }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="grid gap-2">
              <Label>Data Início *</Label>
              <Input v-model="formState.data_inicio" type="date"/>
            </div>
            <div class="grid gap-2">
              <Label>Data Fim *</Label>
              <Input v-model="formState.data_fim" type="date"/>
            </div>
          </div>
          <div class="grid gap-2">
            <Label>Motivo *</Label>
            <Select v-model="formState.motivo">
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
            <Textarea v-model="formState.observacao"/>
          </div>
        </div>
        <DialogFooter>
          <Button @click="$emit('salvar')">Salvar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
