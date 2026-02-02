<script lang="ts" setup>
import {toRefs} from 'vue'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {Clock, Edit, Hash, Layers, Repeat, XCircle} from 'lucide-vue-next'
import ProtocolosListaControles from "@/components/ajustes/ProtocolosListaControles.vue"
import {useProtocoloLista} from "@/composables/useProtocoloLista.ts"
import type {Protocolo} from "@/types/typesProtocolo.ts"

const props = defineProps<{
  diasFuncionamento: number[],
  protocolos: Protocolo[]
}>()

const emit = defineEmits<{
  (e: 'criar'): void
  (e: 'importar', lista: any[], ignored: number): void
  (e: 'edit', protocolo: Protocolo): void
  (e: 'details', protocolo: Protocolo): void
}>()

const {protocolos, diasFuncionamento} = toRefs(props)

const {
  searchTerm,
  filtros,
  filteredProtocolos,
  checkRestricao
} = useProtocoloLista(protocolos, diasFuncionamento)
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
            <div class="flex items-center gap-1" title="Modelo">
              <Layers class="h-4 w-4"/>
              {{ p.templatesCiclo?.length || 0 }} modelos
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
