<script lang="ts" setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Button} from '@/components/ui/button'
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {ArrowLeft, Plus} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import type {ItemProtocolo} from '@/types'
import ProtocolosLista from '@/components/protocolos/ProtocolosLista.vue'
import ProtocolosForm from '@/components/protocolos/ProtocolosForm.vue'
import ProtocolosDetalhes from '@/components/protocolos/ProtocolosDetalhes.vue'

const router = useRouter()
const appStore = useAppStore()

const dialogOpen = ref(false)
const detailsOpen = ref(false)
const editMode = ref(false)
const selectedProtocolo = ref<any>(null)

const formData = ref({
  nome: '',
  descricao: '',
  indicacao: '',
  duracao: 0,
  frequencia: '',
  numeroCiclos: 0,
  medicamentos: [] as ItemProtocolo[],
  preMedicacoes: [] as ItemProtocolo[],
  posMedicacoes: [] as ItemProtocolo[],
  observacoes: '',
  precaucoes: '',
  ativo: true,
  diasSemanaPermitidos: [] as number[]
})

const inferirGrupoInfusao = (duracao: number): 'rapido' | 'medio' | 'longo' => {
  if (duracao < 120) return 'rapido'
  if (duracao <= 240) return 'medio'
  return 'longo'
}

const resetForm = () => {
  formData.value = {
    nome: '', descricao: '', indicacao: '', duracao: 0,
    frequencia: '', numeroCiclos: 0,
    medicamentos: [],
    preMedicacoes: [],
    posMedicacoes: [],
    observacoes: '', precaucoes: '', ativo: true,
    diasSemanaPermitidos: []
  }
  selectedProtocolo.value = null
  editMode.value = false
}

const handleAdd = () => {
  resetForm()
  dialogOpen.value = true
}

const handleEdit = (p: any) => {
  selectedProtocolo.value = p
  formData.value = {
    nome: p.nome,
    descricao: p.descricao || '',
    indicacao: p.indicacao,
    duracao: p.duracao,
    frequencia: p.frequencia,
    numeroCiclos: p.numeroCiclos,
    medicamentos: p.medicamentos ? JSON.parse(JSON.stringify(p.medicamentos)) : [],
    preMedicacoes: p.preMedicacoes ? JSON.parse(JSON.stringify(p.preMedicacoes)) : [],
    posMedicacoes: p.posMedicacoes ? JSON.parse(JSON.stringify(p.posMedicacoes)) : [],
    observacoes: p.observacoes || '',
    precaucoes: p.precaucoes || '',
    ativo: p.ativo,
    diasSemanaPermitidos: Array.isArray(p.diasSemanaPermitidos) ? [...p.diasSemanaPermitidos] : []
  }
  editMode.value = true
  dialogOpen.value = true
}

const handleViewDetails = (p: any) => {
  selectedProtocolo.value = p
  detailsOpen.value = true
}

const handleToggleStatus = async (p: any) => {
  try {
    if (p.ativo) {
      await appStore.desativarProtocolo(p.id)
      toast.success('Protocolo desativado')
    } else {
      await appStore.atualizarProtocolo(p.id, {ativo: true})
      toast.success('Protocolo reativado')
    }
  } catch (error) {
    console.error(error)
  }
}

const handleSubmit = async () => {
  const grupoInfusao = inferirGrupoInfusao(formData.value.duracao)
  const data = {...formData.value, grupoInfusao}

  try {
    if (editMode.value && selectedProtocolo.value) {
      await appStore.atualizarProtocolo(selectedProtocolo.value.id, data)
      toast.success('Protocolo atualizado')
    } else {
      await appStore.adicionarProtocolo(data)
      toast.success('Protocolo criado')
    }
    dialogOpen.value = false
  } catch (error) {
    console.error(error)
  }
}
</script>

<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button size="icon" variant="outline" @click="router.back()">
          <ArrowLeft class="h-4 w-4"/>
        </Button>
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Protocolos</h1>
        </div>
      </div>
      <Button @click="handleAdd">
        <Plus class="h-4 w-4 mr-2"/>
        Novo Protocolo
      </Button>
    </div>

    <ProtocolosLista
        :protocolos="appStore.protocolos"
        @details="handleViewDetails"
        @edit="handleEdit"
        @toggle-status="handleToggleStatus"
    />

    <Dialog v-model:open="dialogOpen">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{{ editMode ? 'Editar' : 'Novo' }} Protocolo</DialogTitle>
        </DialogHeader>

        <ProtocolosForm v-model="formData"/>

        <DialogFooter>
          <Button variant="outline" @click="dialogOpen = false">Cancelar</Button>
          <Button @click="handleSubmit">Salvar Protocolo</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <ProtocolosDetalhes
        v-model:open="detailsOpen"
        :protocolo="selectedProtocolo"
    />
  </div>
</template>