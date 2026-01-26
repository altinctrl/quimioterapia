<script lang="ts" setup>
import {Badge} from '@/components/ui/badge'
import {HoverCard, HoverCardContent, HoverCardTrigger} from '@/components/ui/hover-card'
import {formatDiasCiclo, getUnidadeFinal} from "@/utils/prescricaoUtils.ts"
import {DetalhesMedicamento} from "@/types/protocoloTypes.ts";
import {useAppStore} from "@/stores/app.ts";

defineProps<{
  dados: DetalhesMedicamento
}>()

const appStore = useAppStore()

const isValido = (nome: string | undefined) => {
  if (!nome) return false
  return appStore.parametros.diluentes?.includes(nome)
}
</script>

<template>
  <div class="w-full">
    <div class="flex justify-between items-start mb-1">
      <span class="text-lg font-bold text-gray-800">{{ dados.medicamento }}</span>
    </div>

    <div class="text-sm text-gray-600 flex flex-wrap gap-x-4 gap-y-1 mb-2">
      <span>
        <strong>Dose:</strong> {{ dados.doseReferencia }} {{ dados.unidade }}
        <span v-if="dados.doseMaxima" class="font-bold text-red-800">
          (Máx: {{ dados.doseMaxima + getUnidadeFinal(dados.unidade) }})
        </span>
      </span>
      <span><strong>Via:</strong> {{ dados.via }}</span>
      <span><strong>Tempo:</strong> {{ dados.tempoMinutos }} minutos</span>
      <span><strong>Dias do Ciclo:</strong> {{ formatDiasCiclo(dados.diasDoCiclo) }}</span>
    </div>

    <div v-if="dados.configuracaoDiluicao"
         class="flex items-center gap-2 text-sm border-t border-gray-200 pt-2 mt-2">
      <span class="text-gray-500">Diluente:</span>
      <span
          :class="isValido(dados.configuracaoDiluicao?.selecionada) ? 'text-gray-700' : 'text-red-600'"
          :title="dados.configuracaoDiluicao?.selecionada"
          class="font-medium truncate flex items-center gap-1"
      >
        {{ dados.configuracaoDiluicao?.selecionada || 'Não especificado' }}
        <span
            v-if="dados.configuracaoDiluicao?.selecionada && !isValido(dados.configuracaoDiluicao?.selecionada)"
            class="text-[10px] text-red-500 font-bold bg-red-50 px-1 rounded ml-auto"
        >
          INDISPONÍVEL
        </span>
      </span>

      <HoverCard v-if="dados.configuracaoDiluicao?.opcoesPermitidas && dados.configuracaoDiluicao?.opcoesPermitidas?.length > 1">
        <HoverCardTrigger as-child>
          <Badge class="cursor-pointer h-5 px-1.5" variant="outline">
            +{{ dados.configuracaoDiluicao.opcoesPermitidas.length - 1 }} opções
          </Badge>
        </HoverCardTrigger>
        <HoverCardContent class="min-w-[16rem] w-auto p-3">
          <div class="space-y-2">
            <h4 class="text-xs font-semibold text-gray-500 uppercase">Diluentes Permitidos</h4>
            <ul class="list-disc list-inside text-xs space-y-1 text-gray-700">
              <li v-for="dil in dados.configuracaoDiluicao.opcoesPermitidas" :key="dil"
                  :class="!isValido(dil) ? 'text-red-500 line-through' : ''">
                {{ dil }}
                <span v-if="dil === dados.configuracaoDiluicao.selecionada" class="text-blue-500 font-bold">
                  (Padrão)
                </span>
                <span v-if="!isValido(dil)" class="text-[10px] text-red-500 font-bold bg-red-50 px-1 rounded ml-auto">
                  INDISPONÍVEL
                </span>
              </li>
            </ul>
          </div>
        </HoverCardContent>
      </HoverCard>
    </div>

    <div v-if="dados.notasEspecificas"
         class="mt-2 text-xs text-orange-900 bg-orange-50 p-1.5 rounded border border-orange-100">
      {{ dados.notasEspecificas }}
    </div>
  </div>
</template>
