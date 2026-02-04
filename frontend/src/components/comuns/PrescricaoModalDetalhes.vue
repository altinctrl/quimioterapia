<script lang="ts" setup>
import {computed, ref} from 'vue'
import {useRouter} from 'vue-router'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {Separator} from '@/components/ui/separator'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import {Textarea} from '@/components/ui/textarea'
import {Activity, AlertTriangle, Download, FileText, History} from 'lucide-vue-next'
import {toast} from "vue-sonner";
import api from "@/services/api.ts";
import {getUnidadeFinal} from "@/utils/utilsPrescricao.ts";
import {usePrescricaoStatus} from '@/composables/usePrescricaoStatus.ts'
import {usePrescricaoStore} from '@/stores/storePrescricao.ts'
import {useAuthStore} from '@/stores/storeAuth.ts'
import {PrescricaoStatusEnum} from '@/types/typesPrescricao.ts'
import TimelineHistorico, {type TimelineItem} from '@/components/comuns/TimelineHistorico.vue'

const props = defineProps<{
  open: boolean
  prescricao: any
}>()

const emit = defineEmits(['update:open'])
const router = useRouter()

const prescricaoStore = usePrescricaoStore()
const authStore = useAuthStore()
const prescricaoAtual = computed(() => {
  const id = props.prescricao?.id
  if (!id) return props.prescricao
  return prescricaoStore.prescricoes.find(p => p.id === id) || props.prescricao
})

const {statusOptions, formatarStatus, alterarStatus, carregando} = usePrescricaoStatus()

const statusSelecionado = ref<PrescricaoStatusEnum | ''>('')
const motivo = ref('')

const podeSalvarStatus = computed(() => {
  if (!statusSelecionado.value) return false
  if ([PrescricaoStatusEnum.SUSPENSA, PrescricaoStatusEnum.CANCELADA].includes(statusSelecionado.value)) {
    return motivo.value.trim().length > 0
  }
  return true
})

const historicoItens = computed<TimelineItem[]>(() => {
  if (!prescricaoAtual.value) return []
  const itens: TimelineItem[] = []

  const statusList = prescricaoAtual.value.historicoStatus || []
  statusList.forEach((item: any, index: number) => {
    itens.push({
      id: `status-${index}-${item.data}`,
      data: item.data,
      titulo: `Status: ${formatarStatus(item.statusNovo)}`,
      descricao: item.statusAnterior ? `${formatarStatus(item.statusAnterior)} → ${formatarStatus(item.statusNovo)}` : undefined,
      usuario: item.usuarioNome || item.usuarioId,
      meta: item.motivo
    })
  })

  const agList = prescricaoAtual.value.historicoAgendamentos || []
  agList.forEach((item: any, index: number) => {
    itens.push({
      id: `ag-${index}-${item.data}`,
      data: item.data,
      titulo: `Agendamento ${item.agendamentoId}`,
      descricao: `Status: ${item.statusAgendamento}`,
      usuario: item.usuarioNome || item.usuarioId,
      meta: item.observacoes
    })
  })

  return itens
})

const getCategoriaLabel = (cat: string) => {
  const map: Record<string, string> = {
    'pre_med': 'Pré-Medicação',
    'qt': 'Terapia',
    'pos_med_hospitalar': 'Pós-Med (Hosp)',
    'pos_med_domiciliar': 'Pós-Med (Casa)',
  }
  return map[cat] || cat
}

const formatDiasCiclo = (dias: number[]) => {
  if (!dias || dias.length === 0) return ''
  return dias.map(d => `${d}`).join(', ')
}

const fetchPdfBlob = async () => {
  if (!prescricaoAtual.value?.id) throw new Error("ID inválido")
  const response = await api.get(`/api/prescricoes/${prescricaoAtual.value.id}/pdf`, {
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
    const nomePaciente = prescricaoAtual.value.conteudo?.paciente?.nome || 'paciente'
    link.setAttribute('download', `Prescricao_${nomePaciente}_${prescricaoAtual.value.id.slice(0, 8)}.pdf`)

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error(e)
    toast.error("Erro ao baixar PDF.")
  }
}

const handleSalvarStatus = async () => {
  if (!prescricaoAtual.value?.id || !statusSelecionado.value) return

  if ([PrescricaoStatusEnum.SUSPENSA, PrescricaoStatusEnum.CANCELADA].includes(statusSelecionado.value)) {
    if (!motivo.value.trim()) {
      toast.error('Informe o motivo da alteração')
      return
    }
  }

  try {
    await alterarStatus(prescricaoAtual.value.id, statusSelecionado.value, motivo.value)
    statusSelecionado.value = ''
    motivo.value = ''
  } catch (e) {
    console.error(e)
  }
}

const handleSubstituir = async () => {
  if (!prescricaoAtual.value?.id) return
  await router.push({
    name: 'Prescricao',
    query: {
      pacienteId: prescricaoAtual.value.pacienteId,
      substituirDe: prescricaoAtual.value.id
    }
  })
  emit('update:open', false)
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
            <DialogDescription v-if="prescricaoAtual?.conteudo?.paciente">
              Paciente: <span class="font-medium text-gray-900">{{ prescricaoAtual.conteudo.paciente.nome }}</span>
              <span class="mx-2 text-gray-300">|</span>
              Prontuário: {{ prescricaoAtual.conteudo.paciente.prontuario }}
            </DialogDescription>
          </div>
          <Badge :variant="prescricaoAtual?.status === 'concluida' ? 'default' : 'outline'" class="h-6">
            {{ formatarStatus(prescricaoAtual?.status) }}
          </Badge>
        </div>
      </DialogHeader>

      <div class="flex-1 overflow-y-auto min-h-0 w-full p-6 space-y-6 scrollbar-thin scrollbar-thumb-gray-200">

        <Tabs default-value="detalhes" class="space-y-6">
          <TabsList class="grid w-full grid-cols-2">
            <TabsTrigger value="detalhes">Detalhes</TabsTrigger>
            <TabsTrigger value="historico">Histórico</TabsTrigger>
          </TabsList>

          <TabsContent value="detalhes" class="space-y-6">

        <div v-if="prescricaoAtual" class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg border">
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Data Emissão</span>
            <p class="text-sm font-medium">{{ new Date(prescricaoAtual.dataEmissao).toLocaleDateString('pt-BR') }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Protocolo</span>
            <p class="text-sm font-medium">{{ prescricaoAtual.conteudo?.protocolo?.nome }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Ciclo</span>
            <p class="text-sm font-medium">{{ prescricaoAtual.conteudo?.protocolo?.cicloAtual }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500 uppercase font-bold">Médico</span>
            <p :title="prescricaoAtual.conteudo?.medico?.nome" class="text-sm font-medium truncate">
              {{ prescricaoAtual.conteudo?.medico?.nome }}
            </p>
          </div>
        </div>

        <div v-if="prescricaoAtual?.conteudo?.paciente">
          <h4 class="text-sm font-medium mb-3 flex items-center gap-2 text-gray-900">
            <Activity class="h-4 w-4 text-gray-900"/>
            Dados Antropométricos
          </h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 border p-4 rounded-lg bg-white shadow-sm">
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Peso</span>
              <span class="font-medium">{{ prescricaoAtual.conteudo.paciente.peso }} kg</span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Altura</span>
              <span class="font-medium">{{ prescricaoAtual.conteudo.paciente.altura }} cm</span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Sup. Corpórea</span>
              <span class="font-medium">{{ prescricaoAtual.conteudo.paciente.sc }} m²</span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm text-gray-500">Creatinina</span>
              <span class="font-medium">{{ prescricaoAtual.conteudo.paciente.creatinina ? prescricaoAtual.conteudo.paciente.creatinina + ' mg/dL' : '-' }}</span>
            </div>
          </div>
        </div>

          <div v-if="prescricaoAtual?.conteudo?.diagnostico" class="bg-blue-50 border border-blue-100 rounded-lg p-4">
            <h4 class="text-sm font-bold text-blue-800 uppercase mb-1">Hipótese Diagnóstica</h4>
            <p class="text-sm text-blue-700">{{ prescricaoAtual.conteudo.diagnostico }}</p>
          </div>

        <Separator/>

        <div v-if="prescricaoAtual?.conteudo?.blocos" class="space-y-6">
          <div
              v-for="bloco in prescricaoAtual.conteudo.blocos"
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
          </TabsContent>

          <TabsContent value="historico" class="space-y-6">
            <div class="bg-gray-50 p-4 rounded-lg border space-y-3">
              <div class="flex items-center gap-2 text-sm font-semibold text-gray-900">
                <History class="h-4 w-4" />
                Alterar status da prescrição
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="space-y-1">
                  <label class="text-xs font-bold uppercase text-gray-500">Novo status</label>
                  <Select
                    :model-value="statusSelecionado"
                    @update:model-value="(val) => (statusSelecionado = val as PrescricaoStatusEnum)"
                  >
                    <SelectTrigger class="bg-white">
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

              </div>

              <div class="space-y-1">
                <label class="text-xs font-bold uppercase text-gray-500">Motivo</label>
                <Textarea v-model="motivo" rows="2" placeholder="Descreva o motivo da alteração" />
              </div>

              <div class="flex justify-end">
                <Button :disabled="!podeSalvarStatus || carregando" @click="handleSalvarStatus">
                  Salvar alteração
                </Button>
              </div>
            </div>

            <TimelineHistorico
              :itens="historicoItens"
              vazio-texto="Nenhum histórico disponível para esta prescrição."
            />
          </TabsContent>
        </Tabs>
      </div>

      <DialogFooter class="p-4 border-t bg-gray-50 shrink-0 rounded-b-lg">
        <div class="flex gap-2 mr-auto">
          <Button variant="secondary" @click="handleBaixar">
            <Download class="h-4 w-4 mr-2"/>
            Baixar
          </Button>
          <Button
            v-if="['medico', 'admin'].includes(authStore.user?.role || '')"
            variant="outline"
            @click="handleSubstituir"
          >
            Substituir
          </Button>
        </div>
        <Button variant="outline" @click="emit('update:open', false)">Fechar</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
