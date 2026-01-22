<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {toast} from 'vue-sonner'
import ProtocolosForm from '@/components/protocolos/ProtocolosForm.vue'
import {Button} from "@/components/ui/button";
import {Save} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const loading = ref(true)
const isEditMode = computed(() => !!route.params.id)

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
      idTemplate: 'Padrão',
      aplicavelAosCiclos: '',
      blocos: []
    }
  ]
})

const formData = ref(getInitialFormState())

onMounted(async () => {
  try {
    loading.value = true
    await appStore.fetchProtocolos()

    if (isEditMode.value) {
      const id = route.params.id
      const protocolo = appStore.protocolos.find((p: any) => p.id === id)

      if (protocolo) {
        const clone = JSON.parse(JSON.stringify(protocolo))
        if (!clone.templatesCiclo || clone.templatesCiclo.length === 0) {
          clone.templatesCiclo = [{idTemplate: 'Padrão', blocos: []}]
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
      } else {
        toast.error("Protocolo não encontrado")
        await router.push({name: 'Ajustes', query: {tab: 'protocolos'}})
      }
    }
  } catch (error) {
    console.error(error)
    toast.error("Erro ao carregar dados do protocolo")
  } finally {
    loading.value = false
  }
})

const handleCancel = () => {
  router.push({name: 'Ajustes', query: {tab: 'protocolos'}})
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

    if (isEditMode.value) {
      await appStore.atualizarProtocolo(route.params.id as string, data)
      toast.success('Protocolo atualizado com sucesso')
    } else {
      await appStore.adicionarProtocolo(data)
      toast.success('Protocolo criado com sucesso')
    }

    await router.push({name: 'Ajustes', query: {tab: 'protocolos'}})
  } catch (error) {
    console.error(error)
    toast.error('Erro ao salvar protocolo')
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    <div v-if="loading" class="flex justify-center py-12">
      <p class="text-muted-foreground animate-pulse">Carregando dados...</p>
    </div>

    <template v-else>
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">
            {{ isEditMode ? 'Editar Protocolo' : 'Novo Protocolo' }}
          </h1>
        </div>

        <div class="flex items-center gap-3">
          <Button variant="outline" @click="handleCancel">
            Cancelar
          </Button>
          <Button class="flex items-center gap-2" @click="handleSubmit">
            <Save class="h-4 w-4"/>
            Salvar
          </Button>
        </div>
      </div>

      <ProtocolosForm
          v-model="formData"
      />
    </template>
  </div>
</template>
