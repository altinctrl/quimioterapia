<script lang="ts" setup>
import {computed, ref} from 'vue'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {Clock, Edit, Hash, Layers, Repeat, XCircle} from 'lucide-vue-next'
import {diasSemanaOptions} from "@/constants/constProtocolos.ts";
import ProtocolosListaControles, {type ProtocoloFiltros} from "@/components/ajustes/ProtocolosListaControles.vue";

const props = defineProps<{
  diasFuncionamento: number[],
  protocolos: any[]
}>()

const emit = defineEmits<{
  (e: 'criar'): void
  (e: 'importar', lista: any[], ignored: number): void
  (e: 'edit', protocolo: any): void
  (e: 'details', protocolo: any): void
  (e: 'toggleStatus', protocolo: any): void
}>()

const searchTerm = ref('')
const filtros = ref<ProtocoloFiltros>({
  sortOrder: 'nome',
  status: 'todos',
  restricao: 'todos',
  grupoInfusao: ['rapido', 'medio', 'longo', 'extra_longo']
})

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
  let result = props.protocolos.filter(p => {
    const matchesSearch = p.nome.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
        (p.indicacao && p.indicacao.toLowerCase().includes(searchTerm.value.toLowerCase()))
    if (!matchesSearch) return false

    if (filtros.value.status === 'ativos' && !p.ativo) return false
    if (filtros.value.status === 'inativos' && p.ativo) return false

    const {isRestricted} = checkRestricao(p)
    if (filtros.value.restricao === 'com' && !isRestricted) return false
    if (filtros.value.restricao === 'sem' && isRestricted) return false

    const grupo = p.grupoInfusao || inferirGrupoInfusao(p.tempoTotalMinutos || 0)
    return filtros.value.grupoInfusao.includes(grupo);
  })

  return result.sort((a: any, b: any) => {
    if (filtros.value.sortOrder === 'duracao') {
      return (a.tempoTotalMinutos || 0) - (b.tempoTotalMinutos || 0)
    }
    return a.nome.localeCompare(b.nome)
  })
})
</script>

<template>
  <div class="space-y-6">
    <Card>
      <CardContent class="pt-6">
        <ProtocolosListaControles
            v-model:filtros="filtros"
            v-model:searchTerm="searchTerm"
            @criar="emit('criar')"
            @importar="(dados, ignored) => emit('importar', dados, ignored)"
        />
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
