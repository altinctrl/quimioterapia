<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useAppStore} from '@/stores/app'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Badge} from '@/components/ui/badge'
import {Check, Search} from 'lucide-vue-next'
import {Dialog, DialogContent, DialogHeader, DialogTitle,} from '@/components/ui/dialog'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import type {Paciente, PacienteImport} from '@/types'
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

const LIMITE_ITENS_LISTA = 100

const {errors, defineField, handleSubmit, resetForm} = useForm({
  validationSchema: buscaPacienteFormSchema,
  initialValues: {termo: ''}
})

const [termoExterno, termoProps] = defineField('termo')
const resultadosExternos = ref<PacienteImport[]>([])
const buscandoExterno = ref(false)
const buscaRealizada = ref(false)

const resultadosLimitados = computed(() => {
  return resultadosExternos.value.slice(0, LIMITE_ITENS_LISTA)
})

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    resetForm()
    resultadosExternos.value = []
    buscaRealizada.value = false
  }
})

const handleBuscarExterno = handleSubmit(async (values) => {
  buscandoExterno.value = true
  buscaRealizada.value = true
  try {
    const res = await api.get('/api/pacientes/externo/buscar', {
      params: {termo: values.termo, limit: LIMITE_ITENS_LISTA+1}
    })
    resultadosExternos.value = res.data
  } catch (e) {
    toast.error("Erro ao buscar no sistema externo")
  } finally {
    buscandoExterno.value = false
  }
})

const handleImportarPaciente = async (pacienteExterno: PacienteImport) => {
  try {
    if (pacienteExterno.id) {
      const pacienteCompleto = await appStore.carregarPaciente(pacienteExterno.id.toString())
      if (pacienteCompleto) {
        emit('paciente-importado', pacienteCompleto)
        emit('update:open', false)
      }
    } else {
      const detalhesCompletos = await api.get(`/api/pacientes/externo/${pacienteExterno.id}`)
      const novoPaciente = await appStore.adicionarPaciente(detalhesCompletos.data)
      toast.success(`Paciente ${pacienteExterno.nome} importado com sucesso!`)
      emit('paciente-importado', novoPaciente)
      emit('update:open', false)
    }
  } catch (e) {
    console.error(e)
    toast.error("Erro ao importar paciente")
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-3xl max-h-[90vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>Importar Paciente do AGHU</DialogTitle>
      </DialogHeader>

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

      <div class="flex-1 overflow-y-auto min-h-0 border rounded-md scrollbar-thin scrollbar-thumb-gray-200">
        <Table>
          <TableHeader>
            <TableRow class="hover:bg-transparent">
              <TableHead class="pl-4">Nome</TableHead>
              <TableHead>CPF</TableHead>
              <TableHead>Nascimento</TableHead>
              <TableHead class="text-center">Ação</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-if="!buscaRealizada && !buscandoExterno">
              <TableCell class="text-center text-muted-foreground py-10" colspan="4">
                <div class="flex flex-col items-center gap-2">
                  <Search class="h-8 w-8 opacity-20"/>
                  <p>Digite o nome ou CPF para iniciar a pesquisa.</p>
                </div>
              </TableCell>
            </TableRow>

            <TableRow v-if="buscandoExterno">
              <TableCell class="text-center text-muted-foreground py-10" colspan="4">
                <div class="flex items-center justify-center gap-2">
                  <div class="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
                  Pesquisando pacientes no AGHU...
                </div>
              </TableCell>
            </TableRow>

            <TableRow v-if="buscaRealizada && !buscandoExterno && resultadosExternos.length === 0">
              <TableCell class="text-center py-10 bg-slate-50/30" colspan="4">
                <div class="flex flex-col items-center gap-1">
                  <p class="text-sm font-semibold text-slate-700">Nenhum paciente encontrado</p>
                  <p class="text-xs text-muted-foreground">Verifique se os dados estão corretos ou tente um termo diferente.</p>
                </div>
              </TableCell>
            </TableRow>

            <TableRow
                v-for="p in resultadosLimitados"
                :key="p.registro"
                :class="p.id ? 'bg-blue-50/50' : ''"
            >
              <TableCell>
                <div class="flex items-center gap-2 pl-2">
                  {{ p.nome }}
                  <Badge
                      v-if="p.id"
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
                    :variant="p.id ? 'secondary' : 'outline'"
                    size="sm"
                    @click="handleImportarPaciente(p)"
                >
                  {{ p.id ? 'Selecionar' : 'Importar' }}
                </Button>
              </TableCell>
            </TableRow>

            <TableRow v-if="resultadosExternos.length >= LIMITE_ITENS_LISTA">
              <TableCell class="py-6 bg-slate-50/50" colspan="4">
                <div class="flex flex-col items-center justify-center text-center space-y-1">
                  <p class="text-sm font-medium text-amber-700">
                    A pesquisa retornou muitos resultados.
                  </p>
                  <p class="text-xs text-muted-foreground">
                    Exibindo apenas os primeiros {{ LIMITE_ITENS_LISTA }} registros.<br>
                    Tente <strong>refinar sua busca</strong> utilizando o nome completo ou CPF.
                  </p>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </DialogContent>
  </Dialog>
</template>
