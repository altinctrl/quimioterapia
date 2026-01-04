<script lang="ts" setup>
import {computed, ref} from 'vue'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList} from '@/components/ui/command'
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover'
import {Activity, Check, ChevronsUpDown, Copy, Info} from 'lucide-vue-next'

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
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <Activity class="h-5 w-5"/>
        2. Ciclo
      </CardTitle>
    </CardHeader>
    <CardContent class="grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div v-if="ultimaPrescricao"
           class="col-span-1 sm:col-span-4 bg-blue-50 border border-blue-200 rounded-md p-3 flex items-start gap-3 mb-2">
        <Info class="h-5 w-5 text-blue-600 mt-0.5 shrink-0"/>
        <div class="text-sm">
          <p class="font-medium text-blue-900">Último Tratamento Registrado</p>
          <div class="flex flex-wrap gap-x-4 mt-1 text-blue-800">
            <span>Protocolo: <strong>{{ ultimaPrescricao.protocolo }}</strong></span>
            <span>Ciclo Realizado: <strong>{{ ultimaPrescricao.cicloAtual }}</strong></span>
            <span class="text-blue-600 text-xs self-center">({{
                new Date(ultimaPrescricao.dataPrescricao).toLocaleDateString('pt-BR')
              }})</span>
          </div>
        </div>
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
                      :value="p.nome + ' ' + p.indicacao"
                      class="cursor-pointer border-b last:border-0"
                      @select="() => { localProtocolo = p.nome; openCombobox = false }"
                  >
                    <Check :class="['mr-2 h-4 w-4', localProtocolo === p.nome ? 'opacity-100' : 'opacity-0']"/>
                    <div class="flex flex-col">
                      <span class="font-medium">{{ p.nome }}</span>
                      <span class="text-xs text-muted-foreground">{{ p.indicacao }} • {{ p.duracao }} min</span>
                    </div>
                  </CommandItem>
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      <div class="col-span-1 sm:col-span-1 flex flex-col gap-2">
        <Label>Ciclo Nº</Label>
        <Input v-model="localNumeroCiclo" class="h-14" type="number"/>
      </div>
    </CardContent>
  </Card>

  <div class="flex justify-center py-2">
    <div class="relative inline-block">
      <Button
          :disabled="!ultimaPrescricao || protocolo !== ultimaPrescricao.protocolo"
          class="text-blue-700 border-blue-200 hover:bg-blue-50 bg-white shadow-sm"
          variant="outline"
          @click="emit('repetir')"
      >
        <Copy class="h-4 w-4 mr-2"/>
        Repetir Última Prescrição
      </Button>

      <span
          v-if="ultimaPrescricao && protocolo !== ultimaPrescricao.protocolo"
          class="absolute left-1/2 -translate-x-1/2 -top-8 w-max px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 hover:opacity-100 transition-opacity cursor-help"
      >
        Disponível apenas para o mesmo protocolo
      </span>
    </div>
  </div>
</template>
