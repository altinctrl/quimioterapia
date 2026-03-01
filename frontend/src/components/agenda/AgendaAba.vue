<script lang="ts" setup>
import {computed, onUnmounted, ref, toRef, watch} from 'vue'
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Checkbox} from '@/components/ui/checkbox'
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import AgendaControles from '@/components/agenda/AgendaControles.vue'
import AgendaTabela from '@/components/agenda/AgendaTabela.vue'
import {Agendamento, AgendamentoStatusEnum, FiltrosAgenda, TipoAgendamento} from "@/types/typesAgendamento.ts";
import {
  LABELS_STATUS_LOTE_AGENDA,
  STATUS_GERAL_POS_CHECKIN,
} from "@/constants/constAgenda.ts"
import {useAgendaOperacoes} from "@/composables/useAgendaOperacoes.ts";
import {useAgendaListagem} from "@/composables/useAgendaListagem.ts";

const props = defineProps<{
  agendamentos: Agendamento[]
  filtros: FiltrosAgenda
  mostrarFiltrosInfusao?: boolean
  tipo: TipoAgendamento
}>()

const emit = defineEmits<{
  (e: 'update:filtros', value: FiltrosAgenda): void
  (e: 'reset'): void
  (e: 'remarcado'): void
  (e: 'selection-change', count: number): void
  (e: 'abrir-detalhes', agendamento: Agendamento): void
  (e: 'abrir-prescricao', agendamento: Agendamento): void
  (e: 'abrir-tags', agendamento: any): void
  (e: 'abrir-remarcar', agendamento: Agendamento): void
  (e: 'alterar-checkin', agendamento: Agendamento, checkin: boolean): void
  (e: 'alterar-status', agendamento: Agendamento, novoStatus: string): void
}>()

const {
  aplicarStatusPacienteLote,
  remarcarLote,
} = useAgendaOperacoes()

const filtrosModel = computed({
  get: () => props.filtros,
  set: (val) => emit('update:filtros', val)
})

const agendamentosRef = toRef(props, 'agendamentos')

const {
  listaProcessada: agendamentosProcessados
} = useAgendaListagem(agendamentosRef, filtrosModel, { filtrarInfusao: props.mostrarFiltrosInfusao ?? true })

const selectedIds = ref<string[]>([])
const bulkRemarcarOpen = ref(false)
const bulkStatusPaciente = ref('')
const bulkForm = ref({
  novaData: '',
  novoHorario: '',
  motivo: '',
  manterHorario: true
})

const selectedAgendamentos = computed(() => {
  const ids = new Set(selectedIds.value)
  return agendamentosProcessados.value.filter(a => ids.has(a.id))
})

const limparSelecao = () => {
  selectedIds.value = []
  bulkStatusPaciente.value = ''
}

watch(agendamentosProcessados, (lista) => {
  const idsVisiveis = new Set(lista.map(a => a.id))
  selectedIds.value = selectedIds.value.filter(id => idsVisiveis.has(id))
})

const abrirRemarcacaoLote = () => {
  if (selectedIds.value.length === 0) return
  bulkForm.value = {
    novaData: '',
    novoHorario: '',
    motivo: '',
    manterHorario: true
  }
  bulkRemarcarOpen.value = true
}

const confirmarRemarcacaoLote = async () => {
  const selecionados = selectedAgendamentos.value
  if (selecionados.length === 0) return
  const ids = selecionados.map(a => a.id)
  try {
    await remarcarLote(ids, bulkForm.value)
    bulkRemarcarOpen.value = false
    limparSelecao()
    emit('remarcado')
  } catch (error) {}
}

const opcoesStatusLote = computed<Array<{ id: string; label: string }>>(() => {
  const selecionados = selectedAgendamentos.value
  if (selecionados.length === 0) return []

  if (props.tipo === 'infusao') {
    return LABELS_STATUS_LOTE_AGENDA
  }

  return LABELS_STATUS_LOTE_AGENDA.filter(op =>
    STATUS_GERAL_POS_CHECKIN.includes(op.id as any)
  )
})

const handleAplicarStatusPacienteLote = async () => {
  await aplicarStatusPacienteLote(selectedAgendamentos.value, bulkStatusPaciente.value as AgendamentoStatusEnum)
  limparSelecao()
}

watch(() => selectedIds.value.length, (newCount) => {
  emit('selection-change', newCount)
})

onUnmounted(() => {
  emit('selection-change', 0)
})
</script>

<template>
  <Card class="overflow-hidden">
    <div class="px-4 pt-4">
      <AgendaControles
          v-model="filtrosModel"
          v-model:bulk-status-paciente="bulkStatusPaciente"
          :mostrar-farmacia="mostrarFiltrosInfusao"
          :mostrar-grupos-infusao="mostrarFiltrosInfusao"
          :opcoes-status-lote="opcoesStatusLote"
          :selected-ids="selectedIds"
          @reset-filtros="emit('reset')"
          @limpar-selecao="limparSelecao"
          @aplicar-status="handleAplicarStatusPacienteLote"
          @aplicar-remarcacao="abrirRemarcacaoLote"
      />
    </div>

    <CardContent class="p-0 mt-0">
      <AgendaTabela
          :agendamentos="agendamentosProcessados"
          :tipo="tipo"
          v-model:selected-ids="selectedIds"
          class="border-0 rounded-none shadow-none"
          @abrir-detalhes="(ag) => emit('abrir-detalhes', ag)"
          @abrir-prescricao="(ag) => emit('abrir-prescricao', ag)"
          @abrir-tags="(ag) => emit('abrir-tags', ag)"
          @abrir-remarcar="(ag) => emit('abrir-remarcar', ag)"
          @alterar-checkin="(ag, checkin) => emit('alterar-checkin', ag, checkin)"
          @alterar-status="(ag, status) => emit('alterar-status', ag, status)"
      />
    </CardContent>
  </Card>

  <Dialog :open="bulkRemarcarOpen" @update:open="bulkRemarcarOpen = $event">
    <DialogContent class="sm:max-w-[460px]">
      <DialogHeader>
        <DialogTitle>Remarcar em lote</DialogTitle>
        <DialogDescription>
          {{ selectedIds.length }} agendamentos serão remarcados para a nova data.
        </DialogDescription>
      </DialogHeader>

      <div class="grid gap-4 py-4">
        <div class="space-y-2">
          <Label>Nova Data</Label>
          <Input v-model="bulkForm.novaData" type="date"/>
        </div>

        <div class="flex items-start gap-2">
          <Checkbox
              :checked="bulkForm.manterHorario"
              class="mt-1"
              @update:checked="(val) => bulkForm.manterHorario = val as boolean"
          />
          <div class="space-y-1">
            <Label class="text-sm">Manter horário original</Label>
            <p class="text-xs text-muted-foreground">Desmarque para aplicar um horário único para todos.</p>
          </div>
        </div>

        <div v-if="!bulkForm.manterHorario" class="space-y-2">
          <Label>Novo Horário</Label>
          <Input v-model="bulkForm.novoHorario" type="time"/>
        </div>

        <div class="space-y-2">
          <Label>Motivo</Label>
          <Textarea
              v-model="bulkForm.motivo"
              placeholder="Ex: Ajuste de agenda, indisponibilidade de recurso..."
          />
        </div>
      </div>

      <div class="flex justify-end gap-2">
        <Button variant="outline" @click="bulkRemarcarOpen = false">Cancelar</Button>
        <Button @click="confirmarRemarcacaoLote">Remarcar</Button>
      </div>
    </DialogContent>
  </Dialog>
</template>
