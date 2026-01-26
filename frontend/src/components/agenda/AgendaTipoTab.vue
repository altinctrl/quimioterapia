<script lang="ts" setup>
import {computed} from 'vue'
import {Card, CardContent} from '@/components/ui/card'
import AgendaControls, {type FiltrosAgenda} from '@/components/agenda/AgendaControls.vue'
import AgendaTable from '@/components/agenda/AgendaTable.vue'
import {getDuracaoAgendamento, getGrupoInfusao} from '@/utils/agendaUtils'
import {type Agendamento, AgendamentoStatusEnum, TipoAgendamento} from '@/types'

const props = defineProps<{
  agendamentos: Agendamento[]
  filtros: FiltrosAgenda
  mostrarFiltrosInfusao?: boolean
  tipo: TipoAgendamento
}>()

const emit = defineEmits<{
  (e: 'update:filtros', value: FiltrosAgenda): void
  (e: 'reset'): void

  (e: 'abrir-detalhes', agendamento: Agendamento): void
  (e: 'abrir-prescricao', agendamento: Agendamento): void
  (e: 'abrir-tags', agendamento: any): void
  (e: 'abrir-remarcar', agendamento: Agendamento): void
  (e: 'alterar-checkin', agendamento: Agendamento, checkin: boolean): void
  (e: 'alterar-status', agendamento: Agendamento, novoStatus: string): void
}>()

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
</script>

<template>
  <Card class="overflow-hidden">
    <div class="px-4 pt-4">
      <AgendaControls
          v-model="filtrosModel"
          :mostrar-farmacia="mostrarFiltrosInfusao"
          :mostrar-grupos-infusao="mostrarFiltrosInfusao"
          @reset="emit('reset')"
      />
    </div>

    <CardContent class="p-0 mt-0">
      <AgendaTable
          :agendamentos="agendamentosProcessados"
          :tipo="tipo"
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
</template>
