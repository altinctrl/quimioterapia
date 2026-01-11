<script lang="ts" setup>
import {onMounted, reactive, ref, watch} from 'vue'
import {useAppStore} from '@/stores/app'
import {Button} from '@/components/ui/button'
import {toast} from 'vue-sonner'

import AjustesFuncionamento from '@/components/ajustes/AjustesFuncionamento.vue'
import AjustesCapacidade from '@/components/ajustes/AjustesCapacidade.vue'
import AjustesTags from '@/components/ajustes/AjustesTags.vue'
import AjustesCargos from '@/components/ajustes/AjustesCargos.vue'
import AjustesFuncoes from '@/components/ajustes/AjustesFuncoes.vue'
import AjustesProtocolosLink from '@/components/ajustes/AjustesProtocolosLink.vue'

const appStore = useAppStore()

const carregando = ref(true)
const horarioAbertura = ref('')
const horarioFechamento = ref('')
const diasSelecionados = ref<number[]>([])
const tags = ref<string[]>([])
const cargos = ref<string[]>([])
const funcoes = ref<string[]>([])

const grupos = reactive({
  rapido: {vagas: 0 as number | string, duracao: ''},
  medio: {vagas: 0 as number | string, duracao: ''},
  longo: {vagas: 0 as number | string, duracao: ''}
})

const handleAdicionarTag = (novaTag: string) => {
  if (novaTag && !tags.value.includes(novaTag)) {
    tags.value.push(novaTag)
  }
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
      longo: {...grupos.longo, vagas: Number(grupos.longo.vagas)}
    },
    tags: [...tags.value],
    cargos: [...cargos.value],
    funcoes: [...funcoes.value]
  }
  try {
    await appStore.salvarConfiguracoes(payload)
    toast.success('Configurações salvas com sucesso!')
  } catch (error) {
    console.error(error)
    toast.error('Erro ao salvar configurações.')
  }
}

onMounted(async () => {
  try {
    carregando.value = true
    await appStore.fetchConfiguracoes()
  } catch (error) {
    console.error("Erro ao carregar configurações:", error)
    toast.error("Não foi possível carregar as configurações do servidor.")
  } finally {
    carregando.value = false
  }
})

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
        Object.assign(grupos.rapido, newVal.gruposInfusao.rapido)
        Object.assign(grupos.medio, newVal.gruposInfusao.medio)
        Object.assign(grupos.longo, newVal.gruposInfusao.longo)
      }
    },
    {deep: true, immediate: true}
)
</script>

<template>
  <div v-if="carregando" class="flex items-center justify-center h-64">
    <p class="text-muted-foreground animate-pulse">Carregando configurações...</p>
  </div>
  <div v-else class="max-w-7xl mx-auto space-y-8 pb-10">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Configurações</h1>
      </div>
      <Button class="shadow-sm" size="lg" @click="handleSalvar">Salvar Alterações</Button>
    </div>

    <div class="grid grid-cols-1 gap-8">

      <AjustesFuncionamento
          v-model:dias-selecionados="diasSelecionados"
          v-model:horario-abertura="horarioAbertura"
          v-model:horario-fechamento="horarioFechamento"
      />

      <AjustesCapacidade
          :grupos="grupos"
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

      <AjustesProtocolosLink/>

    </div>
  </div>
</template>