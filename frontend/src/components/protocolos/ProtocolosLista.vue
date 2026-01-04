<script lang="ts" setup>
import {computed, ref} from 'vue'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Badge} from '@/components/ui/badge'
import {Ban, Beaker, CheckCircle2, Clock, Edit, Eye, Search, XCircle} from 'lucide-vue-next'

const props = defineProps<{
  protocolos: any[]
}>()

const emit = defineEmits<{
  (e: 'edit', protocolo: any): void
  (e: 'details', protocolo: any): void
  (e: 'toggleStatus', protocolo: any): void
}>()

const searchTerm = ref('')
const statusFilter = ref<'todos' | 'ativos' | 'inativos'>('todos')
const restricaoDiaFilter = ref<'todos' | 'com' | 'sem'>('todos')
const grupoInfusaoFilter = ref<'todos' | 'rapido' | 'medio' | 'longo'>('todos')

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

const filteredProtocolos = computed(() => {
  return props.protocolos.filter(p => {
    const matchesSearch = p.nome.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
        p.indicacao.toLowerCase().includes(searchTerm.value.toLowerCase())
    if (!matchesSearch) return false

    if (statusFilter.value === 'ativos' && !p.ativo) return false
    if (statusFilter.value === 'inativos' && p.ativo) return false

    const temRestricao = p.diasSemanaPermitidos && p.diasSemanaPermitidos.length > 0
    if (restricaoDiaFilter.value === 'com' && !temRestricao) return false
    if (restricaoDiaFilter.value === 'sem' && temRestricao) return false

    let grupo = p.grupoInfusao
    if (!grupo) {
      grupo = inferirGrupoInfusao(p.duracao)
    }
    return !(grupoInfusaoFilter.value !== 'todos' && grupo !== grupoInfusaoFilter.value);
  })
})
</script>

<template>
  <div class="space-y-6">
    <Card>
      <CardContent class="pt-6 space-y-4">
        <div class="relative w-full">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"/>
          <Input v-model="searchTerm" class="pl-10" placeholder="Buscar por nome ou indicação..."/>
        </div>

        <div class="flex flex-wrap gap-4">
          <div class="flex items-center gap-2">
            <Label class="whitespace-nowrap">Status:</Label>
            <div class="flex gap-1">
              <Button :variant="statusFilter === 'todos' ? 'default' : 'outline'" size="sm"
                      @click="statusFilter = 'todos'">Todos
              </Button>
              <Button :variant="statusFilter === 'ativos' ? 'default' : 'outline'" size="sm"
                      @click="statusFilter = 'ativos'">Ativos
              </Button>
              <Button :variant="statusFilter === 'inativos' ? 'default' : 'outline'" size="sm"
                      @click="statusFilter = 'inativos'">Inativos
              </Button>
            </div>
          </div>

          <div class="h-8 w-px bg-gray-200 mx-2 hidden md:block"></div>

          <div class="flex items-center gap-2">
            <Label class="whitespace-nowrap">Restrição:</Label>
            <div class="flex gap-1">
              <Button :variant="restricaoDiaFilter === 'todos' ? 'default' : 'outline'" size="sm"
                      @click="restricaoDiaFilter = 'todos'">Todos
              </Button>
              <Button :variant="restricaoDiaFilter === 'com' ? 'default' : 'outline'" size="sm"
                      @click="restricaoDiaFilter = 'com'">Com
              </Button>
              <Button :variant="restricaoDiaFilter === 'sem' ? 'default' : 'outline'" size="sm"
                      @click="restricaoDiaFilter = 'sem'">Sem
              </Button>
            </div>
          </div>

          <div class="h-8 w-px bg-gray-200 mx-2 hidden md:block"></div>

          <div class="flex items-center gap-2">
            <Label class="whitespace-nowrap">Tempo:</Label>
            <div class="flex gap-1">
              <Button :variant="grupoInfusaoFilter === 'todos' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'todos'">Todos
              </Button>
              <Button :variant="grupoInfusaoFilter === 'rapido' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'rapido'">&lt; 2h
              </Button>
              <Button :variant="grupoInfusaoFilter === 'medio' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'medio'">2-4h
              </Button>
              <Button :variant="grupoInfusaoFilter === 'longo' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'longo'">&gt; 4h
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card v-for="p in filteredProtocolos" :key="p.id" :class="!p.ativo ? 'opacity-70 bg-gray-50' : ''">
        <CardHeader class="p-5 pb-3">
          <div class="flex justify-between items-start gap-4">
            <div class="overflow-hidden">
              <CardTitle :title="p.nome" class="flex items-center gap-2 text-lg"> {{ p.nome }}
                <CheckCircle2 v-if="p.ativo" class="h-4 w-4 text-green-600 flex-shrink-0"/>
                <XCircle v-else class="h-4 w-4 text-gray-400 flex-shrink-0"/>
              </CardTitle>
              <CardDescription :title="p.indicacao" class="text-sm mt-1">{{ p.indicacao }}</CardDescription>
            </div>

            <div class="flex gap-1 flex-shrink-0">
              <Button class="h-8 w-8" size="icon" variant="ghost" @click="emit('details', p)">
                <Eye class="h-4 w-4"/>
              </Button>
              <Button class="h-8 w-8" size="icon" variant="ghost" @click="emit('edit', p)">
                <Edit class="h-4 w-4"/>
              </Button>
              <Button class="h-8 w-8 text-orange-500 hover:text-orange-600 hover:bg-orange-50" size="icon"
                      title="Desativar/Ativar"
                      variant="ghost" @click="emit('toggleStatus', p)">
                <Ban class="h-4 w-4"/>
              </Button>
            </div>

          </div>
        </CardHeader>

        <CardContent class="p-5 pt-0 space-y-3">
          <div class="flex items-center gap-4 text-sm text-gray-600 mt-2">
            <div class="flex items-center gap-1">
              <Clock class="h-4 w-4"/>
              {{ p.duracao }} min
            </div>
            <div class="flex items-center gap-1">
              <Beaker class="h-4 w-4"/>
              {{ p.medicamentos.length }} meds
            </div>
          </div>

          <div v-if="p.diasSemanaPermitidos && p.diasSemanaPermitidos.length > 0"
               class="text-xs text-orange-600 font-medium">
            Restrito: {{
              p.diasSemanaPermitidos.map((d: number) => diasSemanaOptions.find(o => o.value === d)?.label).join(', ')
            }}
          </div>

          <div class="flex flex-wrap gap-1.5 h-14 overflow-hidden content-start">
            <Badge v-for="(m, idx) in p.medicamentos.slice(0, 4)" :key="idx" class="px-2 py-0.5" variant="secondary">
              {{ m.nome }}
            </Badge>
            <span v-if="p.medicamentos.length > 4" class="text-xs text-gray-500 self-center font-medium pl-1">
              +{{ p.medicamentos.length - 4 }}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>