<script lang="ts" setup>
import {onMounted} from 'vue'
import {storeToRefs} from 'pinia'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import {useEquipeStore} from '@/stores/storeEquipe'
import {useConfiguracaoStore} from '@/stores/storeAjustes'
import {useEquipeProfissionais} from '@/composables/useEquipeProfissionais.ts'
import {useEquipeEscala} from '@/composables/useEquipeEscala.ts'
import {useEquipeAusencias} from '@/composables/useEquipeAusencias.ts'
import EquipeEscala from '@/components/equipe/EquipeEscala.vue'
import EquipeLista from '@/components/equipe/EquipeLista.vue'
import EquipeAusencias from '@/components/equipe/EquipeAusencias.vue'

const equipeStore = useEquipeStore()
const configStore = useConfiguracaoStore()
const {profissionais} = storeToRefs(equipeStore)

onMounted(async () => {
  await Promise.all([
    configStore.fetchConfiguracoes(),
    equipeStore.fetchProfissionais(false)
  ])
})

const logicaProfissionais = useEquipeProfissionais()
const logicaEscala = useEquipeEscala(configStore.parametros.funcoes)
const logicaAusencias = useEquipeAusencias()
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
            v-model:data="logicaEscala.dataSelecionada.value"
            :escala="logicaEscala.escalaOrdenada.value"
            :form-state="logicaEscala.formState"
            :funcoes="configStore.parametros.funcoes"
            :profissionais="logicaEscala.profissionaisDisponiveis.value"
            @adicionar="logicaEscala.adicionarEscala"
            @remover="logicaEscala.removerEscala"
            @prev-day="logicaEscala.mudarDia(-1)"
            @next-day="logicaEscala.mudarDia(1)"
        />
      </TabsContent>

      <TabsContent class="space-y-4" value="ausencias">
        <EquipeAusencias
            v-model:mes="logicaAusencias.mesReferencia.value"
            v-model:modal-open="logicaAusencias.isModalOpen.value"
            :ausencias="logicaAusencias.ausenciasOrdenadas.value"
            :form-state="logicaAusencias.formState"
            :profissionais="profissionais"
            @remover="logicaAusencias.removerAusencia"
            @salvar="logicaAusencias.registrarAusencia"
            @abrir-modal="logicaAusencias.abrirModalNovo"
            @prev-month="logicaAusencias.mudarMes(-1)"
            @next-month="logicaAusencias.mudarMes(1)"
        />
      </TabsContent>

      <TabsContent class="space-y-4" value="profissionais">
        <EquipeLista
            v-model:modal-open="logicaProfissionais.isModalOpen.value"
            :cargos="configStore.parametros.cargos"
            :filtros="logicaProfissionais.filtros"
            :form-state="logicaProfissionais.formState"
            :is-editing="logicaProfissionais.isEditing.value"
            :profissionais="logicaProfissionais.profissionaisFiltrados.value"
            @editar="logicaProfissionais.prepararEdicao"
            @novo="() => logicaProfissionais.prepararNovoCadastro(configStore.parametros.cargos[0])"
            @salvar="logicaProfissionais.salvarProfissional"
        />
      </TabsContent>
    </Tabs>
  </div>
</template>
