import {useAppStore} from '@/stores/storeGeral.ts'
import {toast} from 'vue-sonner'
import {FarmaciaStatusEnum} from "@/types/typesAgendamento.ts"

export function useFarmaciaOperacoes() {
  const appStore = useAppStore()

  const alterarStatusFarmacia = async (id: string, novoStatus: FarmaciaStatusEnum) => {
    await appStore.atualizarStatusFarmacia(id, novoStatus)
  }

  const alterarHorarioPrevisao = async (id: string, novoHorario: string) => {
    await appStore.atualizarHorarioPrevisao(id, novoHorario)
  }

  const salvarChecklist = async (id: string, itens: string[]) => {
    await appStore.salvarChecklistFarmacia(id, itens)
  }

  const aplicarStatusFarmaciaLote = async (
    itens: { id: string, statusFarmacia: string, statusBloqueado: boolean }[],
    novoStatus: FarmaciaStatusEnum
  ) => {
    if (!novoStatus) {
      toast.error('Selecione um status para aplicar.')
      return
    }
    const itensParaAtualizar: any[] = []
    let bloqueadosCount = 0

    itens.forEach(row => {
      if (row.statusBloqueado) {
        bloqueadosCount++
        return
      }

      if (row.statusFarmacia !== novoStatus) {
        itensParaAtualizar.push({
          id: row.id,
          detalhes: {
            infusao: {
              status_farmacia: novoStatus
            }
          }
        })
      }
    })

    if (itensParaAtualizar.length === 0) {
      if (bloqueadosCount > 0) {
        toast.warning('Nenhum item válido para atualizar.')
      } else {
        toast.info('Todos os itens já estão com este status.')
      }
      return
    }

    try {
      await appStore.atualizarAgendamentosEmLote(itensParaAtualizar)
      if (bloqueadosCount > 0) {
        toast.warning(`${bloqueadosCount} itens bloqueados foram ignorados.`)
      }
    } catch (error) {
      console.error("Erro na atualização em lote da farmácia", error)
    }
  }

  return {
    alterarStatusFarmacia,
    alterarHorarioPrevisao,
    aplicarStatusFarmaciaLote,
    salvarChecklist,
  }
}
