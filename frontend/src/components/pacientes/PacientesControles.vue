<script lang="ts" setup>
import {computed} from 'vue'
import {Button} from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {ArrowUpDown, ChevronDown, ChevronLeft, ChevronRight, List} from 'lucide-vue-next'

export interface FiltrosPacientes {
  ordenacao: 'nome_asc' | 'nome_desc' | 'registro' | 'recentes'
  perPage: number
}

const props = defineProps<{
  modelValue: FiltrosPacientes
  totalPacientes: number
  page: number
  totalPages: number
}>()

const emit = defineEmits<{
  (e: 'update:page', value: number): void
  (e: 'update:modelValue', value: FiltrosPacientes): void
  (e: 'reset'): void
}>()

const filtros = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const updateField = (field: keyof FiltrosPacientes, value: any) => {
  emit('update:modelValue', {...props.modelValue, [field]: value})
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between pb-2">
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-3">
          <Button
              :disabled="page === 1"
              size="icon"
              variant="outline"
              @click="emit('update:page', page - 1)">
            <ChevronLeft class="h-4 w-4"/>
          </Button>
          <span class="text-sm font-medium mx-2">
              Página {{ page }} de {{ totalPages }}
          </span>
          <Button
              :disabled="page >= totalPages"
              size="icon"
              variant="outline"
              @click="emit('update:page', page + 1)">
            <ChevronRight class="h-4 w-4"/>
          </Button>
        </div>

        <div class="flex items-center gap-4">
          <div class="text-sm text-gray-500">{{ totalPacientes }} Pacientes</div>

          <div class="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button class="justify-between bg-white" size="sm" variant="outline">
            <span class="flex items-center gap-2 text-xs text-gray-600">
              <ArrowUpDown class="h-3.5 w-3.5"/>
              <span class="truncate">
                {{
                  filtros.ordenacao === 'nome_asc' ? 'Nome (A-Z)' :
                  filtros.ordenacao === 'nome_desc' ? 'Nome (Z-A)' :
                  filtros.ordenacao === 'registro' ? 'Prontuário' : 'Mais Recentes'
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
                    :checked="filtros.ordenacao === 'nome_asc'"
                    @select="updateField('ordenacao', 'nome_asc')"
                >
                  Nome (A-Z)
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                    :checked="filtros.ordenacao === 'nome_desc'"
                    @select="updateField('ordenacao', 'nome_desc')"
                >
                  Nome (Z-A)
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                    :checked="filtros.ordenacao === 'registro'"
                    @select="updateField('ordenacao', 'registro')"
                >
                  Nº Prontuário
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                    :checked="filtros.ordenacao === 'recentes'"
                    @select="updateField('ordenacao', 'recentes')"
                >
                  Recém Adicionados
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button
                    class="justify-between bg-white"
                    size="sm"
                    variant="outline"
                >
            <span class="flex items-center gap-2 text-xs text-gray-600">
              <List class="h-3.5 w-3.5"/>
              {{ filtros.perPage }} por página
            </span>
                  <ChevronDown class="h-3 w-3 opacity-50"/>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuLabel>Pacientes por página</DropdownMenuLabel>
                <DropdownMenuSeparator/>
                <DropdownMenuCheckboxItem
                    :checked="filtros.perPage === 10"
                    @select="updateField('perPage', 10)"
                >
                  10
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                    :checked="filtros.perPage === 20"
                    @select="updateField('perPage', 20)"
                >
                  20
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                    :checked="filtros.perPage === 50"
                    @select="updateField('perPage', 50)"
                >
                  50
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                    :checked="filtros.perPage === 100"
                    @select="updateField('perPage', 100)"
                >
                  100
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>
