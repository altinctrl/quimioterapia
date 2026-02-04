<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {AlertTriangle} from 'lucide-vue-next'
import {UnidadeDoseEnum} from '@/types/typesProtocolo.ts'
import {getUnidadeFinal, isDiluenteDisponivel} from '@/utils/utilsPrescricao.ts'
import {usePrescricaoCalculos} from '@/composables/usePrescricaoCalculos.ts'
import {formatNumber, parseNumber} from '@/utils/utilsComuns.ts'

const props = defineProps<{
  item: any
  dadosPaciente: {
    peso: number,
    altura: number,
    sc: number,
    creatinina: number,
    idade?: number,
    sexo?: string
  }
  errors?: Record<string, string>
}>()

const emit = defineEmits(['update:item'])

const {calcularDoseTeorica, calcularDoseFinal} = usePrescricaoCalculos()

const localItem = ref({...props.item})

const diluentesPermitidos = computed(() => {
  return localItem.value?.configuracaoDiluicao?.opcoesPermitidas || []
})

const atualizarCalculos = () => {
  if (!localItem.value) return

  const itemNumerico = {
    ...localItem.value,
    pisoCreatinina: parseNumber(localItem.value.pisoCreatinina),
    tetoGfr: parseNumber(localItem.value.tetoGfr),
    percentualAjuste: parseNumber(localItem.value.percentualAjuste),
    doseMaxima: parseNumber(localItem.value.doseMaxima)
  }

  const novaDoseTeorica = calcularDoseTeorica(itemNumerico, props.dadosPaciente as any)

  if (localItem.value.doseTeorica !== novaDoseTeorica) {
    localItem.value.doseTeorica = novaDoseTeorica
  }

  const novaDoseFinal = calcularDoseFinal(
      novaDoseTeorica,
      itemNumerico.percentualAjuste,
      itemNumerico.doseMaxima
  )

  if (localItem.value.doseFinal !== novaDoseFinal) {
    localItem.value.doseFinal = novaDoseFinal
  }
}

const diasDoCicloModel = computed({
  get: () => {
    const val = localItem.value.diasDoCiclo;
    if (Array.isArray(val)) {
      return val.join(', ');
    }
    return val || '';
  },
  set: (val: string) => {
    localItem.value.diasDoCiclo = val as any;
  }
});

watch(localItem, (novoValor) => {
  emit('update:item', JSON.parse(JSON.stringify(novoValor)))
}, {deep: true})

watch(() => props.item, (novoItemProp) => {
  if (novoItemProp && novoItemProp.idItem !== localItem.value.idItem) {
    localItem.value = {...novoItemProp}
    atualizarCalculos()
  }
}, {deep: true})

watch(() => props.dadosPaciente, () => {
  atualizarCalculos()
}, {deep: true})

onMounted(() => {
  atualizarCalculos()
})
</script>

<template>
  <div
      :class="{'border-red-500': Object.keys(errors || {}).length > 0}"
      class="bg-white border rounded-lg p-3 shadow-sm"
  >
    <div class="flex flex-wrap items-start justify-between gap-2 mb-3 border-b pb-2">
      <div class="flex flex-col">
        <span class="font-bold text-sm text-gray-800">{{ localItem.medicamento }}</span>
        <span class="text-sm text-gray-500">
           Referência: {{ localItem.doseReferencia }} {{ localItem.unidade }} ({{ localItem.via }})
           <span v-if="parseNumber(localItem.doseMaxima) > 0" class="text-red-500 font-medium ml-1">
             Máximo: {{ localItem.doseMaxima + ' ' + getUnidadeFinal(localItem.unidade) }}
           </span>
        </span>
      </div>

      <div class="flex items-center gap-2">
        <div
            v-if="parseNumber(localItem.doseMaxima) > 0 && localItem.doseFinal >= parseNumber(localItem.doseMaxima)"
            class="flex items-center text-sm text-amber-700 bg-amber-100 px-2 py-1 rounded"
        >
          <AlertTriangle class="h-3 w-3 mr-1"/>
          Teto Atingido
        </div>
      </div>
    </div>

    <div v-if="localItem.unidade === UnidadeDoseEnum.AUC" class="grid grid-cols-2 md:grid-cols-12 gap-3 items-start">
      <div class="col-span-1 md:col-span-6">
        <Label :class="errors?.pisoCreatinina ? 'text-red-500' : 'text-gray-500'" class="text-xs uppercase">
          Piso Creatinina
        </Label>
        <div class="relative">
          <Input
              v-model="localItem.pisoCreatinina"
              :class="{'border-red-500': errors?.pisoCreatinina}"
              class="h-8 pr-6"
              inputmode="decimal"
              type="text"
              @update:model-value="atualizarCalculos"
          />
          <span class="absolute right-2 top-1.5 text-sm pointer-events-none">mg/dL</span>
        </div>
        <span v-if="errors?.pisoCreatinina" class="text-xs text-red-500">{{ errors.pisoCreatinina }}</span>
      </div>

      <div class="col-span-1 md:col-span-6">
        <Label :class="errors?.tetoGfr ? 'text-red-500' : 'text-gray-500'" class="text-xs uppercase">
          Teto GFR
        </Label>
        <div class="relative">
          <Input
              v-model="localItem.tetoGfr"
              :class="{'border-red-500': errors?.tetoGfr}"
              class="h-8 pr-6"
              inputmode="decimal"
              type="text"
              @update:model-value="atualizarCalculos"
          />
          <span class="absolute right-2 top-1.5 text-sm pointer-events-none">mL/min</span>
        </div>
        <span v-if="errors?.tetoGfr" class="text-xs text-red-500">{{ errors.tetoGfr }}</span>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-12 gap-3 items-start">
      <div class="col-span-1 md:col-span-4">
        <Label class="text-xs text-gray-500 uppercase">Dose Teórica</Label>
        <div class="relative">
          <Input
              :model-value="formatNumber(localItem.doseTeorica)"
              class="h-8 bg-gray-50 border-dashed"
              disabled
          />
          <span class="absolute right-2 top-1.5 text-sm font-medium pointer-events-none bg-gray-50">
            {{ getUnidadeFinal(localItem.unidade) }}
          </span>
        </div>
      </div>

      <div class="col-span-1 md:col-span-4">
        <Label :class="{'text-red-500': errors?.percentualAjuste}" class="text-xs font-bold uppercase">
          Ajuste
        </Label>
        <div class="relative">
          <Input
              v-model="localItem.percentualAjuste"
              :class="{'border-red-500': errors?.percentualAjuste}"
              class="h-8 pr-6 font-bold"
              inputmode="decimal"
              type="text"
              @update:model-value="atualizarCalculos"
          />
          <span class="absolute right-2 top-1.5 text-sm pointer-events-none">%</span>
        </div>
        <span v-if="errors?.percentualAjuste" class="text-xs text-red-500">{{ errors?.percentualAjuste }}</span>
      </div>

      <div class="col-span-2 md:col-span-4">
        <Label :class="errors?.doseFinal ? 'text-red-500' : 'text-green-600'" class="text-xs font-bold uppercase">
          Dose Final
        </Label>
        <div class="relative">
          <Input
              :class="{'border-red-500 bg-red-50': errors?.doseFinal}"
              :model-value="formatNumber(localItem.doseFinal)"
              class="h-8 bg-green-50 text-green-800 font-bold border-green-200 disabled:opacity-100 disabled:cursor-default"
              disabled
          />
          <span class="absolute right-2 top-1.5 text-sm font-medium pointer-events-none bg-green-50 text-green-800">
            {{ getUnidadeFinal(localItem.unidade) }}
          </span>
        </div>
        <span v-if="errors?.doseFinal" class="text-xs text-red-500 font-bold">{{ errors.doseFinal }}</span>
      </div>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-12 gap-3 items-start">
      <div class="col-span-2 md:col-span-4">
        <Label :class="errors?.diluicaoFinal ? 'text-red-500' : 'text-gray-500'" class="text-xs uppercase">
          Diluição
        </Label>
        <Select v-model="localItem.diluicaoFinal" :disabled="!diluentesPermitidos.length">
          <SelectTrigger
              :class="{
                'border-red-500': errors?.diluicaoFinal,
                'border-red-300 text-red-900': diluentesPermitidos.length > 0 && isDiluenteDisponivel(localItem.diluicaoFinal)
              }"
              class="h-8 text-sm"
          >
            <SelectValue :placeholder="diluentesPermitidos.length ? 'Selecione...' : 'Sem opções'"/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem
                v-for="dil in diluentesPermitidos"
                :key="dil"
                :value="dil"
            >
              <span :class="isDiluenteDisponivel(dil) ? 'text-red-600 line-through decoration-red-600/50' : ''">
                {{ dil }}
              </span>
              <span
                  v-if="isDiluenteDisponivel(dil)"
                  class="text-xs text-red-500 font-bold bg-red-50 px-1 rounded ml-auto"
              >
                INDISPONÍVEL
              </span>
            </SelectItem>
          </SelectContent>
        </Select>
        <span v-if="errors?.diluicaoFinal" class="text-xs text-red-500">{{ errors.diluicaoFinal }}</span>
      </div>

      <div class="col-span-1 md:col-span-4">
        <Label :class="{'text-red-500': errors?.tempoMinutos}" class="text-xs font-bold uppercase">Tempo</Label>
        <div class="relative">
          <Input
              v-model="localItem.tempoMinutos"
              :class="{'border-red-500': errors?.tempoMinutos}"
              class="h-8 pr-6"
              inputmode="decimal"
              type="text"
          />
          <span class="absolute right-2 top-1.5 text-sm pointer-events-none">minutos</span>
        </div>
        <span v-if="errors?.tempoMinutos" class="text-xs text-red-500">{{ errors?.tempoMinutos }}</span>
      </div>

      <div class="col-span-1 md:col-span-4">
        <Label :class="{'text-red-500': errors?.diasDoCiclo}" class="text-xs font-bold uppercase">Dias do ciclo</Label>
        <div class="relative">
          <Input
              v-model="diasDoCicloModel"
              :class="{'border-red-500': errors?.diasDoCiclo}"
              class="h-8 pr-6"
              placeholder="Ex: 1, 8, 15"
              type="text"
          />
        </div>
        <span v-if="errors?.diasDoCiclo" class="text-xs text-red-500">{{ errors?.diasDoCiclo }}</span>
      </div>
    </div>
    <div class="col-span-2 md:col-span-3">
      <Label class="text-xs text-gray-500 uppercase">Notas</Label>
      <Input v-model="localItem.notasEspecificas" class="h-8 text-sm"/>
    </div>
  </div>
</template>
