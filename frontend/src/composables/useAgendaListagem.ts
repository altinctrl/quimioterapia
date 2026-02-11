import {computed, Ref} from 'vue'
import {Agendamento, AgendamentoStatusEnum, FiltrosAgenda} from "@/types/typesAgendamento.ts"
import {getDuracaoAgendamento, getGrupoInfusao} from '@/utils/utilsAgenda.ts'

export function useAgendaListagem(
  listaBruta: Ref<Agendamento[]>,
  filtros: Ref<FiltrosAgenda>,
  options: { filtrarInfusao: boolean } = {filtrarInfusao: true}
) {

  const listaProcessada = computed(() => {
    let lista = [...listaBruta.value]

    if (filtros.value.esconderRemarcados) {
      lista = lista.filter(a => a.status !== AgendamentoStatusEnum.REMARCADO)
    }

    if (filtros.value.turno !== 'todos') {
      lista = lista.filter(a => a.turno === filtros.value.turno)
    }

    if (options.filtrarInfusao) {
      if (filtros.value.statusFarmacia.length > 0) {
        lista = lista.filter(a => {
          const status = a.detalhes?.infusao?.statusFarmacia
          return status && filtros.value.statusFarmacia.includes(status)
        })
      }

      if (filtros.value.gruposInfusao.length > 0) {
        lista = lista.filter(a => {
          const duracao = getDuracaoAgendamento(a)
          const grupo = getGrupoInfusao(duracao)
          return filtros.value.gruposInfusao.includes(grupo)
        })
      }
    }

    return lista.sort((a, b) => {
      const durA = getDuracaoAgendamento(a)
      const durB = getDuracaoAgendamento(b)

      switch (filtros.value.ordenacao) {
        case 'grupo_asc':
          if (durA !== durB) return durA - durB
          return a.horarioInicio.localeCompare(b.horarioInicio)

        case 'grupo_desc':
          if (durA !== durB) return durB - durA
          return a.horarioInicio.localeCompare(b.horarioInicio)

        case 'horario':
          return a.horarioInicio.localeCompare(b.horarioInicio)

        case 'status':
          return getPesoStatus(a.status) - getPesoStatus(b.status)

        default:
          return 0
      }
    })
  })

  return {
    listaProcessada
  }
}

function getPesoStatus(s: string): number {
  if (['suspenso', 'intercorrencia', 'ausente'].includes(s)) return 0
  if (s === 'aguardando-medicamento') return 1
  if (s === 'em-infusao') return 2
  if (s === 'concluido') return 10
  return 5
}
