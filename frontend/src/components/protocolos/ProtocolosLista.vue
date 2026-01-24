<script lang="ts" setup>
import {computed, ref} from 'vue'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Badge} from '@/components/ui/badge'
import {Clock, Edit, FileUp, Hash, Layers, Plus, Repeat, Search, XCircle} from 'lucide-vue-next'
import {useProtocoloImport} from "@/composables/protocolos/useProtocoloImport";
import {diasSemanaOptions} from "@/utils/protocoloConstants";

const props = defineProps<{
  diasFuncionamento: number[],
  protocolos: any[]
}>()

const emit = defineEmits<{
  (e: 'criar') : void
  (e: 'importar', lista: any[], ignored: number): void
  (e: 'edit', protocolo: any): void
  (e: 'details', protocolo: any): void
  (e: 'toggleStatus', protocolo: any): void
}>()

const searchTerm = ref('')
const statusFilter = ref<'todos' | 'ativos' | 'inativos'>('todos')
const restricaoDiaFilter = ref<'todos' | 'com' | 'sem'>('todos')
const grupoInfusaoFilter = ref<'todos' | 'rapido' | 'medio' | 'longo' | 'extra_longo'>('todos')

const inferirGrupoInfusao = (duracao: number): 'rapido' | 'medio' | 'longo' | 'extra_longo' => {
  if (duracao <= 30) return 'rapido'
  if (duracao <= 120) return 'medio'
  if (duracao <= 240) return 'longo'
  return 'extra_longo'
}

const checkRestricao = (protocolo: any) => {
  const diasPermitidos = protocolo.diasSemanaPermitidos || []
  const diasClinica = props.diasFuncionamento || []
  if (!diasPermitidos.length || !diasClinica.length) {
    return {isRestricted: false, text: 'Permitido todos os dias.'}
  }

  const diasFaltantes = diasClinica.filter((d: number) => !diasPermitidos.includes(d))
  if (diasFaltantes.length === 0) {
    return {isRestricted: false, text: 'Permitido todos os dias.'}
  }

  const labels = diasPermitidos
      .sort((a: number, b: number) => a - b)
      .map((d: number) => diasSemanaOptions.find(opt => opt.value === d)?.label)
      .filter(Boolean)
      .join(', ')

  return {isRestricted: true, text: `Permitido nos dias: ${labels}.`}
}

const filteredProtocolos = computed(() => {
  return props.protocolos.filter(p => {
    const matchesSearch = p.nome.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
        (p.indicacao && p.indicacao.toLowerCase().includes(searchTerm.value.toLowerCase()))
    if (!matchesSearch) return false

    if (statusFilter.value === 'ativos' && !p.ativo) return false
    if (statusFilter.value === 'inativos' && p.ativo) return false

    const {isRestricted} = checkRestricao(p)
    if (restricaoDiaFilter.value === 'com' && !isRestricted) return false
    if (restricaoDiaFilter.value === 'sem' && isRestricted) return false

    let grupo = p.grupoInfusao
    if (!grupo) {
      grupo = inferirGrupoInfusao(p.tempoTotalMinutos || 0)
    }
    return !(grupoInfusaoFilter.value !== 'todos' && grupo !== grupoInfusaoFilter.value);
  })
})

const { handleFileUpload, isProcessing, ignored } = useProtocoloImport()
const fileInput = ref<HTMLInputElement | null>(null)

const onFileChange = async (e: Event) => {
  const dados = await handleFileUpload(e)
  if (dados) emit('importar', dados, ignored.value)
}
</script>

<template>
  <div class="space-y-6">
    <Card>
      <CardContent class="pt-6 space-y-4">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="relative flex-1">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"/>
            <Input v-model="searchTerm" class="pl-10" placeholder="Buscar por nome ou indicação..."/>
          </div>

          <div class="flex gap-2">
            <Button class="flex items-center justify-end gap-3" @click.stop="emit('criar')">
              <Plus class="h-4 w-4"/>
              Criar
            </Button>

            <Button :disabled="isProcessing" class="flex items-center justify-end gap-3" variant="outline"
                    @click="fileInput?.click()">
              <FileUp class="h-4 w-4"/>
              Importar
            </Button>
            <input ref="fileInput" accept=".json" class="hidden" type="file" @change="onFileChange"/>
          </div>
        </div>

        <div class="flex flex-wrap gap-1">
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
                      @click="grupoInfusaoFilter = 'rapido'">&lt; 30min
              </Button>
              <Button :variant="grupoInfusaoFilter === 'medio' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'medio'">30min-2h
              </Button>
              <Button :variant="grupoInfusaoFilter === 'longo' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'longo'">2h-4h
              </Button>
              <Button :variant="grupoInfusaoFilter === 'extra_longo' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'extra_longo'">&gt; 4h
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      <Card
          v-for="p in filteredProtocolos"
          :key="p.id"
          :class="!p.ativo ? 'opacity-70 bg-gray-50' : ''"
          class="cursor-pointer hover:shadow-md transition-shadow"
          @click="emit('details', p)">
        <CardHeader class="p-5 pb-3">
          <div class="flex justify-between items-start gap-4">
            <div class="overflow-hidden">
              <CardTitle :title="p.nome" class="flex items-center gap-2 text-lg">
                <XCircle v-if="!p.ativo" class="h-4 w-4 text-gray-400 flex-shrink-0"/>
                {{ p.nome }}
              </CardTitle>
              <CardDescription :title="p.indicacao" class="text-sm mt-1">
                {{ p.indicacao || 'Sem indicação' }}
              </CardDescription>
            </div>

            <Button class="h-8 w-8" size="icon" variant="ghost" @click.stop="emit('edit', p)">
              <Edit class="h-4 w-4"/>
            </Button>
          </div>
        </CardHeader>

        <CardContent class="p-5 pt-0 space-y-3">
          <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-600 mt-2">
            <div class="flex items-center gap-1" title="Total de Ciclos">
              <Hash class="h-4 w-4"/>
              {{ p.totalCiclos ? `${p.totalCiclos} ciclos` : 'Indef.' }}
            </div>
            <div class="flex items-center gap-1" title="Duração do Ciclo">
              <Repeat class="h-4 w-4"/>
              {{ p.duracaoCicloDias }} dias
            </div>
            <div class="flex items-center gap-1" title="Tempo na Cadeira">
              <Clock class="h-4 w-4"/>
              {{ p.tempoTotalMinutos || 0 }} min
            </div>
            <div class="flex items-center gap-1" title="Templates/Variantes">
              <Layers class="h-4 w-4"/>
              {{ p.templatesCiclo?.length || 0 }} variantes
            </div>
          </div>

          <div :class="checkRestricao(p).isRestricted ? 'text-orange-600' : 'text-muted-foreground'"
               class="text-xs font-medium h-4 flex items-center">
            {{ checkRestricao(p).text }}
          </div>

          <div v-if="p.fase || p.linha" class="flex flex-wrap gap-2 pt-1">
            <Badge v-if="p.fase" class="bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100" variant="secondary">
              {{ p.fase }}
            </Badge>
            <Badge v-if="p.linha" class="border-gray-300 text-gray-600" variant="outline">
              {{ p.linha }}ª Linha
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
