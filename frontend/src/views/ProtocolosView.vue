<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Button} from '@/components/ui/button'
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {ArrowLeft, Plus} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import ProtocolosLista from '@/components/protocolos/ProtocolosLista.vue'
import ProtocolosForm from '@/components/protocolos/ProtocolosForm.vue'
import ProtocolosDetalhes from '@/components/protocolos/ProtocolosDetalhes.vue'
import {ScrollArea} from "@/components/ui/scroll-area";

const router = useRouter()
const appStore = useAppStore()

onMounted(() => {
  appStore.fetchProtocolos()
})

const dialogOpen = ref(false)
const detailsOpen = ref(false)
const editMode = ref(false)
const selectedProtocolo = ref<any>(null)

const getInitialFormState = () => ({
  nome: '',
  indicacao: '',
  fase: '',
  linha: null as number | null,
  tempoTotalMinutos: 0,
  duracaoCicloDias: 21,
  totalCiclos: 0,
  observacoes: '',
  precaucoes: '',
  ativo: true,
  diasSemanaPermitidos: [] as number[],
  templatesCiclo: [
    {
      idTemplate: 'padrao',
      aplicavelAosCiclos: '',
      blocos: []
    }
  ]
})

const formData = ref(getInitialFormState())

const handleAdd = () => {
  formData.value = getInitialFormState()
  selectedProtocolo.value = null
  editMode.value = false
  dialogOpen.value = true
}

const handleEdit = (p: any) => {
  selectedProtocolo.value = p
  const clone = JSON.parse(JSON.stringify(p))
  if (!clone.templatesCiclo || clone.templatesCiclo.length === 0) {
    clone.templatesCiclo = [{idTemplate: 'padrao', blocos: []}]
  }

  formData.value = {
    nome: clone.nome,
    indicacao: clone.indicacao,
    fase: clone.fase,
    linha: clone.linha,
    tempoTotalMinutos: clone.tempoTotalMinutos || clone.duracao || 0,
    duracaoCicloDias: clone.duracaoCicloDias || 21,
    totalCiclos: clone.totalCiclos || 0,
    observacoes: clone.observacoes || '',
    precaucoes: clone.precaucoes || '',
    ativo: clone.ativo,
    diasSemanaPermitidos: Array.isArray(clone.diasSemanaPermitidos) ? [...clone.diasSemanaPermitidos] : [],
    templatesCiclo: clone.templatesCiclo
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
  try {
    const data = JSON.parse(JSON.stringify(formData.value))
    if (!data.fase || data.fase === '' || data.fase === 'none') {
      data.fase = null
    }

    if (data.templatesCiclo) {
      data.templatesCiclo.forEach((template: any) => {
        if (template.blocos) {
          template.blocos.forEach((bloco: any) => {
            if (bloco.itens) {
              bloco.itens = bloco.itens.map((item: any) => {
                if (item.tipo === 'medicamento_unico') {
                  const {labelGrupo, opcoes, ...rest} = item
                  return rest
                } else if (item.tipo === 'grupo_alternativas') {
                  const {dados, ...rest} = item
                  return rest
                }
                return item
              })
            }
          })
        }
      })
    }

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
      <DialogContent class="max-w-4xl max-h-[90vh] flex flex-col p-0 gap-0">
        <DialogHeader class="p-6 pb-4 border-b">
          <DialogTitle class="text-xl font-bold text-gray-900 flex items-center gap-3">
            {{ editMode ? 'Editar' : 'Novo' }} Protocolo
          </DialogTitle>
        </DialogHeader>

        <ScrollArea class="h-[calc(90vh-140px)] w-full">
          <ProtocolosForm v-model="formData" class="p-6"/>
        </ScrollArea>

        <DialogFooter class="p-4 border-t bg-gray-50">
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
