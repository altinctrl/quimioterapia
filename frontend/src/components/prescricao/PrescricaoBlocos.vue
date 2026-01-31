<script lang="ts" setup>
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {AlertCircle, Info} from 'lucide-vue-next'
import PrescricaoItem from './PrescricaoItem.vue'
import {Card} from "@/components/ui/card"
import {getCategoriaColor, getCategoriaLabel} from "@/utils/utilsPrescricao.ts";

const props = defineProps<{
  blocos: any[]
  dadosPaciente: any
  errors?: Record<string, string>
}>()

const emit = defineEmits(['update:blocos'])

const getGrupoError = (bIndex: number, iIndex: number) => {
  if (!props.errors) return undefined;
  return props.errors[`blocos[${bIndex}].itens[${iIndex}].itemSelecionado`];
}

const getItemErrors = (bIndex: number, iIndex: number, isGroup = false) => {
  if (!props.errors) return {};
  const prefix = `blocos[${bIndex}].itens[${iIndex}]${isGroup ? '.itemSelecionado' : ''}.`;
  const result: Record<string, string> = {};
  Object.entries(props.errors).forEach(([key, message]) => {
    if (key.startsWith(prefix)) {
      const fieldName = key.replace(prefix, '');
      result[fieldName] = message;
    }
  });
  return result;
}

const hasBlockError = (bIndex: number) => {
  if (!props.errors) return false;
  if (typeof props.errors?.['blocos'] === 'string') return true;
  return Object.keys(props.errors).some(key =>
      key.startsWith(`blocos[${bIndex}]`) && !key.includes('.itens')
  );
}

const atualizarBlocos = (bIndex: number, iIndex: number, novoItem: any) => {
  const novosBlocos = JSON.parse(JSON.stringify(props.blocos))
  novosBlocos[bIndex].itens[iIndex] = novoItem
  emit('update:blocos', novosBlocos)
}

const onSelecionarMedicamento = (bIndex: number, iIndex: number, nomeMedicamento: string) => {
  const novosBlocos = JSON.parse(JSON.stringify(props.blocos))
  const itemDoLoop = novosBlocos[bIndex].itens[iIndex]
  const opcao = itemDoLoop.opcoes.find((op: any) => op.medicamento === nomeMedicamento);

  if (opcao) {
    itemDoLoop.itemSelecionado = {
      ...opcao,
      percentualAjuste: 100,
      doseTeorica: 0,
      doseFinal: 0,
      tipo: 'medicamento_unico',
      pisoCreatinina: opcao.pisoCreatinina || undefined,
      tetoGfr: opcao.tetoGfr || undefined,
      diluicaoFinal: '',
      configuracaoDiluicao: opcao.configuracaoDiluicao || undefined,
    };
    emit('update:blocos', novosBlocos)
  }
}
</script>

<template>
  <Card class="p-6">
    <div class="space-y-6">
      <div class="border rounded-md p-3 flex items-center mb-2 gap-3">
        <Info class="h-5 w-5 shrink-0"/>
        <div class="text-sm flex flex-col">
          <span>Os blocos abaixo representam a <strong>sequência</strong> exata de administração.</span>
          <span>Itens dentro do mesmo bloco são administrados <strong>concomitantemente</strong> (via Y).</span>
        </div>
      </div>

      <div
          v-if="typeof props.errors?.['blocos'] === 'string'"
          class="bg-red-50 border border-red-500 p-4 rounded-lg flex items-center gap-3 animate-in shake"
      >
        <AlertCircle class="h-5 w-5 text-red-600 shrink-0"/>
        <div class="flex flex-col">
          <span class="text-sm text-red-800 font-bold">Erro na Estrutura dos Blocos</span>
          <span class="text-xs text-red-700">{{ errors?.blocos }}</span>
        </div>
      </div>

      <div v-for="(bloco, bIndex) in blocos" :key="bIndex"
           :class="[hasBlockError(bIndex) ? 'border-red-500 ring-2 ring-red-500/20' : getCategoriaColor(bloco.categoria)]"
           class="border rounded-xl overflow-hidden shadow-sm"
      >
        <div class="bg-gray-50/80 px-4 py-3 border-b flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div
                class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-900 text-white font-bold shadow-sm">
              {{ bloco.ordem }}
            </div>
            <div>
              <h3 class="font-bold text-gray-800 uppercase text-sm tracking-wide">
                {{ getCategoriaLabel(bloco.categoria) }}
              </h3>
            </div>
          </div>
        </div>

        <div class="p-4 space-y-4">
          <div v-for="(item, iIndex) in bloco.itens" :key="item.idItem || iIndex">

            <div
                v-if="item.tipo === 'grupo_alternativas'"
                :class="getGrupoError(bIndex, iIndex as number) ? 'border-red-500' : ''"
                class="border rounded-lg p-4"
            >
              <div class="flex items-center gap-2 mb-3">
                <span class="font-bold text-gray-800 text-sm">{{ item.labelGrupo }}</span>
              </div>

              <Select
                  :model-value="item.itemSelecionado?.medicamento || ''"
                  @update:model-value="(val) => onSelecionarMedicamento(bIndex, iIndex as number, val as string)"
              >
                <SelectTrigger
                    :class="getGrupoError(bIndex, iIndex as number) ? 'border-red-500 text-red-700' : ''">
                  <SelectValue placeholder="Selecione a medicação..."/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="(opt, optIdx) in item.opcoes" :key="optIdx" :value="opt.medicamento">
                    {{ opt.medicamento }} ({{ opt.doseReferencia }} {{ opt.unidade }})
                  </SelectItem>
                </SelectContent>
              </Select>

              <span v-if="getGrupoError(bIndex, iIndex as number)" class="text-xs text-red-600 font-bold mt-1 block">
                {{ getGrupoError(bIndex, iIndex as number) }}
              </span>

              <div v-if="item.itemSelecionado"
                   class="mt-4 pl-4 border-l-2  animate-in fade-in slide-in-from-top-2">
                <PrescricaoItem
                    :key="item.itemSelecionado.medicamento"
                    :dados-paciente="dadosPaciente"
                    :errors="getItemErrors(bIndex, iIndex as number, true)"
                    :item="item.itemSelecionado"
                    @update:item="(novoItemSelecionado) => {
                        const novoGrupo = { ...item, itemSelecionado: novoItemSelecionado };
                        atualizarBlocos(bIndex, iIndex as number, novoGrupo);
                    }"
                />
              </div>
            </div>

            <div v-else>
              <PrescricaoItem
                  :key="item.idItem || iIndex"
                  :dados-paciente="dadosPaciente"
                  :errors="getItemErrors(bIndex, iIndex as number, false)"
                  :item="item"
                  @update:item="(novoItem) => atualizarBlocos(bIndex, iIndex as number, novoItem)"
              />
            </div>
          </div>

          <div v-if="!bloco.itens || bloco.itens.length === 0" class="text-center text-gray-400 text-sm italic py-2">
            Bloco sem itens.
          </div>
        </div>
      </div>
    </div>
  </Card>
</template>
