<script lang="ts" setup>
import {ref, watch} from 'vue'
import {useAppStore} from '@/stores/app'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Badge} from '@/components/ui/badge'
import {Check, Search} from 'lucide-vue-next'
import {Dialog, DialogContent, DialogHeader, DialogTitle,} from '@/components/ui/dialog'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import type {Paciente} from '@/types'
import {buscaPacienteFormSchema} from "@/schemas/pacienteSchema.ts";
import {useForm} from "vee-validate";

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'paciente-importado', paciente: Paciente): void
}>()

const appStore = useAppStore()

const {errors, defineField, handleSubmit, resetForm} = useForm({
  validationSchema: buscaPacienteFormSchema,
  initialValues: {termo: ''}
})

const [termoExterno, termoProps] = defineField('termo')
const resultadosExternos = ref<Paciente[]>([])
const buscandoExterno = ref(false)

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    resetForm()
    resultadosExternos.value = []
  }
})

const handleBuscarExterno = handleSubmit(async (values) => {
  buscandoExterno.value = true
  try {
    const res = await api.get('/api/pacientes/externo/buscar', {
      params: {termo: values.termo}
    })
    resultadosExternos.value = res.data
    if (res.data.length === 0) toast.info("Nenhum paciente encontrado.")
  } catch (e) {
    toast.error("Erro ao buscar no sistema externo")
  } finally {
    buscandoExterno.value = false
  }
})

const verificarCadastroLocal = (cpfExterno: string) => {
  return appStore.pacientes.some(p => p.cpf === cpfExterno)
}

const handleImportarPaciente = async (pacienteExterno: Paciente) => {
  const jaEstavaCadastrado = verificarCadastroLocal(pacienteExterno.cpf)

  try {
    const pacienteRetornado = await appStore.adicionarPaciente(pacienteExterno)

    if (jaEstavaCadastrado) {
      toast.info(`Paciente ${pacienteExterno.nome} já estava cadastrado. Selecionado.`)
    } else {
      toast.success(`Paciente ${pacienteExterno.nome} importado com sucesso!`)
    }

    emit('paciente-importado', pacienteRetornado)
    emit('update:open', false)

  } catch (e) {
    console.error(e)
    toast.error("Erro ao importar paciente")
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-3xl">
      <DialogHeader>
        <DialogTitle>Importar Paciente do AGHU</DialogTitle>
      </DialogHeader>

      <div class="space-y-4">
        <div class="space-y-1">
          <div class="flex gap-2">
            <Input
                v-model="termoExterno"
                :class="{'border-destructive': errors.termo}"
                placeholder="Nome, CPF ou Prontuário..."
                v-bind="termoProps"
                @keyup.enter="handleBuscarExterno"
            />
            <Button :disabled="buscandoExterno" @click="handleBuscarExterno">
              <Search class="h-4 w-4 mr-2"/>
              {{ buscandoExterno ? 'Buscando...' : 'Buscar' }}
            </Button>
          </div>
          <p v-if="errors.termo" class="text-xs font-medium text-destructive">
            {{ errors.termo }}
          </p>
        </div>

        <div class="border rounded-md max-h-[300px] overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="pl-4">Nome</TableHead>
                <TableHead>CPF</TableHead>
                <TableHead>Nascimento</TableHead>
                <TableHead class="text-center">Ação</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="resultadosExternos.length === 0">
                <TableCell class="text-center text-gray-500 py-4" colspan="4">
                  {{ buscandoExterno ? 'Pesquisando...' : 'Faça uma busca para ver os resultados.' }}
                </TableCell>
              </TableRow>

              <TableRow
                  v-for="p in resultadosExternos"
                  :key="p.registro"
                  :class="verificarCadastroLocal(p.cpf) ? 'bg-blue-50/50' : ''"
              >
                <TableCell>
                  <div class="flex items-center gap-2 pl-2">
                    {{ p.nome }}
                    <Badge
                        v-if="verificarCadastroLocal(p.cpf)"
                        class="h-5 px-1.5 text-[10px] bg-green-100 text-green-700 border-green-200 gap-1 hover:bg-green-100"
                        variant="secondary"
                    >
                      <Check class="h-3 w-3"/>
                      Cadastrado
                    </Badge>
                  </div>
                </TableCell>
                <TableCell>{{ p.cpf }}</TableCell>
                <TableCell>{{ new Date(p.dataNascimento).toLocaleDateString('pt-BR') }}</TableCell>
                <TableCell class="text-center">
                  <Button
                      :variant="verificarCadastroLocal(p.cpf) ? 'secondary' : 'outline'"
                      size="sm"
                      @click="handleImportarPaciente(p)"
                  >
                    {{ verificarCadastroLocal(p.cpf) ? 'Selecionar' : 'Importar' }}
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
