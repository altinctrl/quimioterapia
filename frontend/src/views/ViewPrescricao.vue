<script lang="ts" setup>
import {onMounted} from 'vue'
import {useRouter} from 'vue-router'
import {Button} from '@/components/ui/button'
import {Label} from '@/components/ui/label'
import {Activity, ArrowLeft, Pill, User} from 'lucide-vue-next'
import {toast} from 'vue-sonner'

import PrescricaoIdentificacao from '@/components/prescricao/PrescricaoIdentificacao.vue'
import PrescricaoProtocolo from '@/components/prescricao/PrescricaoProtocolo.vue'
import PrescricaoRodape from '@/components/prescricao/PrescricaoRodape.vue'
import PrescricaoBlocos from '@/components/prescricao/PrescricaoBlocos.vue'
import {Card} from "@/components/ui/card";
import {usePrescricaoFormulario} from '@/composables/usePrescricaoFormulario.ts'
import {useAppStore} from "@/stores/storeGeral.ts";

const router = useRouter()
const appStore = useAppStore()

const {
  values,
  errors,
  setFieldValue,
  fields,
  pacienteSelecionadoObj,
  ultimaPrescricao,
  templatesDisponiveis,
  templateSelecionadoId,
  prescricaoConcluida,
  prescricaoGeradaId,
  init,
  salvar,
  repetirUltimaPrescricao
} = usePrescricaoFormulario()

onMounted(() => {
  init()
})

const handleBaixar = async () => {
  if (!prescricaoGeradaId.value) {
    toast.error("É necessário confirmar a prescrição antes de baixar.");
    return;
  }
  await appStore.baixarPrescricao(prescricaoGeradaId.value);
};
</script>

<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-20">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button size="icon" variant="outline" @click="router.back()">
          <ArrowLeft class="h-4 w-4"/>
        </Button>
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Nova Prescrição</h1>
        </div>
      </div>
    </div>

    <div class="pt-6 space-y-4 animate-in slide-in-from-bottom-4 duration-500">
      <div class="flex items-center gap-2">
        <User/>
        <h2 class="text-xl font-semibold text-gray-800">Identificação e Dados Antropométricos</h2>
      </div>

      <PrescricaoIdentificacao
          v-model:altura="fields.altura.value"
          v-model:creatinina="fields.creatinina.value"
          v-model:diagnostico="fields.diagnostico.value"
          v-model:errors="errors"
          v-model:pacienteId="fields.pacienteId.value"
          v-model:peso="fields.peso.value"
          :sc="fields.sc.value"
          :sexo="pacienteSelecionadoObj?.sexo || ''"
      />
    </div>

    <div class="pt-6 space-y-4 animate-in slide-in-from-bottom-4 duration-500">
      <div class="flex items-center gap-2">
        <Activity/>
        <h2 class="text-xl font-semibold text-gray-800">Protocolo e Ciclo</h2>
      </div>

      <PrescricaoProtocolo
          v-model:errors="errors"
          v-model:numeroCiclo="fields.numeroCiclo.value"
          v-model:protocolo="fields.protocoloNome.value"
          :ultima-prescricao="ultimaPrescricao"
          @repetir="repetirUltimaPrescricao"
      />
    </div>

    <div v-if="values.blocos && values.blocos.length > 0"
         class="pt-6 space-y-4 animate-in slide-in-from-bottom-4 duration-500"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Pill/>
          <h2 class="text-xl font-semibold text-gray-800">Medicações</h2>
        </div>
      </div>

      <div class="flex flex-col gap-1 mb-2">
        <Label class="text-sm font-semibold text-gray-700">Selecione a Variante do Protocolo</Label>
      </div>

      <Card v-if="templatesDisponiveis.length > 1" class="p-4 flex items-center gap-1 mb-4 w-full">
        <div
            class="flex items-center gap-2 overflow-x-auto flex-1 px-1 w-0"
            style="scrollbar-width: thin; -ms-overflow-style: -ms-autohiding-scrollbar;"
        >
          <Button
              v-for="(template, idx) in templatesDisponiveis"
              :key="idx"
              :variant="templateSelecionadoId === template.idTemplate ? 'default' : 'outline'"
              class="h-8 text-sm whitespace-nowrap flex-shrink-0"
              @click="templateSelecionadoId = template.idTemplate"
          >
            {{ template.idTemplate || `Template ${idx + 1}` }}
          </Button>
        </div>
      </Card>

      <PrescricaoBlocos
          v-model:errors="errors"
          :blocos="values.blocos"
          :dados-paciente="{
             peso: values.peso,
             altura: values.altura,
             sc: values.sc,
             creatinina: values.creatinina,
             sexo: pacienteSelecionadoObj?.sexo,
             idade: pacienteSelecionadoObj?.idade
          }"
          @update:blocos="(novosBlocos) => setFieldValue('blocos', novosBlocos)"
      />
    </div>

    <div v-else-if="fields.protocoloNome.value"
         class="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border border-dashed"
    >
      Carregando estrutura do protocolo...
    </div>

    <PrescricaoRodape
        :concluida="prescricaoConcluida"
        @baixar="handleBaixar"
        @confirmar="salvar"
    />
  </div>
</template>
