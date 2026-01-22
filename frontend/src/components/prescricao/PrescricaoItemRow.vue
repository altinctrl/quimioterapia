<script lang="ts" setup>
import {computed, watch} from 'vue'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {AlertTriangle} from 'lucide-vue-next'
import {UnidadeDoseEnum} from "@/types"
import {formatDiasCiclo, getUnidadeFinal} from "@/utils/prescricaoUtils.ts";

const props = defineProps<{
  item: any
  dadosPaciente: {
    peso: number,
    altura: number,
    sc: number,
    creatinina: number,
    idade?: number,
    sexo?: string }
}>()

const emit = defineEmits(['update:item'])

const doseCalculadaInicial = computed(() => {
  const ref = parseFloat(props.item.doseReferencia) || 0
  const un = props.item.unidade
  if (un === UnidadeDoseEnum.MG_M2) return ref * (props.dadosPaciente.sc || 0)
  if (un === UnidadeDoseEnum.MG_KG || un === UnidadeDoseEnum.MCG_KG) return ref * (props.dadosPaciente.peso || 0)
  if (un === UnidadeDoseEnum.AUC) {
    const {creatinina, peso, idade, sexo} = props.dadosPaciente
    if (!creatinina || !peso || !idade || !sexo) return 0
    const pisoCreatinina = props.item.pisoCreatinina ?? 0.7
    const tetoGfr = props.item.tetoGfr ?? 125
    const creatininaFinal = creatinina < pisoCreatinina ? pisoCreatinina : creatinina
    let gfr = ((140 - idade) * peso) / (72 * creatininaFinal)
    if (['F', 'FEMININO'].includes(sexo.toUpperCase())) gfr = gfr * 0.85
    if (gfr > tetoGfr) gfr = tetoGfr
    return ref * (gfr + 25)
  }
  return ref
})

const doseFinal = computed(() => {
  let calc = doseCalculadaInicial.value
  const ajuste = props.item.percentualAjuste || 100
  calc = calc * (ajuste / 100)
  if (props.item.doseMaxima && calc > props.item.doseMaxima) calc = props.item.doseMaxima
  return calc
})

watch(doseCalculadaInicial, (val) => {
  const precisao = val < 1 ? 3 : 2;
  props.item.doseTeorica = parseFloat(val.toFixed(precisao));
}, { immediate: true });

watch(doseFinal, (val) => {
  const precisao = val < 1 ? 3 : 2;
  props.item.doseFinal = parseFloat(val.toFixed(precisao));
}, { immediate: true });

const diluentesPermitidos = computed(() => {
  return props.item.configuracaoDiluicao?.opcoesPermitidas || []
})

watch(() => props.item.unidade, (newUnidade) => {
  if (newUnidade === UnidadeDoseEnum.AUC) {
    if (props.item.pisoCreatinina === undefined) props.item.pisoCreatinina = 0.7
    if (props.item.tetoGfr === undefined) props.item.tetoGfr = 125
  }
}, { immediate: true })

watch(() => props.item.configuracaoDiluicao, (cfg) => {
  if (cfg?.selecionada && !props.item.diluicaoFinal) {
    props.item.diluicaoFinal = cfg.selecionada
  }
}, {immediate: true})

const formatNumber = (val: number) => {
  if (isNaN(val)) return '0,00';
  const casasDecimais = val < 1 ? 3 : 2;
  return val.toLocaleString('pt-BR', {
    minimumFractionDigits: casasDecimais,
    maximumFractionDigits: casasDecimais
  });
}
</script>

<template>
  <div class="bg-white border rounded-lg p-3 shadow-sm">
    <div class="flex flex-wrap items-start justify-between gap-2 mb-3 border-b pb-2">
      <div class="flex flex-col">
        <span class="font-bold text-sm text-gray-800">{{ item.medicamento }}</span>
        <span class="text-sm text-gray-500">
           Referência: {{ item.doseReferencia }} {{ item.unidade }} ({{ item.via }})
           <span v-if="item.doseMaxima" class="text-red-500 font-medium ml-1">
             Máximo: {{ item.doseMaxima + ' ' + getUnidadeFinal(item.unidade)}}
           </span>
        </span>
      </div>

      <div class="flex items-center gap-2">
        <div v-if="props.item.doseMaxima && doseFinal >= props.item.doseMaxima"
             class="flex items-center text-sm text-amber-700 bg-amber-100 px-2 py-1 rounded"
        >
          <AlertTriangle class="h-3 w-3 mr-1"/>
          Teto
        </div>
        <div class="font-bold text-sm text-gray-700 bg-gray-100 px-2 py-1 rounded">
          Dias do Ciclo: {{ formatDiasCiclo(item.diasDoCiclo) }}
        </div>
      </div>
    </div>

    <div v-if="item.unidade === 'AUC'" class="grid grid-cols-2 md:grid-cols-12 gap-3 items-end">
      <div class="col-span-1 md:col-span-6">
        <Label class="text-xs text-gray-500 uppercase">
          Piso Creatinina
        </Label>
        <div class="relative">
          <Input
              v-model.number="item.pisoCreatinina"
              class="h-8 pr-6"
              min="0"
              step="0.1"
              type="number"
          />
          <span class="absolute right-12 top-1.5 text-sm pointer-events-none">mg/dL</span>
        </div>
      </div>

      <div class="col-span-1 md:col-span-6">
        <Label class="text-xs text-gray-500 uppercase">
          Teto GFR
        </Label>
        <div class="relative">
          <Input
              v-model.number="item.tetoGfr"
              class="h-8 pr-6"
              min="0"
              step="1"
              type="number"
          />
          <span class="absolute right-12 top-1.5 text-sm pointer-events-none">mL/min</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-12 gap-3 items-end">
      <div class="col-span-1 md:col-span-4">
        <Label class="text-xs text-gray-500 uppercase">
          Dose Calculada
        </Label>
        <div class="relative">
          <Input
              :model-value="formatNumber(doseCalculadaInicial)"
              class="h-8 bg-gray-50 border-dashed disabled:opacity-100 disabled:cursor-default"
              disabled
          />
          <span class="absolute right-2 top-1.5 text-sm font-medium pointer-events-none bg-gray-50">
            {{ getUnidadeFinal(item.unidade) }}
          </span>
        </div>
      </div>

      <div class="col-span-1 md:col-span-4">
        <Label class="text-xs  font-bold uppercase">
          Ajuste
        </Label>
        <div class="relative">
          <Input
              v-model="item.percentualAjuste"
              class="h-8 pr-6 font-bold"
              min="0"
              type="number"
          />
          <span class="absolute right-12 top-1.5 text-sm pointer-events-none">%</span>
        </div>
      </div>

      <div class="col-span-2 md:col-span-4">
        <Label class="text-xs text-green-600 font-bold uppercase">
          Dose Final
        </Label>
        <div class="relative">
          <Input
              :model-value="formatNumber(doseFinal)"
              class="h-8 bg-green-50 text-green-800 font-bold border-green-200 disabled:opacity-100 disabled:cursor-default"
              disabled
          />
          <span class="absolute right-2 top-1.5 text-sm font-medium pointer-events-none bg-green-50 text-green-800">
            {{ getUnidadeFinal(item.unidade) }}
          </span>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-12 gap-3 items-end">
      <div class="col-span-2 md:col-span-8">
        <Label class="text-xs text-gray-500 uppercase flex items-center gap-1">
          Diluição
        </Label>
        <Select
            v-model="item.diluicaoFinal"
            :disabled="!diluentesPermitidos || diluentesPermitidos.length === 0"
        >
          <SelectTrigger class="h-8 text-sm">
            <SelectValue :placeholder="(!diluentesPermitidos || diluentesPermitidos.length === 0) ? 'Sem diluentes' : 'Selecione...'"/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem
                v-for="dil in diluentesPermitidos"
                :key="dil"
                :value="dil"
            >
              {{ dil }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="col-span-1 md:col-span-4">
        <Label class="text-xs font-bold uppercase">Tempo</Label>
        <div class="relative">
          <Input
              v-model="item.tempoMinutos"
              class="h-8 pr-6"
              min="0"
              type="number"
          />
          <span class="absolute right-12 top-1.5 text-sm pointer-events-none">minutos</span>
        </div>
      </div>
    </div>
    <div class="col-span-2 md:col-span-3">
      <Label class="text-xs text-gray-500 uppercase">Notas</Label>
      <Input v-model="item.notasEspecificas" class="h-8 text-sm"/>
    </div>
  </div>
</template>
