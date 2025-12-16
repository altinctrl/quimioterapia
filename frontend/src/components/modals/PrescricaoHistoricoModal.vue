<script lang="ts" setup>
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {Separator} from '@/components/ui/separator'
import {Activity, Clock, Download, FileText, Pill, Printer} from 'lucide-vue-next'
import {toast} from "vue-sonner";
import type {PrescricaoMedica} from '@/types'

defineProps<{
  open: boolean
  prescricao: PrescricaoMedica | null
  pacienteNome?: string
}>()

const emit = defineEmits(['update:open'])

const formatarStatus = (status: string) => {
  const mapa: Record<string, string> = {
    'ativa': 'Ativa',
    'concluida': 'Concluída',
    'pausada': 'Pausada',
    'cancelada': 'Cancelada'
  }
  return mapa[status] || status
}

const handleImprimir = () => {
  window.print()
}

const handleBaixar = () => {
  toast.info('Iniciando download do PDF...')
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <FileText class="h-5 w-5"/>
          Detalhes da Prescrição
        </DialogTitle>
        <DialogDescription v-if="pacienteNome">Paciente: {{ pacienteNome }}</DialogDescription>
      </DialogHeader>

      <div v-if="prescricao" class="space-y-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg border">
          <div>
            <span class="text-xs text-gray-500 uppercase font-bold">Data</span>
            <p class="text-sm font-medium">{{ new Date(prescricao.dataPrescricao).toLocaleDateString('pt-BR') }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500 uppercase font-bold">Protocolo</span>
            <p class="text-sm font-medium">{{ prescricao.protocolo }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500 uppercase font-bold">Ciclo</span>
            <p class="text-sm font-medium">{{ prescricao.cicloAtual }} / {{ prescricao.ciclosTotal }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500 uppercase font-bold">Status</span>
            <div>
              <Badge variant="outline">{{ formatarStatus(prescricao.status) }}</Badge>
            </div>
          </div>
        </div>

        <div>
          <h4 class="text-sm font-medium mb-2 flex items-center gap-2">
            <Activity class="h-4 w-4"/>
            Dados Clínicos
          </h4>
          <div class="grid grid-cols-3 gap-4 text-sm border p-3 rounded-md">
            <div><span class="text-gray-500">Peso:</span> {{ prescricao.peso }} kg</div>
            <div><span class="text-gray-500">Altura:</span> {{ prescricao.altura }} cm</div>
            <div><span class="text-gray-500">Sup. Corpórea:</span> {{ prescricao.superficieCorporea }} m²</div>
          </div>
          <div v-if="prescricao.diagnostico"
               class="mt-2 text-sm bg-blue-50 p-2 rounded text-blue-900 border border-blue-100">
            <strong>Diagnóstico:</strong> {{ prescricao.diagnostico }}
          </div>
        </div>

        <Separator/>

        <div class="space-y-6">
          <div v-if="prescricao.medicamentos && prescricao.medicamentos.length > 0">
            <h4 class="text-sm font-medium mb-2 flex items-center gap-2">
              <Pill class="h-4 w-4 text-purple-600"/>
              Medicações / Pré-QT
            </h4>
            <div class="border rounded-md divide-y">
              <div v-for="med in prescricao.medicamentos" :key="med.id"
                   class="p-3 text-sm flex justify-between items-center">
                <div class="flex items-center gap-3">
                  <Badge class="h-5 w-5 flex items-center justify-center p-0 rounded-full" variant="secondary">
                    {{ med.ordem }}
                  </Badge>
                  <span class="font-medium">{{ med.nome }}</span>
                </div>
                <div class="text-gray-600">
                  {{ med.dose }} - {{ med.via }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="prescricao.qt && prescricao.qt.length > 0">
            <h4 class="text-sm font-medium mb-2 flex items-center gap-2">
              <Pill class="h-4 w-4 text-blue-600"/>
              Quimioterapia (QT)
            </h4>
            <div class="border rounded-md divide-y border-blue-100">
              <div v-for="med in prescricao.qt" :key="med.id"
                   class="p-3 text-sm bg-blue-50/50 flex justify-between items-center">
                <span class="font-medium text-blue-900">{{ med.nome }}</span>
                <div class="text-right">
                  <div class="text-blue-800">{{ med.dose }} {{ med.unidade }} - {{ med.via }}</div>
                  <div v-if="med.tempoInfusao" class="text-xs text-blue-600 flex items-center justify-end gap-1">
                    <Clock class="h-3 w-3"/>
                    {{ med.tempoInfusao }} min
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="prescricao.observacoes">
          <h4 class="text-sm font-medium mb-2">Observações Médicas</h4>
          <div class="bg-yellow-50 border border-yellow-200 p-3 rounded text-sm text-yellow-900">
            {{ prescricao.observacoes }}
          </div>
        </div>

        <div class="flex justify-end pt-4 text-sm text-gray-500">
          <div class="text-right">
            <p>Assinado por: <strong>{{ prescricao.medicoNome || 'Dr. Médico Responsável' }}</strong></p>
            <p>Em: {{ new Date(prescricao.dataPrescricao).toLocaleDateString() }}</p>
          </div>
        </div>
      </div>

      <DialogFooter>
        <div class="flex gap-2 mr-auto">
          <Button variant="secondary" @click="handleImprimir">
            <Printer class="h-4 w-4 mr-2"/>
            Imprimir
          </Button>
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
