<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {ScrollArea} from '@/components/ui/scroll-area'
import {Separator} from '@/components/ui/separator'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {AlertTriangle, CalendarDays, ChevronLeft, ChevronRight, Info, Layers} from 'lucide-vue-next'
import {diasSemanaOptions} from '@/utils/protocoloConstants'
import ProtocolosMedicamentoRead from "@/components/protocolos/ProtocolosMedicamentoRead.vue";

const props = defineProps<{
  open: boolean
  protocolo: any
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()

const activeTemplateIndex = ref(0)
const tabsContainerRef = ref<HTMLElement | null>(null)

const isOpen = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})

const currentTemplate = computed(() => {
  if (!props.protocolo?.templatesCiclo?.length) return null
  return props.protocolo.templatesCiclo[activeTemplateIndex.value]
})

const scrollTabs = (direction: 'left' | 'right') => {
  if (!tabsContainerRef.value) return
  const amount = 200
  tabsContainerRef.value.scrollBy({
    left: direction === 'left' ? -amount : amount,
    behavior: 'smooth'
  })
}

const formatarDiasSemana = (dias: number[]) => {
  if (!dias || !dias.length) return ''
  const nomes = dias.map(dia => diasSemanaOptions.find(o => o.value === dia)?.label || '')
  if (nomes.length === 1) return nomes[0]
  const ultimoNome = nomes.pop()
  return `${nomes.join(', ')} e ${ultimoNome}`
}

const getCategoriaLabel = (cat: string) => {
  const map: Record<string, string> = {
    'pre_med': 'Pré-Medicação',
    'qt': 'Terapia',
    'pos_med_hospitalar': 'Pós-Med (Hosp)',
    'pos_med_domiciliar': 'Pós-Med (Casa)',
    'infusor': 'Infusor'
  }
  return map[cat] || cat
}

watch(() => props.protocolo, () => {
  activeTemplateIndex.value = 0
})
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogContent class="max-w-4xl max-h-[90vh] flex flex-col p-0 gap-0">
      <DialogHeader class="p-6 pb-4 border-b">
        <div class="flex items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
            </div>
            <DialogTitle class="text-xl font-bold text-gray-900 flex items-center gap-3">
              {{ protocolo?.nome }}
              <Badge v-if="!protocolo?.ativo" class="text-xs">Inativo</Badge>
            </DialogTitle>
            <DialogDescription class="mt-1 text-sm text-gray-600 flex flex-col">
              {{ protocolo?.indicacao }}
              <div>
              <span v-if="protocolo?.fase" class="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {{ protocolo?.fase }}
              </span>
                <span v-if="protocolo?.linha"
                      class="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                de {{ protocolo.linha }}ª Linha
              </span>
              </div>
            </DialogDescription>
          </div>
        </div>
      </DialogHeader>

      <ScrollArea class="h-[calc(90vh-140px)] w-full">
        <div class="p-6 space-y-6">
          <div class="flex flex-col gap-4">
            <div v-if="protocolo?.diasSemanaPermitidos?.length" class="flex gap-2">
              <h4 class="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                <CalendarDays class="h-3 w-3"/>
                Dias Permitidos:
              </h4>
              <div class="flex flex-wrap gap-1">
                <div class="text-xs">
                  {{ formatarDiasSemana(protocolo.diasSemanaPermitidos) }}
                </div>
              </div>
            </div>

            <div class="flex items-center text-sm text-gray-600 bg-gray-50 p-2 rounded-lg border">
              <div class="flex flex-1 flex-col items-center px-2">
                <span class="text-[10px] uppercase font-bold text-gray-400">Duração do Ciclo</span>
                <div class="font-medium flex items-center gap-1">
                  {{ protocolo?.duracaoCicloDias }} dias
                </div>
              </div>
              <div class="w-px bg-gray-200 h-8"></div>
              <div class="flex flex-1 flex-col items-center px-2">
                <span class="text-[10px] uppercase font-bold text-gray-400">Total de Ciclos</span>
                <div class="font-medium">
                  {{ protocolo?.totalCiclos ? `${protocolo.totalCiclos} ciclos` : 'Indefinida' }}
                </div>
              </div>
              <div class="w-px bg-gray-200 h-8"></div>
              <div class="flex flex-1 flex-col items-center px-2">
                <span class="text-[10px] uppercase font-bold text-gray-400">Tempo de Administração</span>
                <div class="font-medium flex items-center gap-1">
                  {{ protocolo?.tempoTotalMinutos }} min
                </div>
              </div>
            </div>


            <div v-if="protocolo.observacoes" class="bg-blue-50/50 p-3 rounded-md border border-blue-100 text-sm">
              <strong class="text-blue-700 text-xs uppercase mb-1 flex items-center gap-1">
                <Info class="h-3 w-3"/>
                Observações
              </strong>
              {{ protocolo.observacoes }}
            </div>

            <div v-if="protocolo.precaucoes" class="bg-red-50/50 p-3 rounded-md border border-red-100 text-sm">
              <strong class="text-red-700 text-xs uppercase mb-1 flex items-center gap-1">
                <AlertTriangle class="h-3 w-3"/>
                Precauções
              </strong>
              {{ protocolo.precaucoes }}
            </div>

            <Separator/>
          </div>

          <div v-if="protocolo?.templatesCiclo?.length">
            <div class="flex flex-col gap-1 mb-3">
              <h3 class="text-lg font-semibold flex items-center gap-2">
                <Layers class="h-5 w-5 text-gray-600"/>
                Esquema de Administração
              </h3>
            </div>

            <div v-if="protocolo.templatesCiclo.length > 1"
                 class="bg-gray-100/50 p-1 rounded-lg border flex items-center gap-1 mb-4 w-full">
              <Button
                  class="h-8 w-8 shrink-0 text-gray-400"
                  size="icon"
                  variant="ghost"
                  @click="scrollTabs('left')">
                <ChevronLeft class="h-4 w-4"/>
              </Button>

              <div ref="tabsContainerRef"
                   class="flex items-center gap-2 overflow-x-auto flex-1 px-1 w-0"
                   style="scrollbar-width: thin; -ms-overflow-style: -ms-autohiding-scrollbar;"
              >
                <Button
                    v-for="(template, idx) in protocolo.templatesCiclo"
                    :key="idx"
                    :class="activeTemplateIndex !== idx ? 'bg-white border-gray-200 text-gray-600' : ''"
                    :variant="activeTemplateIndex === idx ? 'default' : 'outline'"
                    class="h-8 text-sm whitespace-nowrap flex-shrink-0"
                    size="sm"
                    @click="activeTemplateIndex = idx"
                >
                  {{ template.idTemplate || `Variante ${idx + 1}` }}
                </Button>
              </div>

              <Button
                  class="h-8 w-8 shrink-0 text-gray-400"
                  size="icon"
                  variant="ghost"
                  @click="scrollTabs('right')">
                <ChevronRight class="h-4 w-4"/>
              </Button>
            </div>

            <div v-if="currentTemplate" class="border rounded-xl overflow-hidden shadow-sm bg-white">
              <div class="bg-gray-50 px-4 py-2 border-b flex justify-between items-center">
                 <span class="font-medium text-sm text-gray-700">
                   {{ currentTemplate.idTemplate }}
                 </span>
                <span v-if="currentTemplate.aplicavelAosCiclos" class="text-xs text-gray-500">
                   Aplica-se aos ciclos: <strong>{{ currentTemplate.aplicavelAosCiclos }}</strong>
                 </span>
              </div>

              <div class="divide-y divide-gray-100">
                <div v-for="bloco in currentTemplate.blocos" :key="bloco.ordem" class="p-4">
                  <div class="flex items-center gap-3 mb-3">
                    <div
                        class="flex items-center justify-center w-6 h-6 rounded-full bg-gray-900 text-white text-xs font-bold">
                      {{ bloco.ordem }}
                    </div>
                    <Badge class="uppercase text-sm tracking-wider" variant="secondary">
                      {{ getCategoriaLabel(bloco.categoria) }}
                    </Badge>
                  </div>

                  <div class="space-y-3 pl-9">
                    <div v-for="(item, iIdx) in bloco.itens" :key="iIdx">

                      <div v-if="item.tipo === 'medicamento_unico'"
                           class="bg-gray-50/80 rounded-lg p-3 border border-gray-100 relative">
                        <ProtocolosMedicamentoRead :dados="item.dados"/>
                      </div>

                      <div v-else class="border border-blue-100 rounded-lg overflow-hidden">
                        <div
                            class="bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700 uppercase flex items-center justify-between">
                          <span>Grupo: {{ item.labelGrupo }}</span>
                        </div>
                        <div class="flex flex-col gap-2 p-2 space-y-2 bg-slate-50/50">
                          <div v-for="(opcao, opIdx) in item.opcoes" :key="opIdx"
                               class="pl-3 border-l-2 border-gray-300 text-sm py-1"
                          >
                            <ProtocolosMedicamentoRead :dados="opcao"/>
                          </div>
                        </div>
                      </div>

                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              Nenhum template selecionado ou disponível.
            </div>
          </div>
        </div>
      </ScrollArea>

      <DialogFooter class="p-4 border-t bg-gray-50">
        <Button @click="isOpen = false">Fechar</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
