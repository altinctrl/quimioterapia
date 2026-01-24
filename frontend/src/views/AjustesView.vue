<script lang="ts" setup>
import {nextTick, onMounted, reactive, ref, watch} from 'vue'
import {onBeforeRouteLeave, useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Button} from '@/components/ui/button'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import {toast} from 'vue-sonner'
import {Save, X} from 'lucide-vue-next'

import AjustesFuncionamento from '@/components/ajustes/AjustesFuncionamento.vue'
import AjustesCapacidade from '@/components/ajustes/AjustesCapacidade.vue'
import AjustesTags from '@/components/ajustes/AjustesTags.vue'
import AjustesCargos from '@/components/ajustes/AjustesCargos.vue'
import AjustesFuncoes from '@/components/ajustes/AjustesFuncoes.vue'
import ProtocolosLista from '@/components/protocolos/ProtocolosLista.vue'
import ProtocolosDetalhes from '@/components/protocolos/ProtocolosDetalhes.vue'
import AjustesDiluentes from "@/components/ajustes/AjustesDiluentes.vue";
import ProtocolosImportModal from "@/components/modals/ProtocolosImportModal.vue";

const appStore = useAppStore()
const router = useRouter()
const route = useRoute()

const carregando = ref(true)
const activeTab = ref('administrativo')
const isDirty = ref(false)

const horarioAbertura = ref('')
const horarioFechamento = ref('')
const diasSelecionados = ref<number[]>([])
const tags = ref<string[]>([])
const cargos = ref<string[]>([])
const funcoes = ref<string[]>([])
const diluentes = ref<string[]>([])

const grupos = reactive({
  rapido: {vagas: 0 as number | string, duracao: ''},
  medio: {vagas: 0 as number | string, duracao: ''},
  longo: {vagas: 0 as number | string, duracao: ''},
  extra_longo: {vagas: 0 as number | string, duracao: ''}
})

const detailsOpen = ref(false)
const selectedProtocolo = ref<any>(null)
const importModalOpen = ref(false)
const listaParaImportar = ref<any[]>([])
const protocolosIgnoradosContador = ref(0)

onBeforeRouteLeave((_to, _from, next) => {
  if (isDirty.value) {
    const confirmacao = window.confirm("Existem alterações não salvas. Deseja sair e descartar as mudanças?")
    confirmacao ? next() : next(false)
  } else {
    next()
  }
})

const handleAdicionarTag = (novaTag: string) => {
  if (novaTag && !tags.value.includes(novaTag)) tags.value.push(novaTag)
}
const handleRemoverTag = (tag: string) => {
  tags.value = tags.value.filter(t => t !== tag)
}
const handleAdicionarCargo = (item: string) => {
  if (item && !cargos.value.includes(item)) cargos.value.push(item)
}
const handleRemoverCargo = (item: string) => {
  cargos.value = cargos.value.filter(i => i !== item)
}
const handleAdicionarFuncao = (item: string) => {
  if (item && !funcoes.value.includes(item)) funcoes.value.push(item)
}
const handleRemoverFuncao = (item: string) => {
  funcoes.value = funcoes.value.filter(i => i !== item)
}

const handleSalvar = async () => {
  const payload = {
    horarioAbertura: horarioAbertura.value,
    horarioFechamento: horarioFechamento.value,
    diasFuncionamento: [...diasSelecionados.value].sort((a, b) => a - b),
    gruposInfusao: {
      rapido: {...grupos.rapido, vagas: Number(grupos.rapido.vagas)},
      medio: {...grupos.medio, vagas: Number(grupos.medio.vagas)},
      longo: {...grupos.longo, vagas: Number(grupos.longo.vagas)},
      extra_longo: {...grupos.extra_longo, vagas: Number(grupos.extra_longo.vagas)}
    },
    tags: [...tags.value],
    cargos: [...cargos.value],
    funcoes: [...funcoes.value],
    diluentes: [...diluentes.value]
  }
  try {
    await appStore.salvarConfiguracoes(payload)
    toast.success('Configurações salvas com sucesso!')
    isDirty.value = false
  } catch (error) {
    console.error(error)
    toast.error('Erro ao salvar configurações.')
  }
}

const handleDesfazer = async () => {
  const dadosSalvos = appStore.parametros
  if (dadosSalvos.horarioAbertura) {
    horarioAbertura.value = dadosSalvos.horarioAbertura
    horarioFechamento.value = dadosSalvos.horarioFechamento
    diasSelecionados.value = [...dadosSalvos.diasFuncionamento]
    tags.value = [...(dadosSalvos.tags || [])]
    cargos.value = [...(dadosSalvos.cargos || [])]
    funcoes.value = [...(dadosSalvos.funcoes || [])]
    diluentes.value = [...(dadosSalvos.diluentes || [])]
    Object.assign(grupos.rapido, dadosSalvos.gruposInfusao.rapido)
    Object.assign(grupos.medio, dadosSalvos.gruposInfusao.medio)
    Object.assign(grupos.longo, dadosSalvos.gruposInfusao.longo)
    Object.assign(grupos.extra_longo, dadosSalvos.gruposInfusao.extra_longo)
    await nextTick()
    isDirty.value = false
  }
}

const handleNovoProtocolo = () => {
  router.push({name: 'NovoProtocolo'})
}

const handleImportarRequest = (lista: any[], ignoredCount: number) => {
  listaParaImportar.value = lista
  protocolosIgnoradosContador.value = ignoredCount
  importModalOpen.value = true
}

const handleConfirmarImportacao = async () => {
  try {
    const lista = listaParaImportar.value
    await appStore.importarProtocolos(lista)
    toast.success(`${lista.length} protocolos importados com sucesso!`)
    await appStore.fetchProtocolos()
    listaParaImportar.value = []
  } catch (error) {
    console.error(error)
    toast.error("Erro ao processar importação no servidor.")
  }
}

const handleEditProtocolo = (p: any) => {
  router.push({name: 'EditarProtocolo', params: {id: p.id}})
}

const handleViewDetails = (p: any) => {
  selectedProtocolo.value = p
  detailsOpen.value = true
}

const handleToggleStatusProtocolo = async (p: any) => {
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
    toast.error('Erro ao alterar status do protocolo')
  }
}

onMounted(async () => {
  try {
    carregando.value = true
    if (route.query.tab) {
      activeTab.value = route.query.tab as string
    }
    await Promise.all([
      appStore.fetchConfiguracoes(),
      appStore.fetchProtocolos()
    ])
  } catch (error) {
    console.error("Erro ao carregar dados:", error)
    toast.error("Não foi possível carregar as informações.")
  } finally {
    carregando.value = false
  }
})

watch(
    [horarioAbertura, horarioFechamento, diasSelecionados, tags, cargos, funcoes, grupos, diluentes],
    () => {
      if (!carregando.value) {
        isDirty.value = true
      }
    },
    {deep: true}
)

watch(
    () => appStore.parametros,
    (newVal) => {
      if (newVal.horarioAbertura) {
        horarioAbertura.value = newVal.horarioAbertura
        horarioFechamento.value = newVal.horarioFechamento
        diasSelecionados.value = [...newVal.diasFuncionamento]
        tags.value = [...(newVal.tags || [])]
        cargos.value = [...(newVal.cargos || [])]
        funcoes.value = [...(newVal.funcoes || [])]
        diluentes.value = [...(newVal.diluentes || [])]
        Object.assign(grupos.rapido, newVal.gruposInfusao.rapido)
        Object.assign(grupos.medio, newVal.gruposInfusao.medio)
        Object.assign(grupos.longo, newVal.gruposInfusao.longo)
        Object.assign(grupos.extra_longo, newVal.gruposInfusao.extra_longo)
        nextTick(() => {
          isDirty.value = false
        })
      }
    },
    {deep: true, immediate: true}
)
</script>

<template>
  <div v-if="carregando" class="flex items-center justify-center h-64">
    <p class="text-muted-foreground animate-pulse">Carregando...</p>
  </div>
  <div v-else class="max-w-5xl mx-auto space-y-8 pb-10">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Configurações</h1>
      </div>

      <div v-if="isDirty" class="flex items-center justify-end gap-3">
        <Button
            class="text-muted-foreground"
            variant="ghost"
            @click="handleDesfazer"
        >
          <X class="h-4 w-4 mr-1"/>
          Cancelar
        </Button>

        <Button @click="handleSalvar">
          <Save class="h-4 w-4 mr-1"/>
          Salvar
        </Button>
      </div>
    </div>

    <Tabs v-model="activeTab" class="w-full">
      <TabsList>
        <TabsTrigger value="administrativo">Administrativo</TabsTrigger>
        <TabsTrigger value="vagas">Vagas</TabsTrigger>
        <TabsTrigger value="diluicao">Diluição</TabsTrigger>
        <TabsTrigger value="protocolos">Protocolos</TabsTrigger>
      </TabsList>

      <TabsContent class="space-y-8 mt-6" value="administrativo">
        <AjustesFuncionamento
            v-model:dias-selecionados="diasSelecionados"
            v-model:horario-abertura="horarioAbertura"
            v-model:horario-fechamento="horarioFechamento"
        />
        <AjustesTags
            :tags="tags"
            @adicionar="handleAdicionarTag"
            @remover="handleRemoverTag"
        />
        <AjustesCargos
            :cargos="cargos"
            @adicionar="handleAdicionarCargo"
            @remover="handleRemoverCargo"
        />
        <AjustesFuncoes
            :funcoes="funcoes"
            @adicionar="handleAdicionarFuncao"
            @remover="handleRemoverFuncao"
        />
      </TabsContent>

      <TabsContent class="space-y-8 mt-6" value="vagas">
        <AjustesCapacidade :grupos="grupos"/>
      </TabsContent>

      <TabsContent class="space-y-6 mt-6" value="protocolos">
        <ProtocolosLista
            :protocolos="appStore.protocolos"
            @criar="handleNovoProtocolo"
            @details="handleViewDetails"
            @edit="handleEditProtocolo"
            @importar="handleImportarRequest"
            @toggle-status="handleToggleStatusProtocolo"
        />
      </TabsContent>

      <TabsContent class="space-y-8 mt-6" value="diluicao">
        <AjustesDiluentes
            v-model:diluentes="diluentes"
        />
      </TabsContent>
    </Tabs>

    <ProtocolosImportModal
        v-model:open="importModalOpen"
        :ignored="protocolosIgnoradosContador"
        :protocolos="listaParaImportar"
        @confirmar="handleConfirmarImportacao"
    />

    <ProtocolosDetalhes
        v-model:open="detailsOpen"
        :protocolo="selectedProtocolo"
    />
  </div>
</template>
