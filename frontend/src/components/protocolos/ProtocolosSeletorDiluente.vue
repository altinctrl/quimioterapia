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
import {ConfiguracaoDiluicao} from "@/types/typesProtocolo.ts";
import {useConfiguracaoStore} from "@/stores/storeAjustes.ts"

const props = defineProps<{
  modelValue: ConfiguracaoDiluicao | undefined
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ConfiguracaoDiluicao): void
}>()

const configStore = useConfiguracaoStore()

const listaGlobalDiluentes = computed(() => {
  return configStore.parametros?.diluentes || []
})

const safeModelValue = computed((): ConfiguracaoDiluicao => {
  return props.modelValue || { selecionada: '', opcoesPermitidas: [] }
})

const diluentesUnificados = computed(() => {
  const globais = listaGlobalDiluentes.value
  const locais = safeModelValue.value.opcoesPermitidas || []
  const unicos = new Set([...globais, ...locais])
  return Array.from(unicos).sort((a, b) => a.localeCompare(b))
})

const isIndisponivel = (diluente: string) => {
  if (listaGlobalDiluentes.value.length === 0) return false
  return !listaGlobalDiluentes.value.includes(diluente)
}

const labelResumido = computed(() => {
  if (diluentesUnificados.value.length === 0) return 'Sem opções'
  const permitidos = safeModelValue.value.opcoesPermitidas || []
  if (permitidos.length === 0) return 'Selecione...'
  if (permitidos.length === 1) return permitidos[0]
  return `${permitidos.length} selecionados`
})

const toggleDiluente = (diluente: string, checked: boolean) => {
  const novoConfig: ConfiguracaoDiluicao = props.modelValue
    ? {...props.modelValue}
    : { selecionada: '', opcoesPermitidas: [] }

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

const updateSelecionada = (val: string) => {
  const novoConfig: ConfiguracaoDiluicao = props.modelValue
      ? {...props.modelValue, selecionada: val}
      : {selecionada: val, opcoesPermitidas: [val]}
  emit('update:modelValue', novoConfig)
}
</script>

<template>
  <div class="grid grid-cols-12 gap-2">
    <div class="col-span-6">
      <Label class="text-sm">Diluentes Permitidos</Label>
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button
            class="w-full justify-between font-normal px-2 bg-white h-8 text-sm"
            variant="outline"
            :disabled="diluentesUnificados.length === 0"
          >
            <span class="truncate">{{ labelResumido }}</span>
            <ChevronDown class="h-3 w-3 opacity-50"/>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" class="text-sm w-full max-h-60 overflow-y-auto">
          <div v-if="diluentesUnificados.length === 0" class="p-2 text-xs text-muted-foreground text-center">
            Nenhum diluente cadastrado
          </div>

          <DropdownMenuCheckboxItem
              v-for="dil in diluentesUnificados"
              :key="dil"
              :checked="safeModelValue.opcoesPermitidas?.includes(dil)"
              class="hover:bg-neutral-100 flex items-center justify-between gap-2"
              @select.prevent="toggleDiluente(dil, !safeModelValue.opcoesPermitidas?.includes(dil))"
          >
            <span :class="isIndisponivel(dil) ? 'text-red-600 line-through decoration-red-600/50' : ''">
              {{ dil }}
            </span>
            <span v-if="isIndisponivel(dil)" class="text-[10px] text-red-500 font-bold bg-red-50 px-1 rounded ml-auto">
              INDISPONÍVEL
            </span>
          </DropdownMenuCheckboxItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>

    <div class="col-span-6">
      <Label class="text-sm">Diluente Padrão</Label>
      <Select
          :disabled="!safeModelValue.opcoesPermitidas?.length"
          :model-value="safeModelValue.selecionada"
          @update:model-value="(val) => updateSelecionada(val as string)"
      >
        <SelectTrigger class="bg-white h-8 text-sm">
          <SelectValue :placeholder="safeModelValue.opcoesPermitidas?.length === 0 ? 'Sem opções' : 'Selecione...'"/>
        </SelectTrigger>
        <SelectContent>
          <SelectItem
            v-for="d in safeModelValue.opcoesPermitidas || []"
            :key="d"
            :value="d"
            class="text-sm hover:bg-neutral-100 flex items-center justify-between gap-2"
          >
            <span :class="isIndisponivel(d) ? 'text-red-600 line-through decoration-red-600/50' : ''">
              {{ d }}
            </span>
            <span v-if="isIndisponivel(d)" class="text-[10px] text-red-500 font-bold bg-red-50 px-1 rounded ml-auto">
              INDISPONÍVEL
            </span>
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  </div>
</template>
