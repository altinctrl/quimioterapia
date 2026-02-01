<script lang="ts" setup>
import {computed} from 'vue'
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Badge} from '@/components/ui/badge'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import {AlertCircle, Calendar, Clock, ExternalLink, Tag, User} from 'lucide-vue-next'
import {Agendamento} from "@/types/typesAgendamento.ts";
import {formatarConsulta, formatarProcedimento} from "@/utils/utilsAgenda.ts";
import TimelineHistorico, {type TimelineItem} from '@/components/comuns/TimelineHistorico.vue'

const props = defineProps<{
  open: boolean
  agendamento: Agendamento | null
  pacienteNome?: string
}>()

const emit = defineEmits(['update:open', 'abrir-prescricao'])

const formatarData = (data: string) => {
  return new Date(data).toLocaleDateString('pt-BR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const historicoItens = computed<TimelineItem[]>(() => {
  if (!props.agendamento) return []

  const itens: TimelineItem[] = []
  const alteracoes = props.agendamento.historicoAlteracoes || []
  alteracoes.forEach((item, index) => {
    const titulo = item.tipoAlteracao === 'status'
      ? 'Status atualizado'
      : item.tipoAlteracao === 'checkin'
        ? 'Check-in atualizado'
        : item.tipoAlteracao === 'prescricao'
          ? 'Prescrição atualizada'
          : `Alteração: ${item.tipoAlteracao}`

    const descricao = item.valorAntigo || item.valorNovo
      ? `${item.valorAntigo ?? '-'} → ${item.valorNovo ?? '-'}`
      : undefined

    itens.push({
      id: `alt-${index}-${item.data}`,
      data: item.data,
      titulo,
      descricao,
      usuario: item.usuarioNome || item.usuarioId,
      meta: item.motivo || item.campo
    })
  })

  const historicoPrescricoes = props.agendamento.detalhes?.historicoPrescricoes || []
  historicoPrescricoes.forEach((item, index) => {
    itens.push({
      id: `presc-${index}-${item.data}`,
      data: item.data,
      titulo: 'Troca de prescrição no agendamento',
      descricao: `${item.prescricaoIdAnterior ?? '-'} → ${item.prescricaoIdNova ?? '-'}`,
      usuario: item.usuarioNome || item.usuarioId,
      meta: item.motivo
    })
  })

  return itens
})
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-2xl">
      <DialogHeader>
        <DialogTitle>Detalhes do Agendamento</DialogTitle>
      </DialogHeader>

      <Tabs v-if="agendamento" default-value="detalhes" class="space-y-4">
        <TabsList class="grid w-full grid-cols-2">
          <TabsTrigger value="detalhes">Detalhes</TabsTrigger>
          <TabsTrigger value="historico">Histórico</TabsTrigger>
        </TabsList>

        <TabsContent value="detalhes" class="space-y-4">

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 p-3 rounded-lg border">
          <div class="md:col-span-2 flex items-center justify-between border-b pb-2 mb-1">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-bold uppercase">Paciente:</span>
              <span class="text-sm font-bold text-gray-900">{{ pacienteNome }}</span>
            </div>
            <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider">
              <span class="text-gray-600 bg-gray-50 px-2 py-0.5 rounded border border-gray-200">
                {{ agendamento.status.replace('-', ' ') }}
              </span>
              <span v-if="agendamento.encaixe"
                    class="px-2 py-0.5 rounded border text-white bg-blue-500 border-blue-600">
                Encaixe
              </span>
            </div>
          </div>

          <div class="md:col-span-2 flex items-start gap-3 pb-3 mb-1">
            <Calendar class="h-5 w-5 text-gray-500 mt-0.5"/>
            <div>
              <p class="text-xs text-gray-500 font-bold uppercase">Data</p>
              <p class="text-gray-900 font-medium capitalize">{{ formatarData(agendamento.data) }}</p>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <Clock class="h-5 w-5 text-gray-500 mt-0.5"/>
            <div>
              <p class="text-xs text-gray-500 font-bold uppercase">Horário</p>
              <div class="flex items-center gap-2">
                <span class="text-gray-900 font-medium">
                  {{ agendamento.horarioInicio }} - {{ agendamento.horarioFim }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <User class="h-5 w-5 text-gray-500 mt-0.5"/>
            <div>
              <p class="text-xs text-gray-500 font-bold uppercase">Agendado por</p>
              <p class="text-gray-900 text-sm">
                {{ agendamento.criadoPor?.nome || agendamento.criadoPorId || '-' }}
              </p>
            </div>
          </div>
        </div>

        <div v-if="agendamento.detalhes?.infusao" class="bg-blue-50/50 p-4 rounded-lg border border-blue-100">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-4">
            <div class="md:col-span-2">
              <p class="text-xs text-blue-600/80 font-bold uppercase">Protocolo</p>
              <p class="text-blue-900 font-medium">
                {{ agendamento.prescricao?.conteudo.protocolo.nome || 'Não informado' }}
              </p>
            </div>

            <div>
              <p class="text-xs text-blue-600/80 font-bold uppercase">Ciclo</p>
              <p class="text-blue-900 font-medium">
                {{
                  agendamento.detalhes.infusao.cicloAtual ? `Ciclo ${agendamento.detalhes.infusao.cicloAtual}` : '-'
                }}
              </p>
            </div>

            <div>
              <p class="text-xs text-blue-600/80 font-bold uppercase">Dia</p>
              <p class="text-blue-900 font-medium">
                {{ agendamento.detalhes.infusao.diaCiclo ? `Dia ${agendamento.detalhes.infusao.diaCiclo}` : '-' }}
              </p>
            </div>

            <div>
              <p class="text-xs text-blue-600/80 font-bold uppercase">Farmácia</p>
              <p class="text-blue-900 font-medium capitalize mt-0.5">
                {{
                  agendamento.detalhes.infusao.statusFarmacia ? agendamento.detalhes.infusao.statusFarmacia.replace('-', ' ') : '-'
                }}
              </p>
            </div>

            <div>
              <p class="text-xs text-blue-600/80 font-bold uppercase">Previsão de Entrega</p>
              <p class="text-blue-900 font-bold flex items-center gap-1">
                {{ agendamento.detalhes.infusao.horarioPrevisaoEntrega || '--:--' }}
              </p>
            </div>
          </div>

          <div v-if="agendamento.detalhes.infusao.prescricaoId"
               class="mt-4 pt-3 border-t border-blue-200/50 flex justify-end">
            <Button class="p-0 h-auto text-sm text-blue-700 font-semibold hover:text-blue-900" variant="link"
                    @click="$emit('abrir-prescricao', agendamento)">
              Ver Prescrição
              <ExternalLink class="h-3 w-3 ml-1"/>
            </Button>
          </div>
        </div>

        <div v-if="agendamento.detalhes?.consulta" class="bg-green-50/50 p-4 rounded-lg border border-green-100">
          <h4 class="text-sm font-bold text-green-900 mb-3 flex items-center gap-2">
            <User class="h-4 w-4 text-green-600"/>
            Dados da Consulta
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-green-600/80 font-bold uppercase">Tipo de Consulta</p>
              <p class="text-green-900 font-medium capitalize">
                {{ formatarConsulta(agendamento.detalhes.consulta.tipoConsulta) }}
              </p>
            </div>
            <div v-if="agendamento.detalhes.consulta.observacoes" class="md:col-span-2">
              <p class="text-xs text-green-600/80 font-bold uppercase">Observações Específicas</p>
              <p class="text-green-900 text-sm mt-1">{{ agendamento.detalhes.consulta.observacoes }}</p>
            </div>
          </div>
        </div>

        <div v-if="agendamento.detalhes?.procedimento" class="bg-orange-50/50 p-4 rounded-lg border border-orange-100">
          <h4 class="text-sm font-bold text-orange-900 mb-3 flex items-center gap-2">
            <AlertCircle class="h-4 w-4 text-orange-600"/>
            Dados do Procedimento
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-orange-600/80 font-bold uppercase">Tipo de Procedimento</p>
              <p class="text-orange-900 font-medium capitalize">
                {{ formatarProcedimento(agendamento.detalhes.procedimento.tipoProcedimento) }}
              </p>
            </div>
            <div v-if="agendamento.detalhes.procedimento.observacoes" class="md:col-span-2">
              <p class="text-xs text-orange-600/80 font-bold uppercase">Observações do Procedimento</p>
              <p class="text-orange-900 text-sm mt-1">{{ agendamento.detalhes.procedimento.observacoes }}</p>
            </div>
          </div>
        </div>

        <div v-if="(agendamento.tags && agendamento.tags.length > 0) || agendamento.observacoes">
          <div v-if="agendamento.tags?.length" class="mb-3">
            <p class="text-xs text-gray-500 font-bold uppercase mb-1 flex items-center gap-1">
              <Tag class="h-3 w-3"/>
              Tags
            </p>
            <div class="flex flex-wrap gap-1">
              <Badge v-for="tag in agendamento.tags" :key="tag" class="text-xs bg-white" variant="outline">{{
                  tag
                }}
              </Badge>
            </div>
          </div>

          <div v-if="agendamento.observacoes">
            <p class="text-xs text-gray-500 font-bold uppercase mb-1 flex items-center gap-1">
              <AlertCircle class="h-3 w-3"/>
              Observações
            </p>
            <div
                class="bg-yellow-50/50 p-2.5 rounded text-sm text-gray-700 whitespace-pre-wrap border border-yellow-100">
              {{ agendamento.observacoes }}
            </div>
          </div>
        </div>

        </TabsContent>

        <TabsContent value="historico">
          <TimelineHistorico
            :itens="historicoItens"
            vazio-texto="Nenhuma alteração registrada para este agendamento."
          />
        </TabsContent>
      </Tabs>

      <DialogFooter>
        <Button variant="outline" @click="emit('update:open', false)">Fechar</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
