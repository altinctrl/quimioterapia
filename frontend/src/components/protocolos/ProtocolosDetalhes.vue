<script lang="ts" setup>
import {computed} from 'vue'
import {Button} from '@/components/ui/button'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'

const props = defineProps<{
  open: boolean
  protocolo: any
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()

const isOpen = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})

const diasSemanaOptions = [
  {value: 1, label: 'Segunda'},
  {value: 2, label: 'Terça'},
  {value: 3, label: 'Quarta'},
  {value: 4, label: 'Quinta'},
  {value: 5, label: 'Sexta'}
]

const inferirGrupoInfusao = (duracao: number): 'rapido' | 'medio' | 'longo' => {
  if (duracao < 120) return 'rapido'
  if (duracao <= 240) return 'medio'
  return 'longo'
}
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogContent class="max-w-2xl">
      <DialogHeader>
        <DialogTitle>{{ protocolo?.nome }}</DialogTitle>
        <DialogDescription>
          <span class="block font-medium text-foreground mb-1">{{ protocolo?.indicacao }}</span>
          <span v-if="protocolo?.descricao" class="block text-xs font-normal text-muted-foreground">
            {{ protocolo.descricao }}
          </span>
        </DialogDescription>
      </DialogHeader>

      <div v-if="protocolo" class="space-y-6">
        <div class="bg-gray-50 p-3 rounded-lg border text-sm space-y-3">
          <div class="grid grid-cols-4 gap-4">
            <div><span class="text-gray-500 block text-xs uppercase font-bold">Duração</span>
              {{ protocolo.duracao }} min
            </div>
            <div><span class="text-gray-500 block text-xs uppercase font-bold">Frequência</span>
              {{ protocolo.frequencia }}
            </div>
            <div><span class="text-gray-500 block text-xs uppercase font-bold">Ciclos</span>
              {{ protocolo.numeroCiclos }}
            </div>
            <div>
              <span class="text-gray-500 block text-xs uppercase font-bold">Grupo</span>
              <span class="capitalize">{{
                  protocolo.grupoInfusao || inferirGrupoInfusao(protocolo.duracao)
                }}</span>
            </div>
          </div>

          <div v-if="protocolo.diasSemanaPermitidos?.length" class="pt-2 border-t border-gray-200">
            <span class="text-gray-500 text-xs uppercase font-bold mr-2">Dias Permitidos:</span>
            <span class="text-gray-700">
              {{
                protocolo.diasSemanaPermitidos.map((d: number) => diasSemanaOptions.find(o => o.value === d)?.label).join(', ')
              }}
            </span>
          </div>
        </div>

        <div class="space-y-6">
          <div v-if="protocolo.preMedicacoes?.length">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Pré-Quimioterapia</h4>
            <ul class="space-y-2">
              <li v-for="(m, i) in protocolo.preMedicacoes" :key="i"
                  class="text-sm flex justify-between border-b border-gray-100 pb-2 last:border-0">
                <span class="text-gray-700">{{ m.nome }}</span>
                <span class="text-gray-500 font-medium text-xs">
                  {{ m.dosePadrao }} {{ m.unidadePadrao }} <span class="text-gray-300 mx-1">|</span> {{ m.viaPadrao }}
                </span>
              </li>
            </ul>
          </div>

          <div v-if="protocolo.medicamentos?.length">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Quimioterapia</h4>
            <ul class="space-y-2">
              <li v-for="(m, i) in protocolo.medicamentos" :key="i"
                  class="text-sm flex justify-between border-b border-gray-100 pb-2 last:border-0">
                <span class="text-gray-700 font-medium">{{ m.nome }}</span>
                <span class="text-gray-500 font-medium text-xs">
                  {{ m.dosePadrao }} {{ m.unidadePadrao }} <span class="text-gray-300 mx-1">|</span> {{ m.viaPadrao }}
                </span>
              </li>
            </ul>
          </div>

          <div v-if="protocolo.posMedicacoes?.length">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Pós-Quimioterapia</h4>
            <ul class="space-y-2">
              <li v-for="(m, i) in protocolo.posMedicacoes" :key="i"
                  class="text-sm flex justify-between border-b border-gray-100 pb-2 last:border-0">
                <span class="text-gray-700">{{ m.nome }}</span>
                <span class="text-gray-500 font-medium text-xs">
                  {{ m.dosePadrao }} {{ m.unidadePadrao }} <span class="text-gray-300 mx-1">|</span> {{ m.viaPadrao }}
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div v-if="protocolo.observacoes || protocolo.precaucoes" class="space-y-3 pt-4 border-t">
          <div v-if="protocolo.observacoes">
            <span class="text-xs font-bold text-gray-500 uppercase block mb-1">Observações</span>
            <p class="text-sm text-gray-700 bg-gray-50 p-2 rounded border">{{ protocolo.observacoes }}</p>
          </div>
          <div v-if="protocolo.precaucoes">
            <span class="text-xs font-bold text-red-600 uppercase block mb-1">Precauções</span>
            <p class="text-sm text-red-800 bg-red-50 p-2 rounded border border-red-100">
              {{ protocolo.precaucoes }}</p>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="isOpen = false">Fechar</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>