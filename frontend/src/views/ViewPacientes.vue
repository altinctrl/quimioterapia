<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/storeGeral.ts'
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Search, UserPlus} from 'lucide-vue-next'
import PacientesTabela from '@/components/pacientes/PacientesTabela.vue'
import PacientesModalImportacao from '@/components/pacientes/PacientesModalImportacao.vue'
import PacientesControles from '@/components/pacientes/PacientesControles.vue'
import {usePacientesLista} from '@/composables/usePacientesLista.ts'
import {usePacienteFormulario} from '@/composables/usePacienteFormulario.ts'

const router = useRouter()
const appStore = useAppStore()

const {
  page,
  filtros,
  termoBusca,
  loading,
  totalPages,
  carregarDados,
  handleBuscaInput,
  resetFiltros
} = usePacientesLista()

const {podeEditar} = usePacienteFormulario()

const dialogNovoPaciente = ref(false)

onMounted(async () => {
  await carregarDados()
})

const handleSelecionarPaciente = (paciente: any) => {
  router.push({name: 'Prontuario', params: {id: paciente.id}})
}

const handlePacienteImportado = (paciente: any) => {
  handleSelecionarPaciente(paciente)
}
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Pacientes</h1>

    <div class="space-y-6">
      <Card>
        <CardContent class="pt-6">
          <div class="flex gap-3">
            <div class="flex-1 relative">
              <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"/>
              <Input
                  :model-value="termoBusca"
                  class="pl-10"
                  placeholder="Buscar por nome, CPF ou prontuário..."
                  @input="handleBuscaInput"
              />
            </div>

            <div v-if="podeEditar">
              <Button class="flex items-center gap-2" @click="dialogNovoPaciente = true">
                <UserPlus class="h-4 w-4"/>
                Novo Paciente
              </Button>

              <PacientesModalImportacao
                  v-model:open="dialogNovoPaciente"
                  @paciente-importado="handlePacienteImportado"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <PacientesControles
            v-model="filtros"
            v-model:page="page"
            :totalPacientes="appStore.totalPacientes"
            :totalPages="totalPages"
            class="px-6 pt-6 pb-2"
            @reset="resetFiltros"
        />

        <CardContent>
          <PacientesTabela
              :loading="loading"
              :pacientes="appStore.pacientes"
              @select="handleSelecionarPaciente"
          />
        </CardContent>
      </Card>
    </div>
  </div>
</template>
