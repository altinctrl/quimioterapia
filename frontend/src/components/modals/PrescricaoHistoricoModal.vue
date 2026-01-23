<script lang="ts" setup>
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {Separator} from '@/components/ui/separator'
import {Activity, AlertTriangle, Download, FileText} from 'lucide-vue-next'
import {toast} from "vue-sonner";
import api from "@/services/api.ts";
import {getUnidadeFinal} from "@/utils/prescricaoUtils.ts";

const props = defineProps<{
  open: boolean
  prescricao: any
}>()

const emit = defineEmits(['update:open'])

const formatarStatus = (status: string) => {
  const mapa: Record<string, string> = {
    'pendente': 'Pendente',
    'em-curso': 'Em Curso',
    'concluida': 'Concluída',
    'suspensa': 'Suspensa',
    'cancelada': 'Cancelada'
  }
  return mapa[status] || status
}

const getCategoriaLabel = (cat: string) => {
  const map: Record<string, string> = {
    'pre_med': 'Pré-Medicação',
    'qt': 'Terapia',
    'pos_med_hospitalar': 'Pós-Med (Hosp)',
    'pos_med_domiciliar': 'Pós-Med (Casa)',
    'infusor': 'Infusor'
  }
  return map[cat] || cat
}

const formatDiasCiclo = (dias: number[]) => {
  if (!dias || dias.length === 0) return ''
  return dias.map(d => `${d}`).join(', ')
}

const fetchPdfBlob = async () => {
  if (!props.prescricao?.id) throw new Error("ID inválido")
  const response = await api.get(`/api/prescricoes/${props.prescricao.id}/pdf`, {
    responseType: 'blob'
  })
  return new Blob([response.data], {type: 'application/pdf'})
}

const handleBaixar = async () => {
  try {
    toast.info("Baixando PDF...")
    const blob = await fetchPdfBlob()
    const url = window.URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    const nomePaciente = props.prescricao.conteudo?.paciente?.nome || 'paciente'
    link.setAttribute('download', `Prescricao_${nomePaciente}_${props.prescricao.id.slice(0, 8)}.pdf`)

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error(e)
    toast.error("Erro ao baixar PDF.")
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-4xl max-h-[90vh] flex flex-col p-0 gap-0">

      <DialogHeader class="p-6 pb-4 border-b shrink-0 bg-white z-10 rounded-t-lg">
        <div class="flex items-start justify-between gap-4">
          <div>
            <DialogTitle class="flex items-center gap-2 text-xl mb-1">
              <FileText class="h-5 w-5"/>
              Prescrição Médica
            </DialogTitle>
            <DialogDescription v-if="prescricao?.conteudo?.paciente">
              Paciente: <span class="font-medium text-gray-900">{{ prescricao.conteudo.paciente.nome }}</span>
              <span class="mx-2 text-gray-300">|</span>
              Prontuário: {{ prescricao.conteudo.paciente.prontuario }}
            </DialogDescription>
          </div>
          <Badge :variant="prescricao?.status === 'concluida' ? 'default' : 'outline'" class="h-6">
            {{ formatarStatus(prescricao?.status) }}
          </Badge>
        </div>
      </DialogHeader>

      <div class="flex-1 overflow-y-auto min-h-0 w-full p-6 space-y-6 scrollbar-thin scrollbar-thumb-gray-200">

        <div v-if="prescricao" class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg border">
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Data Emissão</span>
            <p class="text-sm font-medium">{{ new Date(prescricao.dataEmissao).toLocaleDateString('pt-BR') }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Protocolo</span>
            <p class="text-sm font-medium">{{ prescricao.conteudo?.protocolo?.nome }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Ciclo</span>
            <p class="text-sm font-medium">{{ prescricao.conteudo?.protocolo?.cicloAtual }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Médico</span>
            <p :title="prescricao.conteudo?.medico?.nome" class="text-sm font-medium truncate">
              {{ prescricao.conteudo?.medico?.nome }}
            </p>
          </div>
        </div>

        <div v-if="prescricao?.conteudo?.paciente">
          <h4 class="text-sm font-medium mb-3 flex items-center gap-2 text-gray-900">
            <Activity class="h-4 w-4 text-gray-900"/>
            Dados Antropométricos
          </h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 border p-4 rounded-lg bg-white shadow-sm">
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Peso</span>
              <span class="font-medium">{{ prescricao.conteudo.paciente.peso }} kg</span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Altura</span>
              <span class="font-medium">{{ prescricao.conteudo.paciente.altura }} cm</span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Sup. Corpórea</span>
              <span class="font-medium">{{ prescricao.conteudo.paciente.sc }} m²</span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Creatinina</span>
              <span class="font-medium">{{ prescricao.conteudo.paciente.creatinina ? prescricao.conteudo.paciente.creatinina + ' mg/dL' : '-' }}</span>
            </div>
          </div>
        </div>

        <Separator/>

        <div v-if="prescricao?.conteudo?.blocos" class="space-y-6">
          <div
              v-for="bloco in prescricao.conteudo.blocos"
              :key="bloco.ordem"
              class="border rounded-lg overflow-hidden shadow-sm"
          >
            <div class="bg-gray-100/80 p-3 flex items-center justify-between gap-3 border-b">
              <div class="flex items-center">
                <div
                    class="flex items-center justify-center w-6 h-6 rounded-full bg-gray-800 text-white text-sm font-bold">
                  {{ bloco.ordem }}
                </div>
                <Badge class="uppercase text-sm tracking-wider font-semibold" variant="secondary">
                  {{ getCategoriaLabel(bloco.categoria) }}
                </Badge>
              </div>

              <div v-if="bloco.itens.length > 1"
                   class="flex items-center gap-1.5 px-2 py-0.5 text-xs font-bold uppercase tracking-wide
                          border rounded bg-blue-50 border-blue-100 text-blue-700">
                Simultâneos (Via Y)
              </div>
            </div>

            <div class="divide-y divide-gray-100 bg-white">
              <div v-for="item in bloco.itens" :key="item.idItem" class="p-4 hover:bg-gray-50/50 transition-colors">
                <div class="flex justify-between items-start">
                  <div class="flex items-center gap-2">
                    <h5 class="text-sm font-bold text-gray-900 uppercase">{{ item.medicamento }}</h5>
                    <span class="text-xs text-gray-500 font-medium">({{ item.via }})</span>
                  </div>
                  <Badge v-if="item.diasDoCiclo?.length" class="text-xs" variant="secondary">
                    Dias: {{ formatDiasCiclo(item.diasDoCiclo) }}
                  </Badge>
                </div>

                <div class="text-xs text-gray-600 mb-2 flex gap-4">
                  <span>Referência: <strong class="text-gray-900">{{ item.doseReferencia }} {{ item.unidade }}</strong></span>
                  <span v-if="item.doseMaxima" class="text-red-600 font-bold">
                    (Máximo: {{ item.doseMaxima }}{{ getUnidadeFinal(item.unidade) }})
                  </span>
                </div>

                <div class="grid grid-cols-[1fr_26px_1fr_26px_1fr] gap-1 items-end bg-gray-50 p-3 rounded-md border border-dashed border-gray-300">
                  <div class="flex flex-col">
                    <label class="text-[9px] uppercase font-bold text-gray-500 mb-1">Dose Teórica</label>
                    <div class="bg-white border rounded px-2 py-1 text-sm font-medium h-8 flex items-center">
                      {{ item.doseTeorica }} <small class="ml-1">{{ getUnidadeFinal(item.unidade) }}</small>
                    </div>
                  </div>

                  <div class="h-8 flex items-center justify-center text-gray-400">×</div>

                  <div class="flex flex-col">
                    <label class="text-[9px] uppercase font-bold text-gray-500 mb-1">Ajuste</label>
                    <div class="bg-white border rounded px-2 py-1 text-sm font-medium h-8 flex items-center">
                      {{ item.percentualAjuste }}%
                    </div>
                  </div>

                  <div class="h-8 flex items-center justify-center text-gray-400 font-bold">=</div>

                  <div class="flex flex-col">
                    <label class="text-[9px] uppercase font-bold text-green-700 mb-1">Dose Final</label>
                    <div
                        class="bg-green-50 border border-green-200 rounded px-2 py-1 text-sm font-bold text-green-800 h-8 flex items-center">
                      {{ item.doseFinal }} <small class="ml-1">{{ getUnidadeFinal(item.unidade) }}</small>
                    </div>
                  </div>
                </div>

                <div class="flex flex-col gap-2 mt-3">
                  <div class="flex items-center justify-between gap-2 bg-gray-50 p-2 rounded border border-gray-100">
                    <div class="flex items-center gap-2 text-sm">
                      <span class="text-gray-500 font-medium">Diluição:</span>
                      <span class="text-gray-700 font-medium">{{ item.diluicaoFinal || 'Não especificada' }}</span>
                    </div>
                    <div class="flex items-center gap-2 text-sm ">
                      <span class="text-gray-500 font-medium">Tempo:</span>
                      <span class="text-gray-700 font-medium">{{ item.tempoMinutos }} minutos</span>
                    </div>
                  </div>

                  <div v-if="item.notasEspecificas"
                       class="flex items-start gap-2 text-sm bg-yellow-50 p-2 rounded border border-yellow-100 text-yellow-800">
                    <AlertTriangle class="h-3 w-3 shrink-0 mt-0.5"/>
                    <span>{{ item.notasEspecificas }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500 italic border-2 border-dashed rounded-lg">
          Nenhum bloco de prescrição encontrado.
        </div>

        <div v-if="prescricao?.conteudo?.observacoes" class="bg-blue-50 border border-blue-100 rounded-lg p-4">
          <h4 class="text-sm font-bold text-blue-800 uppercase mb-1">Observações Gerais</h4>
          <p class="text-sm text-blue-700">{{ prescricao.conteudo.observacoes }}</p>
        </div>

      </div>

      <DialogFooter class="p-4 border-t bg-gray-50 shrink-0 rounded-b-lg">
        <div class="flex gap-2 mr-auto">
          <Button variant="secondary" @click="handleBaixar">
            <Download class="h-4 w-4 mr-2"/>
            Baixar
          </Button>
        </div>
        <Button variant="outline" @click="emit('update:open', false)">Fechar</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
