<script lang="ts" setup>
import {computed, ref} from 'vue'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {ArrowUpDown, CalendarOff, ChevronDown, Clock, FileUp, Filter, Plus, Search, X} from 'lucide-vue-next'
import {useProtocoloImportacao} from "@/composables/useProtocoloImportacao.ts";

export interface ProtocoloFiltros {
  sortOrder: 'nome' | 'duracao'
  status: 'todos' | 'ativos' | 'inativos'
  restricao: 'todos' | 'com' | 'sem'
  grupoInfusao: string[]
}

const props = defineProps<{
  searchTerm: string
  filtros: ProtocoloFiltros
}>()

const emit = defineEmits<{
  (e: 'update:searchTerm', value: string): void
  (e: 'update:filtros', value: ProtocoloFiltros): void
  (e: 'criar'): void
  (e: 'importar', lista: any[], ignored: number): void
}>()

const isFiltersExpanded = ref(false)

const localSearch = computed({
  get: () => props.searchTerm,
  set: (val) => emit('update:searchTerm', val)
})

const updateFiltro = (campo: keyof ProtocoloFiltros, valor: any) => {
  emit('update:filtros', {...props.filtros, [campo]: valor})
}

const hasActiveFilters = computed(() => {
  const todosSelecionados = props.filtros.grupoInfusao.length === 4
  return props.filtros.status !== 'todos' ||
      props.filtros.restricao !== 'todos' ||
      !todosSelecionados ||
      props.filtros.sortOrder !== 'nome'
})

const clearFilters = () => {
  emit('update:filtros', {
    sortOrder: 'nome',
    status: 'todos',
    restricao: 'todos',
    grupoInfusao: ['rapido', 'medio', 'longo', 'extra_longo']
  })
}

const toggleGrupo = (grupo: string) => {
  const atual = [...props.filtros.grupoInfusao]
  const index = atual.indexOf(grupo)
  if (index === -1) atual.push(grupo)
  else atual.splice(index, 1)
  updateFiltro('grupoInfusao', atual)
}

const {handleFileUpload, isProcessing, ignored} = useProtocoloImportacao()
const fileInput = ref<HTMLInputElement | null>(null)

const onFileChange = async (e: Event) => {
  const dados = await handleFileUpload(e)
  if (dados) emit('importar', dados, ignored.value)
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col md:flex-row gap-2">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"/>
        <Input v-model="localSearch" class="pl-10" placeholder="Buscar por nome ou indicação..."/>
      </div>

      <Button
          :class="{'bg-blue-50 border-blue-200 text-blue-700': isFiltersExpanded || hasActiveFilters}"
          class="shrink-0"
          size="icon"
          variant="outline"
          @click="isFiltersExpanded = !isFiltersExpanded"
      >
        <Filter class="h-4 w-4"/>
      </Button>

      <Button :disabled="isProcessing" class="flex items-center justify-end gap-3" variant="outline"
              @click="fileInput?.click()">
        <FileUp class="h-4 w-4"/>
        Importar
      </Button>
      <input ref="fileInput" accept=".json" class="hidden" type="file" @change="onFileChange"/>

      <Button class="flex items-center justify-end gap-3" @click.stop="emit('criar')">
        <Plus class="h-4 w-4"/>
        Criar
      </Button>
    </div>

    <Transition
        enter-active-class="animate-in slide-in-from-top-2 fade-in duration-200"
        leave-active-class="animate-out slide-out-to-top-2 fade-out duration-200"
    >
      <div v-if="isFiltersExpanded" class="flex flex-wrap gap-3 justify-end">

        <Button
            v-if="hasActiveFilters"
            class="text-xs text-muted-foreground hover:text-red-600"
            size="sm"
            variant="ghost"
            @click="clearFilters"
        >
          <X class="h-3.5 w-3.5 mr-1"/>
          Limpar
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button class="justify-between bg-white min-w-[140px]" size="sm" variant="outline">
                  <span class="flex items-center gap-2 text-xs text-gray-600">
                    <ArrowUpDown class="h-3.5 w-3.5"/>
                    {{ filtros.sortOrder === 'nome' ? 'Nome (A-Z)' : 'Duração' }}
                  </span>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Ordenar por</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem
                :checked="filtros.sortOrder === 'nome'"
                @select="updateFiltro('sortOrder', 'nome')"
            >
              Nome (A-Z)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.sortOrder === 'duracao'"
                @select="updateFiltro('sortOrder', 'duracao')"
            >
              Duração (Curta → Longa)
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
                :class="{'border-blue-300 bg-blue-50': filtros.status !== 'todos'}"
                class="justify-between bg-white min-w-[120px]"
                size="sm"
                variant="outline"
            >
              <div class="flex items-center gap-2 text-xs text-gray-600">
                <div
                    :class="{'bg-green-500': filtros.status === 'ativos', 'bg-red-400': filtros.status === 'inativos'}"
                    class="h-2 w-2 rounded-full bg-gray-400"
                ></div>
                {{ filtros.status === 'todos' ? 'Status' : (filtros.status === 'ativos' ? 'Ativos' : 'Inativos') }}
              </div>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Filtrar Status</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem
                :checked="filtros.status === 'todos'"
                @select="updateFiltro('status', 'todos')"
            >
              Todos
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.status === 'ativos'"
                @select="updateFiltro('status', 'ativos')"
            >
              Ativos
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.status === 'inativos'"
                @select="updateFiltro('status', 'inativos')"
            >
              Inativos
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
                :class="{'border-blue-300 bg-blue-50': filtros.restricao !== 'todos'}"
                class="justify-between bg-white min-w-[130px]"
                size="sm"
                variant="outline"
            >
                  <span class="flex items-center gap-2 text-xs text-gray-600">
                    <CalendarOff class="h-3.5 w-3.5"/>
                    {{
                      filtros.restricao === 'todos' ? 'Restrição' : (filtros.restricao === 'com' ? 'Com Restrição' : 'Sem Restrição')
                    }}
                  </span>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Restrição de Dias</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem :checked="filtros.restricao === 'todos'"
                                      @select="updateFiltro('restricao', 'todos')">
              Todos
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.restricao === 'com'"
                @select="updateFiltro('restricao', 'com')"
            >
              Com Restrição
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.restricao === 'sem'"
                @select="updateFiltro('restricao', 'sem')"
            >
              Sem Restrição
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
                :class="{'border-blue-300 bg-blue-50': filtros.grupoInfusao.length > 0}"
                class="justify-between bg-white min-w-[130px]"
                size="sm"
                variant="outline"
            >
              <span class="flex items-center gap-2 text-xs text-gray-600">
                <Clock class="h-3.5 w-3.5"/>
                {{
                  filtros.grupoInfusao.length === 4 ? 'Duração (Todos)' : `${filtros.grupoInfusao.length} Selecionados`
                }}
              </span>
              <ChevronDown class="h-3 w-3 opacity-50"/>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Grupo de Infusão</DropdownMenuLabel>
            <DropdownMenuSeparator/>
            <DropdownMenuCheckboxItem
                :checked="filtros.grupoInfusao.includes('rapido')"
                @select.prevent="toggleGrupo('rapido')">
              Rápida (< 30min)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.grupoInfusao.includes('medio')"
                @select.prevent="toggleGrupo('medio')">
              Média (30min-2h)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.grupoInfusao.includes('longo')"

                @select.prevent="toggleGrupo('longo')">
              Longa (2h-4h)
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
                :checked="filtros.grupoInfusao.includes('extra_longo')"
                @select.prevent="toggleGrupo('extra_longo')">
              Extra Longa (> 4h)
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </Transition>
  </div>
</template>
