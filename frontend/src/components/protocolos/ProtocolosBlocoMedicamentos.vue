<script lang="ts" setup>
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Badge} from '@/components/ui/badge'
import {ArrowDown, ArrowUp, Copy, Plus, Trash2} from 'lucide-vue-next'
import {categoriasBloco} from '@/constants/constProtocolos.ts'
import {cn} from "@/lib/utils.ts"
import {Checkbox} from "@/components/ui/checkbox"
import ProtocolosMedicamentoEditavel from "@/components/protocolos/ProtocolosMedicamentoEditavel.vue"
import type {Bloco} from "@/types/typesProtocolo.ts"
import {useProtocoloBlocos} from '@/composables/useProtocoloBlocos.ts'

defineProps<{
  bloco: Bloco,
  index: number,
  isFirst: boolean,
  isLast: boolean
}>()

const emit = defineEmits(['remove', 'move-up', 'move-down'])

const {
  selectedIndexes,
  addItemToBloco,
  removeItemFromBloco,
  addOptionToGroup,
  removeOptionFromGroup,
  toggleItemType,
  toggleSelection,
  mergeSelected
} = useProtocoloBlocos()
</script>

<template>
  <div class="border rounded-lg bg-white shadow-sm overflow-hidden">
    <div class="bg-gray-100 p-3 flex items-center gap-3 border-b">
      <div class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-800 text-white font-bold">
        {{ bloco.ordem }}
      </div>
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-gray-500 font-bold">CATEGORIA</span>
        <Select v-model="bloco.categoria">
          <SelectTrigger class="w-[200px] h-8 bg-white">
            <SelectValue/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="c in categoriasBloco" :key="c.value" :value="c.value">{{ c.label }}</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="flex items-center gap-2 ml-auto">
        <Button :disabled="isFirst" class="h-8 w-8" size="icon" variant="ghost" @click="$emit('move-up')">
          <ArrowUp class="h-4 w-4 text-gray-600"/>
        </Button>
        <Button :disabled="isLast" class="h-8 w-8" size="icon" variant="ghost" @click="$emit('move-down')">
          <ArrowDown class="h-4 w-4 text-gray-600"/>
        </Button>
        <Button class="h-8 w-8 text-red-500 hover:bg-red-50" size="icon" variant="ghost" @click="$emit('remove')">
          <Trash2 class="h-4 w-4"/>
        </Button>
      </div>
    </div>

    <div class="p-4 bg-gray-50/50 space-y-3">
      <div v-if="bloco.itens.length === 0"
           class="text-center py-4 text-sm text-gray-400 border-2 border-dashed rounded-md">
        Nenhum item neste bloco
      </div>

      <div v-if="selectedIndexes.length > 0"
           class="flex items-center justify-between bg-blue-50 border border-blue-100 p-2 rounded-md animate-in fade-in duration-300">
        <span class="text-xs font-medium text-blue-700 ml-2">
          {{ selectedIndexes.length }} itens selecionados
        </span>
        <div class="flex gap-2">
          <Button class="h-7 text-xs border-blue-200" size="sm" variant="outline" @click="selectedIndexes = []">
            Cancelar
          </Button>
          <Button :disabled="selectedIndexes.length < 2" class="h-7 text-xs bg-blue-600 hover:bg-blue-700" size="sm"
                  @click="mergeSelected">
            Transformar em Grupo de Opções
          </Button>
        </div>
      </div>

      <div v-for="(item, iIndex) in bloco.itens" :key="iIndex"
           :class="cn('flex flex-col gap-2 border rounded-md p-3 bg-white relative group shadow-sm' +
            'transition-colors', selectedIndexes.includes(iIndex) && 'border-blue-400 bg-blue-50/30')"
      >

        <div class="flex justify-between items-center mb-2 border-b pb-2">
          <div class="flex items-center gap-2">
            <Checkbox
                :checked="selectedIndexes.includes(iIndex)"
                @update:checked="(val) => toggleSelection(iIndex, val as boolean)"
            />
            <Badge class="text-[11px] uppercase tracking-wider bg-gray-50" variant="outline">
              {{ item.tipo === 'medicamento_unico' ? 'Medicamento Único' : 'Grupo de Opções' }}
            </Badge>
            <Button
                class="h-6 text-xs text-blue-600 px-2"
                size="sm"
                variant="ghost"
                @click="toggleItemType(bloco, item, iIndex)"
            >
              <Copy class="h-3 w-3 mr-1"/>
              {{ item.tipo === 'medicamento_unico' ? 'Converter em Grupo de Opções' : 'Separar em Itens Únicos' }}
            </Button>
          </div>
          <Button
              class="h-6 w-6 text-gray-400 hover:text-red-500"
              size="icon"
              variant="ghost"
              @click="removeItemFromBloco(bloco, iIndex)"
          >
            <Trash2 class="h-3 w-3"/>
          </Button>
        </div>

        <div v-if="item.tipo === 'medicamento_unico'">
          <ProtocolosMedicamentoEditavel v-model="item.dados"/>
        </div>

        <div v-else class="space-y-3">
          <div>
            <Label class="text-sm">Rótulo do Grupo</Label>
            <Input v-model="item.labelGrupo" class="h-8 font-medium"/>
          </div>

          <div class="pl-3 border-l-4 border-blue-100 space-y-4">
            <div v-for="(opcao, opIdx) in item.opcoes" :key="opIdx"
                 class="bg-white p-3 rounded relative border border-gray-200 shadow-sm">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm font-bold text-gray-700">Opção {{ opIdx + 1 }}</span>
                <Button class="h-6 w-6 text-red-400 hover:text-red-600" size="icon" variant="ghost"
                        @click="removeOptionFromGroup(item, opIdx)">
                  <Trash2 class="h-3 w-3"/>
                </Button>
              </div>
              <ProtocolosMedicamentoEditavel v-model="item.opcoes[opIdx]"/>
            </div>

            <Button class="w-full h-8 text-sm border-dashed" size="sm" variant="outline"
                    @click="addOptionToGroup(item)">
              <Plus class="h-3 w-3 mr-1"/>
              Adicionar Opção ao Grupo
            </Button>
          </div>
        </div>
      </div>

      <Button class="text-sm w-full mt-2" size="sm" variant="secondary" @click="addItemToBloco">
        <Plus class="h-4 w-4 mr-2"/>
        Adicionar Medicamento ao Bloco
      </Button>
    </div>
  </div>
</template>
