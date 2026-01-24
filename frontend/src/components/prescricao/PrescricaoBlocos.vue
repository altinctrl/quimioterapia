<script lang="ts" setup>
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {AlertCircle, Info} from 'lucide-vue-next'
import PrescricaoItemRow from './PrescricaoItemRow.vue'
import {Card} from "@/components/ui/card";

defineProps<{
  blocos: any[]
  dadosPaciente: any
}>()

const getCategoriaLabel = (cat: string) => {
  const map: Record<string, string> = {
    'pre_med': 'Pré-Medicação',
    'qt': 'Terapia',
    'pos_med_hospitalar': 'Pós-Medicação (Hospitalar)',
    'pos_med_domiciliar': 'Pós-Medicação (Domiciliar)',
  }
  return map[cat] || cat
}

const getCategoriaColor = (cat: string) => {
  if (cat === 'qt') return 'border-blue-200 bg-blue-50/20'
  if (cat === 'pre_med') return 'border-gray-200 bg-gray-50/20'
  return 'border-gray-200 bg-white'
}
</script>

<template>
  <Card class="p-6">
    <div class="space-y-6">
      <div class="border rounded-md p-3 flex items-center mb-2 gap-3">
        <Info class="h-5 w-5 shrink-0"/>
        <div class="text-sm flex flex-col">
          <span>Os blocos abaixo representam a <strong>sequência</strong> exata de administração.</span>
          <span>Itens dentro do mesmo bloco são administrados <strong>concomitantemente</strong> (via Y).</span>
        </div>
      </div>

      <div v-for="(bloco, bIndex) in blocos" :key="bIndex"
           :class="getCategoriaColor(bloco.categoria)"
           class="border rounded-xl overflow-hidden shadow-sm"
      >
        <div class="bg-gray-50/80 px-4 py-3 border-b flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div
                class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-900 text-white font-bold shadow-sm">
              {{ bloco.ordem }}
            </div>
            <div>
              <h3 class="font-bold text-gray-800 uppercase text-sm tracking-wide">{{
                  getCategoriaLabel(bloco.categoria)
                }}</h3>
            </div>
          </div>
        </div>

        <div class="p-4 space-y-4">
          <div v-for="(item, iIndex) in bloco.itens" :key="iIndex">
            <div v-if="item.tipo === 'grupo_alternativas'" class="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div class="flex items-center gap-2 mb-3">
                <AlertCircle class="h-5 w-5 text-orange-600"/>
                <span class="font-bold text-orange-800 text-sm">Seleção Obrigatória: {{ item.labelGrupo }}</span>
              </div>
              <Select
                  :model-value="item.selectedOptionIndex?.toString()"
                  @update:model-value="(val) => {
                 item.selectedOptionIndex = parseInt(val);
                 item.itemSelecionado = JSON.parse(JSON.stringify(item.opcoes[parseInt(val)]));
                 item.itemSelecionado.percentualAjuste = 100;
               }"
              >
                <SelectTrigger class="bg-white border-orange-300">
                  <SelectValue placeholder="Selecione a medicação..."/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="(opt, optIdx) in item.opcoes" :key="optIdx" :value="optIdx.toString()">
                    {{ opt.medicamento }} ({{ opt.doseReferencia }} {{ opt.unidade }})
                  </SelectItem>
                </SelectContent>
              </Select>
              <div v-if="item.itemSelecionado"
                   class="mt-4 pl-4 border-l-2 border-orange-300 animate-in fade-in slide-in-from-top-2">
                <PrescricaoItemRow
                    :dados-paciente="dadosPaciente"
                    :item="item.itemSelecionado"
                />
              </div>
            </div>
            <div v-else>
              <PrescricaoItemRow
                  :dados-paciente="dadosPaciente"
                  :item="item.dados"
              />
            </div>
          </div>

          <div v-if="!bloco.itens || bloco.itens.length === 0" class="text-center text-gray-400 text-sm italic py-2">
            Bloco sem itens.
          </div>
        </div>
      </div>
    </div>
  </Card>
</template>
