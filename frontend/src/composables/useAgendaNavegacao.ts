import {useSessionStorage} from '@vueuse/core'
import {getDataLocal} from '@/lib/utils.ts'
import {somarDias} from '@/utils/utilsAgenda.ts'

export function useAgendaNavegacao(chaveStorage: string) {
  const dataSelecionada = useSessionStorage(chaveStorage, getDataLocal())

  const handleHoje = () => {
    dataSelecionada.value = getDataLocal()
  }

  const handleDiaAnterior = () => {
    dataSelecionada.value = somarDias(dataSelecionada.value, -1)
  }

  const handleProximoDia = () => {
    dataSelecionada.value = somarDias(dataSelecionada.value, 1)
  }

  return {
    dataSelecionada,
    handleHoje,
    handleDiaAnterior,
    handleProximoDia,
  }
}
