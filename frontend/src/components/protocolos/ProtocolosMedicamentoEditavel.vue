<script lang="ts" setup>
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import ProtocolosSeletorDiluente from './ProtocolosSeletorDiluente.vue'
import {DetalhesMedicamento, UnidadeDoseEnum, ViaAdministracaoEnum} from "@/types/typesProtocolo.ts";
import {Textarea} from "@/components/ui/textarea";
import {getUnidadeFinal} from "@/utils/utilsPrescricao.ts";
import {formatDiasCicloToString, parseDiasCicloFromString} from "@/utils/utilsComuns.ts";

const props = defineProps<{
  modelValue: DetalhesMedicamento
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: DetalhesMedicamento): void
}>()

const updateField = (field: keyof DetalhesMedicamento, value: any) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [field]: value
  })
}

const handleDiasUpdate = (val: string | number) => {
  updateField('diasDoCiclo', parseDiasCicloFromString(val))
}
</script>

<template>
  <div class="space-y-2">
    <div class="grid grid-cols-12 gap-3">
      <div class="col-span-8">
        <Label class="text-sm">Medicamento</Label>
        <Input
            v-model="modelValue.medicamento"
            class="h-8"
            placeholder="Nome do fármaco"
        />
      </div>
      <div class="col-span-4">
        <Label class="text-sm">Dias do Ciclo</Label>
        <Input
            :model-value="formatDiasCicloToString(modelValue.diasDoCiclo)"
            class="h-8"
            placeholder="Ex: 1, 8, 15"
            @update:model-value="handleDiasUpdate"
        />
      </div>
    </div>

    <div class="grid grid-cols-12 gap-3">
      <div class="col-span-4">
        <Label class="text-sm">Dose Referência</Label>
        <Input v-model="modelValue.doseReferencia" class="h-8" step="0.1" type="number"/>
      </div>
      <div class="col-span-4">
        <Label class="text-sm">Unidade de Medida</Label>
        <Select v-model="modelValue.unidade">
          <SelectTrigger class="h-8">
            <SelectValue/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="u in UnidadeDoseEnum" :key="u" :value="u">{{ u }}</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="col-span-4">
        <Label class="text-sm">Dose Máxima ({{ getUnidadeFinal(modelValue.unidade) }})</Label>
        <Input v-model="modelValue.doseMaxima" class="h-8" placeholder="Opcional" type="number"/>
      </div>
    </div>

    <div class="grid grid-cols-12 gap-3">
      <div class="col-span-2">
        <Label class="text-sm">Via</Label>
        <Select v-model="modelValue.via">
          <SelectTrigger class="h-8">
            <SelectValue/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="v in ViaAdministracaoEnum" :key="v" :value="v">{{ v }}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="col-span-8">
        <ProtocolosSeletorDiluente
            v-model="modelValue.configuracaoDiluicao"
        />
      </div>

      <div class="col-span-2">
        <Label class="text-sm">Tempo (min)</Label>
        <Input v-model="modelValue.tempoMinutos" class="h-8" type="number"/>
      </div>
    </div>

    <div>
      <Label class="text-sm">Notas</Label>
      <Textarea
          v-model="modelValue.notasEspecificas"
          class="min-h-8 max-h-[100px]"
          rows="1"
      />
    </div>
  </div>
</template>
