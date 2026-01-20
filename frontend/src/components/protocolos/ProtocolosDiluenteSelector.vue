<script lang="ts" setup>
import {computed} from 'vue'
import {Button} from '@/components/ui/button'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {ChevronDown} from 'lucide-vue-next'
import {diluentesDisponiveis} from '@/utils/protocoloConstants'
import {ConfiguracaoDiluicao} from "@/types";

const props = defineProps<{
  modelValue: ConfiguracaoDiluicao
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ConfiguracaoDiluicao): void
}>()

const labelResumido = computed(() => {
  const permitidos = props.modelValue?.opcoesPermitidas || []
  if (permitidos.length === 0) return 'Selecione...'
  if (permitidos.length === 1) return permitidos[0]
  return `${permitidos.length} selecionados`
})

const toggleDiluente = (diluente: string, checked: boolean) => {
  const novoConfig = {...props.modelValue}

  if (!novoConfig.opcoesPermitidas) novoConfig.opcoesPermitidas = []

  if (checked) {
    if (!novoConfig.opcoesPermitidas.includes(diluente)) {
      novoConfig.opcoesPermitidas.push(diluente)
    }
    if (novoConfig.opcoesPermitidas.length === 1) {
      novoConfig.selecionada = diluente
    }
  } else {
    novoConfig.opcoesPermitidas = novoConfig.opcoesPermitidas.filter(d => d !== diluente)
    if (novoConfig.selecionada === diluente) {
      novoConfig.selecionada = novoConfig.opcoesPermitidas[0] || ''
    }
  }
  emit('update:modelValue', novoConfig)
}
</script>

<template>
  <div class="grid grid-cols-12 gap-2">
    <div class="col-span-6">
      <Label class="text-sm">Diluentes Permitidos</Label>
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button class="w-full justify-between font-normal px-2 bg-white h-8 text-sm" variant="outline">
            <span class="truncate">{{ labelResumido }}</span>
            <ChevronDown class="h-3 w-3 opacity-50"/>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" class="text-sm w-full max-h-60 overflow-y-auto">
          <DropdownMenuCheckboxItem
              v-for="dil in diluentesDisponiveis"
              :key="dil"
              :checked="modelValue.opcoesPermitidas?.includes(dil)"
              class="hover:bg-neutral-100"
              @select.prevent="toggleDiluente(dil, !modelValue.opcoesPermitidas?.includes(dil))"
          >
            {{ dil }}
          </DropdownMenuCheckboxItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>

    <div class="col-span-6">
      <Label class="text-sm">Diluente Padrão</Label>
      <Select
          :disabled="!modelValue.opcoesPermitidas?.length"
          :model-value="modelValue.selecionada"
          @update:model-value="(val) => emit('update:modelValue', { ...modelValue, selecionada: val as string})"
      >
        <SelectTrigger class="bg-white h-8 text-sm">
          <SelectValue placeholder="Padrão"/>
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="d in modelValue.opcoesPermitidas || []" :key="d" :value="d" class="text-sm">
            {{ d }}
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  </div>
</template>
