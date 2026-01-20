<script lang="ts" setup>
import {computed, defineEmits, defineProps, ref} from 'vue'
import type {Profissional} from '@/types'
import {Button} from '@/components/ui/button'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Switch} from '@/components/ui/switch'
import {Edit} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";

const props = defineProps<{
  profissionais: Profissional[]
  cargos: string[]
}>()

const emits = defineEmits<{
  (e: 'criar', dados: Partial<Profissional>): void
  (e: 'atualizar', dados: Partial<Profissional>): void
}>()

const isModalOpen = ref(false)
const isEditing = ref(false)

const filtroCargo = ref('Todos')
const filtroAtivo = ref('Todos')

const form = ref({
  username: '',
  nome: '',
  cargo: '',
  registro: '',
  ativo: true
})

const profissionaisFiltrados = computed(() => {
  return props.profissionais
      .filter(p => {
        const matchCargo = filtroCargo.value === 'Todos' || p.cargo === filtroCargo.value
        const matchAtivo = filtroAtivo.value === 'Todos'
            ? true
            : filtroAtivo.value === 'Ativos' ? p.ativo
                : !p.ativo
        return matchCargo && matchAtivo
      })
      .sort((a, b) => a.nome.localeCompare(b.nome))
})

function openModal(profissional: Profissional | null = null) {
  if (profissional) {
    isEditing.value = true
    form.value = {
      ...profissional,
      registro: profissional.registro || ""
    }
  } else {
    isEditing.value = false
    const cargoPadrao = props.cargos.length > 0 ? props.cargos[0] : ''
    form.value = {username: '', nome: '', cargo: cargoPadrao, registro: '', ativo: true}
  }
  isModalOpen.value = true
}

function onSubmit() {
  if (!form.value.username || !form.value.nome || !form.value.cargo) {
    toast.error('Preencha os campos obrigatórios.')
    return
  }

  if (isEditing.value) {
    emits('atualizar', {...form.value})
  } else {
    emits('criar', {...form.value})
  }
  isModalOpen.value = false
}
</script>

<template>
  <div class="space-y-4">
    <Card>
      <div class="flex flex-col md:flex-row justify-between items-center gap-4 p-4">
        <div class="flex gap-4 items-center flex-1">
          <div class="flex items-center gap-2">
            <Label>Cargo:</Label>
            <Select v-model="filtroCargo">
              <SelectTrigger class="w-[180px]">
                <SelectValue placeholder="Cargo"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Todos">Todos</SelectItem>
                <SelectItem v-for="c in props.cargos" :key="c" :value="c">{{ c }}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="flex items-center gap-2">
            <Label>Status:</Label>
            <Select v-model="filtroAtivo">
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

        <Button @click="openModal()">Novo Profissional</Button>
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
                <TableHead>Registro</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead class="text-right pr-4"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="prof in profissionaisFiltrados" :key="prof.username">
                <TableCell class="font-medium pl-4">{{ prof.nome }}</TableCell>
                <TableCell>{{ prof.cargo }}</TableCell>
                <TableCell>{{ prof.registro || '-' }}</TableCell>
                <TableCell>
                  {{ prof.ativo ? 'Ativo' : 'Inativo' }}
                </TableCell>
                <TableCell class="text-right">
                  <Button class="h-6 w-6 hover:bg-transparent hover:text-blue-600" size="icon" variant="ghost"
                          @click="openModal(prof)">
                    <Edit class="h-4 w-4"/>
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow v-if="profissionaisFiltrados.length === 0">
                <TableCell class="text-center h-24" colspan="6">Nenhum profissional encontrado.</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <Dialog :open="isModalOpen" @update:open="isModalOpen = $event">
      <DialogContent class="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{{ isEditing ? 'Editar Profissional' : 'Novo Profissional' }}</DialogTitle>
        </DialogHeader>
        <div class="grid gap-4 py-4">
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Usuário *</Label>
            <Input v-model="form.username" :disabled="isEditing" class="col-span-3"/>
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Nome *</Label>
            <Input v-model="form.nome" class="col-span-3"/>
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Cargo *</Label>
            <Select v-model="form.cargo">
              <SelectTrigger class="col-span-3">
                <SelectValue placeholder="Selecione"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="c in props.cargos" :key="c" :value="c">{{ c }}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Registro</Label>
            <Input v-model="form.registro" class="col-span-3" placeholder="COREN, CRM..."/>
          </div>
          <div v-if="isEditing" class="grid grid-cols-4 items-center gap-4">
            <Label class="text-right">Ativo</Label>
            <Switch v-model:checked="form.ativo"/>
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" @click="onSubmit">Salvar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
