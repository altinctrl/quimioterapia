import {computed, Ref} from 'vue'
import {Agendamento, AgendamentoStatusEnum, FarmaciaStatusEnum} from "@/types/typesAgendamento.ts"
import {getDuracaoAgendamento, getGrupoInfusao} from "@/utils/utilsAgenda.ts"

export function useAgendaMetricas(agendamentos: Ref<Agendamento[]>) {

  const metricas = computed(() => {
    const dados = {
      total: 0,
      encaixes: 0,
      manha: 0,
      tarde: 0,

      emAndamento: 0,
      concluidos: 0,
      suspensos: 0,
      intercorrencias: 0,

      rapido: 0,
      medio: 0,
      longo: 0,
      extraLongo: 0,

      farmaciaPendentes: 0,
      farmaciaPreparando: 0,
      farmaciaProntas: 0,
      farmaciaEnviadas: 0
    }

    const list = agendamentos.value
    dados.total = list.length

    for (const ag of list) {
      if (ag.turno === 'manha') dados.manha++
      else if (ag.turno === 'tarde') dados.tarde++

      if (ag.encaixe) dados.encaixes++

      if ([AgendamentoStatusEnum.EM_INFUSAO, AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO].includes(ag.status))
        dados.emAndamento++
      else if (ag.status === AgendamentoStatusEnum.CONCLUIDO) dados.concluidos++
      else if (ag.status === AgendamentoStatusEnum.SUSPENSO) dados.suspensos++
      else if (ag.status === AgendamentoStatusEnum.INTERCORRENCIA) dados.intercorrencias++

      const minutos = getDuracaoAgendamento(ag)
      const grupo = getGrupoInfusao(minutos)

      if (grupo === 'rapido') dados.rapido++
      else if (grupo === 'medio') dados.medio++
      else if (grupo === 'longo') dados.longo++
      else if (grupo === 'extra_longo') dados.extraLongo++

      const statusFarm = ag.detalhes?.infusao?.statusFarmacia
      if (statusFarm === FarmaciaStatusEnum.PENDENTE) dados.farmaciaPendentes++
      else if (statusFarm === FarmaciaStatusEnum.EM_PREPARACAO) dados.farmaciaPreparando++
      else if (statusFarm === FarmaciaStatusEnum.PRONTO) dados.farmaciaProntas++
      else if (statusFarm === FarmaciaStatusEnum.ENVIADO) dados.farmaciaEnviadas++
    }

    return dados
  })

  return {
    metricas
  }
}
