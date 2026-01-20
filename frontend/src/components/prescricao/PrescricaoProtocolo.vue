<script lang="ts" setup>
import {computed, ref} from 'vue'
import {useAppStore} from '@/stores/app'
import {Card} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList} from '@/components/ui/command'
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover'
import {AlertTriangle, Check, ChevronsUpDown, Copy, Info} from 'lucide-vue-next'

const props = defineProps<{
  protocolo: string
  numeroCiclo: string
  ultimaPrescricao: any
}>()

const emit = defineEmits<{
  (e: 'update:protocolo', value: string): void
  (e: 'update:numeroCiclo', value: string): void
  (e: 'repetir'): void
}>()

const appStore = useAppStore()
const openCombobox = ref(false)

const localProtocolo = computed({
  get: () => props.protocolo,
  set: (val) => emit('update:protocolo', val)
})

const localNumeroCiclo = computed({
  get: () => props.numeroCiclo,
  set: (val) => emit('update:numeroCiclo', val)
})

const protocoloSelecionadoObj = computed(() => {
  return appStore.protocolos.find(p => p.nome === props.protocolo)
})

const opcoesCiclo = computed(() => {
  const total = protocoloSelecionadoObj.value?.totalCiclos || 0
  if (total === 0) {
    return [{value: '0', label: '0 - Indefinido'}]
  }
  return Array.from({length: total}, (_, i) => ({
    value: (i + 1).toString(),
    label: `Ciclo ${i + 1}`
  }))
})
</script>

<template>
  <Card class="p-6">
    <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div v-if="ultimaPrescricao && ultimaPrescricao.conteudo && ultimaPrescricao.conteudo.protocolo"
           class="col-span-1 sm:col-span-4 bg-blue-50 border border-blue-200 rounded-md p-3 flex items-center
           justify-between mb-2 animate-in fade-in">
        <div class="flex items-center gap-3">
          <Info class="h-5 w-5 text-blue-600 shrink-0"/>
          <div class="text-sm">
            <p class="font-medium text-blue-900">Última Prescrição Emitida</p>
            <div class="flex flex-wrap gap-x-4 mt-1 text-blue-800">
              <span>{{ ultimaPrescricao.conteudo.protocolo.nome }}</span>
              <span><strong>Ciclo {{ ultimaPrescricao.conteudo.protocolo.cicloAtual }}</strong></span>
              <span class="text-blue-600 text-xs self-center">({{
                  new Date(ultimaPrescricao.dataEmissao).toLocaleDateString('pt-BR')
                }})</span>
            </div>
          </div>
        </div>
        <Button
            v-if="ultimaPrescricao"
            class="border bg-white text-blue-700 uppercase font-bold"
            variant="secondary"
            @click="emit('repetir')"
        >
          <Copy class="h-4 w-4 mr-2"/>
          Repetir
        </Button>
      </div>

      <div class="col-span-1 sm:col-span-3 flex flex-col gap-2">
        <Label>Protocolo *</Label>
        <Popover v-model:open="openCombobox">
          <PopoverTrigger as-child>
            <Button :aria-expanded="openCombobox" class="w-full justify-between h-14 px-3 text-left font-normal"
                    role="combobox" type="button" variant="outline">
              <div v-if="localProtocolo" class="flex flex-col items-start text-left overflow-hidden w-full">
                <span class="font-semibold leading-tight truncate w-full">{{ localProtocolo }}</span>
                <span class="text-xs text-muted-foreground leading-tight truncate w-full">
                  {{ appStore.protocolos.find(p => p.nome === localProtocolo)?.indicacao }}
                </span>
              </div>
              <span v-else class="text-muted-foreground">Selecione o protocolo...</span>
              <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50"/>
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" class="w-[--reka-popover-trigger-width] p-0">
            <Command class="h-auto w-full">
              <CommandInput placeholder="Buscar..."/>
              <CommandEmpty>Nenhum protocolo encontrado.</CommandEmpty>
              <CommandList>
                <CommandGroup>
                  <CommandItem
                      v-for="p in appStore.protocolos"
                      :key="p.id"
                      :value="p.nome"
                      class="cursor-pointer border-b last:border-0"
                      @select="() => { localProtocolo = p.nome; openCombobox = false }"
                  >
                    <Check :class="['mr-2 h-4 w-4', localProtocolo === p.nome ? 'opacity-100' : 'opacity-0']"/>
                    <div class="flex flex-col">
                      <span class="font-medium">{{ p.nome }}</span>
                      <span v-if="p.indicacao" class="text-xs text-muted-foreground">{{ p.indicacao }}</span>
                    </div>
                  </CommandItem>
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      <div class="col-span-1 sm:col-span-1 flex flex-col gap-2">
        <Label>Ciclo Atual</Label>
        <Select v-model="localNumeroCiclo" :disabled="!localProtocolo">
          <SelectTrigger class="h-14">
            <SelectValue placeholder="Ciclo"/>
          </SelectTrigger>
          <SelectContent class="max-h-60">
            <SelectItem v-for="op in opcoesCiclo" :key="op.value" :value="op.value">
              {{ op.label }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      </div> <div v-if="protocoloSelecionadoObj && (protocoloSelecionadoObj.observacoes || protocoloSelecionadoObj.precaucoes)"
         class="mt-6 space-y-4 border-t pt-4 animate-in slide-in-from-top-2">

      <div v-if="protocoloSelecionadoObj.observacoes" class="flex flex-col gap-1 px-3">
        <h4 class="text-sm font-bold flex items-center gap-2 text-slate-700">
          <Info class="h-4 w-4" />
          Observações do Protocolo
        </h4>
        <p class="text-sm text-muted-foreground whitespace-pre-line leading-relaxed">
          {{ protocoloSelecionadoObj.observacoes }}
        </p>
      </div>

      <div v-if="protocoloSelecionadoObj.precaucoes" class="flex flex-col gap-1 p-3 bg-amber-50 border border-amber-100 rounded-md">
        <h4 class="text-sm font-bold flex items-center gap-2 text-amber-800">
          <AlertTriangle class="h-4 w-4" />
          Precauções
        </h4>
        <p class="text-sm text-amber-700 whitespace-pre-line">
          {{ protocoloSelecionadoObj.precaucoes }}
        </p>
      </div>
    </div>
  </Card>
</template>
