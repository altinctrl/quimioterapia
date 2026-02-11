<script lang="ts" setup>
import {computed, onUnmounted, ref, watch} from 'vue'
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Checkbox} from '@/components/ui/checkbox'
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import AgendaControles from '@/components/agenda/AgendaControles.vue'
import AgendaTabela from '@/components/agenda/AgendaTabela.vue'
import {getDuracaoAgendamento, getGrupoInfusao} from '@/utils/utilsAgenda.ts'
import {Agendamento, AgendamentoStatusEnum, FiltrosAgenda, TipoAgendamento} from "@/types/typesAgendamento.ts";
import {
  LABELS_STATUS_LOTE_AGENDA,
  STATUS_GERAL_POS_CHECKIN,
} from "@/constants/constAgenda.ts"
import {ChevronDown} from "lucide-vue-next";
import {useAgendaOperacoes} from "@/composables/useAgendaOperacoes.ts";

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

const agendamentosProcessados = computed(() => {
  let lista = [...props.agendamentos]

  if (filtrosModel.value.esconderRemarcados) lista = lista.filter(a => a.status !== AgendamentoStatusEnum.REMARCADO)
  if (filtrosModel.value.turno !== 'todos') lista = lista.filter(a => a.turno === filtrosModel.value.turno)

  if ((props.mostrarFiltrosInfusao ?? true) && filtrosModel.value.statusFarmacia.length > 0) {
    lista = lista.filter(a => {
      const status = a.detalhes?.infusao?.statusFarmacia
      return status && filtrosModel.value.statusFarmacia.includes(status)
    })
  }

  if ((props.mostrarFiltrosInfusao ?? true) && filtrosModel.value.gruposInfusao.length > 0) {
    lista = lista.filter(a => {
      const duracao = getDuracaoAgendamento(a)
      const grupo = getGrupoInfusao(duracao)
      return filtrosModel.value.gruposInfusao.includes(grupo)
    })
  }

  return lista.sort((a, b) => {
    const durA = getDuracaoAgendamento(a)
    const durB = getDuracaoAgendamento(b)

    switch (filtrosModel.value.ordenacao) {
      case 'grupo_asc':
        if (durA !== durB) return durA - durB
        return a.horarioInicio.localeCompare(b.horarioInicio)

      case 'grupo_desc':
        if (durA !== durB) return durB - durA
        return a.horarioInicio.localeCompare(b.horarioInicio)

      case 'horario':
        return a.horarioInicio.localeCompare(b.horarioInicio)

      case 'status':
        const getPeso = (s: string) => {
          if (['suspenso', 'intercorrencia', 'ausente'].includes(s)) return 0
          if (s === 'aguardando-medicamento') return 1
          if (s === 'em-infusao') return 2
          if (s === 'concluido') return 10
          return 5
        }
        return getPeso(a.status) - getPeso(b.status)

      default:
        return 0
    }
  })
})

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
          :mostrar-farmacia="mostrarFiltrosInfusao"
          :mostrar-grupos-infusao="mostrarFiltrosInfusao"
          @reset="emit('reset')"
      />
    </div>

    <div v-if="selectedIds.length" class="px-4 py-3">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between bg-blue-50 border border-blue-100 rounded-md p-3">
        <span class="text-sm font-medium text-blue-700">
          {{ selectedIds.length }} agendamentos selecionados
        </span>
        <div class="flex flex-wrap gap-2">
          <div class="relative">
            <select
                v-model="bulkStatusPaciente"
                class="flex h-8 w-full items-center justify-between rounded-md border border-input bg-background
                         px-3 py-1 pr-8 text-sm ring-offset-background placeholder:text-muted-foreground
                         focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2
                         disabled:cursor-not-allowed disabled:opacity-50 appearance-none truncate"
            >
              <option disabled value="">Alterar status...</option>
              <option
                  v-for="opcao in opcoesStatusLote"
                  :key="opcao.id"
                  :value="opcao.id"
              >
                {{ opcao.label }}
              </option>
            </select>
            <ChevronDown class="absolute right-2 top-2 h-4 w-4 opacity-50 pointer-events-none"/>
          </div>
          <Button class="h-8" size="sm" variant="outline" @click="limparSelecao">
            Cancelar
          </Button>
          <Button class="h-8" size="sm" @click="handleAplicarStatusPacienteLote">
            Confirmar
          </Button>
          <Button class="h-8" size="sm" @click="abrirRemarcacaoLote">
            Remarcar
          </Button>
        </div>
      </div>
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
