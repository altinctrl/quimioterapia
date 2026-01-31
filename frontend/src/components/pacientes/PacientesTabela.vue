<script lang="ts" setup>
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {Paciente} from "@/types/typesPaciente.ts";

defineProps<{
  pacientes: Paciente[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', paciente: Paciente): void
}>()

const calcularIdade = (dataNasc: string | Date | undefined) => {
  if (!dataNasc) return 0
  const hoje = new Date()
  const nasc = new Date(dataNasc)
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const m = hoje.getMonth() - nasc.getMonth()
  if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) {
    idade--
  }
  return idade
}
</script>

<template>
  <div class="rounded-md border">
    <Table>
      <TableHeader>
        <TableRow class="hover:bg-transparent">
          <TableHead class="pl-4">Nome</TableHead>
          <TableHead>Prontuário</TableHead>
          <TableHead>CPF</TableHead>
          <TableHead>Idade</TableHead>
          <TableHead>Telefone</TableHead>
          <TableHead>Protocolo</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-if="pacientes.length === 0">
          <TableCell class="text-center text-gray-500 py-8" colspan="6">
            {{ loading ? 'Carregando...' : 'Nenhum paciente encontrado' }}
          </TableCell>
        </TableRow>

        <TableRow
            v-for="paciente in pacientes"
            v-else
            :key="paciente.id"
            class="cursor-pointer hover:bg-gray-50"
            @click="emit('select', paciente)"
        >
          <TableCell class="font-medium pl-4">{{ paciente.nome }}</TableCell>
          <TableCell>{{ paciente.registro }}</TableCell>
          <TableCell>{{ paciente.cpf }}</TableCell>
          <TableCell>{{ calcularIdade(paciente.dataNascimento) }} anos</TableCell>
          <TableCell>{{ paciente.telefone }}</TableCell>
          <TableCell>
            <Badge class="font-normal" variant="outline">
              {{ paciente.protocoloUltimaPrescricao || '-'}}
            </Badge>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>