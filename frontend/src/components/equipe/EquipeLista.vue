<script lang="ts" setup>
import {Button} from '@/components/ui/button'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Switch} from '@/components/ui/switch'
import {Edit} from 'lucide-vue-next'
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {Profissional} from "@/types/typesEquipe.ts";

const props = defineProps<{
  profissionais: Profissional[]
  cargos: string[]
  filtros: { cargo: string, ativo: string }
  formState: Profissional
  isEditing: boolean
  modalOpen: boolean
}>()

defineEmits<{
  (e: 'update:modalOpen', value: boolean): void
  (e: 'novo'): void
  (e: 'editar', p: Profissional): void
  (e: 'salvar'): void
}>()
</script>

<template>
  <div class="space-y-4">
    <Card>
      <div class="flex flex-col md:flex-row justify-between items-center gap-4 p-4">
        <div class="flex gap-4 items-center flex-1">
          <div class="flex items-center gap-2">
            <Label>Cargo:</Label>
            <Select v-model="props.filtros.cargo">
              <SelectTrigger class="w-[180px]">
                <SelectValue placeholder="Cargo"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Todos">Todos</SelectItem>
                <SelectItem v-for="c in cargos" :key="c" :value="c">{{ c }}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="flex items-center gap-2">
            <Label>Status:</Label>
            <Select v-model="props.filtros.ativo">
              <SelectTrigger class="w-[150px]">
                <SelectValue placeholder="Status"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Todos">Todos</SelectItem>
                <SelectItem value="Ativos">Ativos</SelectItem>
                <SelectItem value="Inativos">Inativos</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button @click="$emit('novo')">Novo Profissional</Button>
      </div>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Profissionais Cadastrados</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow class="hover:bg-transparent">
                <TableHead class="pl-4">Nome</TableHead>
                <TableHead>Cargo</TableHead>
                <TableHead>COREN</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead class="text-right pr-4"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="prof in profissionais" :key="prof.username">
                <TableCell class="font-medium pl-4">{{ prof.nome }}</TableCell>
                <TableCell>{{ prof.cargo }}</TableCell>
                <TableCell>{{ prof.registro || '-' }}</TableCell>
                <TableCell>{{ prof.ativo ? 'Ativo' : 'Inativo' }}</TableCell>
                <TableCell class="text-right">
                  <Button class="h-6 w-6 hover:bg-transparent hover:text-blue-600" size="icon" variant="ghost"
                          @click="$emit('editar', prof)">
                    <Edit class="h-4 w-4"/>
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow v-if="profissionais.length === 0">
                <TableCell class="text-center h-24" colspan="6">Nenhum profissional encontrado.</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <Dialog :open="modalOpen" @update:open="$emit('update:modalOpen', $event)">
      <DialogContent class="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{{ isEditing ? 'Editar Profissional' : 'Novo Profissional' }}</DialogTitle>
        </DialogHeader>
        <div class="grid gap-4 py-4">
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Usuário *</Label>
            <Input v-model="formState.username" :disabled="isEditing" class="col-span-3"/>
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Nome *</Label>
            <Input v-model="formState.nome" class="col-span-3"/>
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Cargo *</Label>
            <Select v-model="formState.cargo">
              <SelectTrigger class="col-span-3">
                <SelectValue placeholder="Selecione"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="c in cargos" :key="c" :value="c">{{ c }}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">COREN</Label>
            <Input v-model="formState.registro" class="col-span-3"/>
          </div>
          <div v-if="isEditing" class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Ativo</Label>
            <Switch v-model:checked="formState.ativo"/>
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" @click="$emit('salvar')">Salvar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
