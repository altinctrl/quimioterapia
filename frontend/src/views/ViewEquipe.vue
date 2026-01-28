<script lang="ts" setup>
import {onMounted, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {endOfMonth, format, startOfMonth} from 'date-fns'
import {useEquipeStore} from '@/stores/storeEquipe.ts'
import {useConfiguracaoStore} from '@/stores/storeAjustes.ts'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import EquipeEscala from '@/components/equipe/EquipeEscala.vue'
import EquipeLista from '@/components/equipe/EquipeLista.vue'
import EquipeAusencias from '@/components/equipe/EquipeAusencias.vue'
import {toast} from 'vue-sonner'
import {AusenciaProfissional, EscalaPlantao, Profissional} from "@/types/typesEquipe.ts";

const equipeStore = useEquipeStore()
const configStore = useConfiguracaoStore()

const {profissionais, escalaDia, ausencias} = storeToRefs(equipeStore)
const dataEscala = ref<Date>(new Date())
const mesAusencia = ref<Date>(new Date())

onMounted(async () => {
  await Promise.all([
    configStore.fetchConfiguracoes(),
    equipeStore.fetchProfissionais(false),
    carregarEscala(),
    carregarAusencias()
  ])
})

async function carregarEscala() {
  await equipeStore.fetchEscalaDia(format(dataEscala.value, 'yyyy-MM-dd'))
}

async function carregarAusencias() {
  const start = format(startOfMonth(mesAusencia.value), 'yyyy-MM-dd')
  const end = format(endOfMonth(mesAusencia.value), 'yyyy-MM-dd')
  await equipeStore.fetchAusencias(start, end)
}

watch(dataEscala, carregarEscala)
watch(mesAusencia, carregarAusencias)

async function handleCriarProfissional(dados: Partial<Profissional>) {
  try {
    await equipeStore.criarProfissional(dados)
    toast.success('Profissional cadastrado')
  } catch (e: any) {
    toast.error(e.message)
  }
}

async function handleAtualizarProfissional(dados: Partial<Profissional>) {
  try {
    if (!dados.username) return
    await equipeStore.atualizarProfissional(dados.username, dados)
    toast.success('Profissional atualizado')
  } catch (e: any) {
    toast.error(e.message)
  }
}

async function handleAdicionarEscala(dados: Partial<EscalaPlantao>) {
  try {
    await equipeStore.adicionarEscala(dados)
    toast.success('Adicionado à escala')
  } catch (e: any) {
    toast.error(e.message)
  }
}

async function handleRemoverEscala(id: string) {
  try {
    await equipeStore.removerEscala(id)
    toast.success('Removido da escala')
  } catch (e: any) {
    toast.error('Erro ao remover')
  }
}

async function handleRegistrarAusencia(dados: Partial<AusenciaProfissional>) {
  try {
    await equipeStore.registrarAusencia(dados)
    toast.success('Ausência registrada')
    await carregarAusencias()
  } catch (e: any) {
    toast.error(e.message)
  }
}

async function handleRemoverAusencia(id: string) {
  try {
    await equipeStore.removerAusencia(id)
    toast.success('Ausência removida')
  } catch (e: any) {
    toast.error('Erro ao remover')
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div>
      <h1 class="text-3xl font-bold tracking-tight">Gestão de Equipe</h1>
    </div>

    <Tabs class="space-y-4" default-value="escala">
      <TabsList>
        <TabsTrigger value="escala">Escala</TabsTrigger>
        <TabsTrigger value="ausencias">Ausências</TabsTrigger>
        <TabsTrigger value="profissionais">Cadastro</TabsTrigger>
      </TabsList>

      <TabsContent class="space-y-4" value="escala">
        <EquipeEscala
            v-model:data="dataEscala"
            :escala="escalaDia"
            :funcoes="configStore.parametros.funcoes"
            :profissionais="profissionais"
            @adicionar="handleAdicionarEscala"
            @remover="handleRemoverEscala"
        />
      </TabsContent>

      <TabsContent class="space-y-4" value="ausencias">
        <EquipeAusencias
            v-model:mesReferencia="mesAusencia"
            :ausencias="ausencias"
            :profissionais="profissionais"
            @registrar="handleRegistrarAusencia"
            @remover="handleRemoverAusencia"
        />
      </TabsContent>

      <TabsContent class="space-y-4" value="profissionais">
        <EquipeLista
            :cargos="configStore.parametros.cargos"
            :profissionais="profissionais"
            @atualizar="handleAtualizarProfissional"
            @criar="handleCriarProfissional"
        />
      </TabsContent>
    </Tabs>
  </div>
</template>
