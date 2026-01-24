<script lang="ts" setup>
import {computed, ref} from 'vue'
import {Button} from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {ArrowUpDown, ChevronDown, ChevronUp, Clock, Eye, EyeOff, Filter, Pill, Users, X} from 'lucide-vue-next'

export interface FiltrosAgenda {
  ordenacao: string
  turno: string
  statusFarmacia: string[]
  gruposInfusao: string[]
  esconderRemarcados: boolean
}

const props = defineProps<{
  modelValue: FiltrosAgenda
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: FiltrosAgenda): void
  (e: 'reset'): void
}>()

const isExpanded = ref(false)

const filtros = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const toggleFilter = (field: 'turno' | 'statusFarmacia' | 'gruposInfusao', value: string) => {
  const current = [...props.modelValue[field]]
  const index = current.indexOf(value)
  if (index === -1) current.push(value)
  else current.splice(index, 1)

  emit('update:modelValue', {...props.modelValue, [field]: current})
}

const updateField = (field: keyof FiltrosAgenda, value: any) => {
  emit('update:modelValue', {...props.modelValue, [field]: value})
}

const activeCount = computed(() => {
  let c = 0
  if (filtros.value.turno != 'todos') c++
  if (filtros.value.statusFarmacia.length > 0) c++
  if (filtros.value.gruposInfusao.length > 0) c++
  if (!filtros.value.esconderRemarcados) c++
  if (filtros.value.ordenacao !== 'grupo_asc') c++
  return c
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between pb-2">
      <div class="flex items-center gap-2">
        <Button
            class="h-7 w-[200px] p-4"
            size="sm"
            variant="outline"
            @click="isExpanded = !isExpanded"
        >
          <div class="flex items-center gap-2">
            <Filter class="h-4 w-4 text-gray-500"/>
            <span class="text-sm font-medium text-gray-700">Filtros e Ordenação</span>
          </div>
          <ChevronUp v-if="isExpanded" class="h-4 w-4"/>
          <ChevronDown v-else class="h-4 w-4"/>
        </Button>

        <Button
            v-if="activeCount > 0"
            class="h-7 text-xs text-muted-foreground hover:text-red-600"
            size="sm"
            variant="ghost"
            @click="emit('reset')"
        >
          <X/>
          Limpar Filtros
        </Button>
      </div>
    </div>

    <Transition
        enter-active-class="animate-in slide-in-from-top-2 fade-in duration-200"
        leave-active-class="animate-out slide-out-to-top-2 fade-out duration-200"
    >
      <div v-if="isExpanded" class="flex flex-wrap gap-3 ">
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button class="w-[160px] justify-between bg-white" size="sm" variant="outline">
            <span class="flex items-center gap-2 text-xs text-gray-600">
              <ArrowUpDown class="h-3.5 w-3.5"/>
              <span class="truncate">
                {{
                  filtros.ordenacao === 'grupo_asc' ? 'Duração (C → L)' :
                  filtros.ordenacao === 'grupo_desc' ? 'Duração (L → C)' :
                  filtros.ordenacao === 'horario' ? 'Horário' : 'Status'
                }}
              </span>
            </span>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Ordenar por</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem
                :checked="filtros.ordenacao === 'grupo_asc'"
                @select="updateField('ordenacao', 'grupo_asc')"
            >
              Duração Asc.
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.ordenacao === 'grupo_desc'"
                @select="updateField('ordenacao', 'grupo_desc')"
            >
              Duração Desc.
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.ordenacao === 'horario'"
                @select="updateField('ordenacao', 'horario')"
            >
              Horário
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.ordenacao === 'status'"
                @select="updateField('ordenacao', 'status')"
            >
              Status
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button :class="{'border-blue-300 bg-blue-50': filtros.turno != 'todos'}"
                    class="w-[130px] justify-between bg-white" size="sm"
                    variant="outline"
            >
            <span class="flex items-center gap-2 text-xs text-gray-600">
              <Clock class="h-3.5 w-3.5"/>
              {{ filtros.turno == 'todos' ? 'Turno' : `${filtros.turno == 'manha' ? 'Manhã' : 'Tarde'}`}}
            </span>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Filtrar Turno</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem
                :checked="filtros.turno === 'todos'"
                @select.prevent="updateField('turno', 'todos')"
            >
              Todos
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.turno === 'manha'"
                @select.prevent="updateField('turno', 'manha')"
            >
              Manhã
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.turno === 'tarde'"
                @select.prevent="updateField('turno', 'tarde')"
            >
              Tarde
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
                :class="{'border-blue-300 bg-blue-50': filtros.gruposInfusao.length > 0}"
                class="w-[140px] justify-between bg-white" size="sm"
                variant="outline"
            >
            <span class="flex items-center gap-2 text-xs text-gray-600">
              <Users class="h-3.5 w-3.5"/>
              {{ filtros.gruposInfusao.length ? `${filtros.gruposInfusao.length} Grupos` : 'Duração' }}
            </span>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Grupo de Infusão</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem
                :checked="filtros.gruposInfusao.includes('rapido')"
                @select.prevent="toggleFilter('gruposInfusao', 'rapido')"
            >
              <span class="w-2 h-2 rounded-full bg-blue-500 mr-2"></span> Rápida (&lt;30m)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.gruposInfusao.includes('medio')"
                @select.prevent="toggleFilter('gruposInfusao', 'medio')"
            >
              <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span> Média (30m-2h)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.gruposInfusao.includes('longo')"
                @select.prevent="toggleFilter('gruposInfusao', 'longo')"
            >
              <span class="w-2 h-2 rounded-full bg-amber-500 mr-2"></span> Longa (2h-4h)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.gruposInfusao.includes('extra_longo')"
                @select.prevent="toggleFilter('gruposInfusao', 'extra_longo')"
            >
              <span class="w-2 h-2 rounded-full bg-rose-600 mr-2"></span> Extra Longa (&gt;4h)
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
                :class="{'border-blue-300': filtros.statusFarmacia.length > 0}"
                class="w-[140px] justify-between bg-white" size="sm"
                variant="outline"
            >
            <span class="flex items-center gap-2 text-xs text-gray-600">
              <Pill class="h-3.5 w-3.5"/>
              {{ filtros.statusFarmacia.length ? `${filtros.statusFarmacia.length} Status` : 'Farmácia' }}
            </span>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Status Farmácia</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem
                :checked="filtros.statusFarmacia.includes('pendente')"
                @select.prevent="toggleFilter('statusFarmacia', 'pendente')"
            >
              Pendente
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.statusFarmacia.includes('em-preparacao')"
                @select.prevent="toggleFilter('statusFarmacia', 'em-preparacao')"
            >
              Em Preparação
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.statusFarmacia.includes('pronta')"
                @select.prevent="toggleFilter('statusFarmacia', 'pronta')"
            >
              Pronta
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.statusFarmacia.includes('enviada')"
                @select.prevent="toggleFilter('statusFarmacia', 'enviada')"
            >
              Enviada
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button
            :class="{'border-blue-300': filtros.esconderRemarcados}"
            class="w-[122px] justify-between transition-colors" size="sm"
            variant="outline"
            @click="updateField('esconderRemarcados', !filtros.esconderRemarcados)"
        >
        <span class="flex items-center gap-2 text-xs text-gray-600">
          <component
              :is="filtros.esconderRemarcados ? EyeOff : Eye"
              class="h-3.5 w-3.5"
          />
          Remarcados
        </span>
        </Button>

      </div>
    </Transition>
  </div>
</template>