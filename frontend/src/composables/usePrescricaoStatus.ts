import {computed, ref} from 'vue'
import {toast} from 'vue-sonner'
import {usePrescricaoStore} from '@/stores/storePrescricao.ts'
import {PrescricaoStatusEnum} from '@/types/typesPrescricao.ts'

const statusLabels: Record<string, string> = {
  [PrescricaoStatusEnum.PENDENTE]: 'Pendente',
  [PrescricaoStatusEnum.AGENDADA]: 'Agendada',
  [PrescricaoStatusEnum.EM_CURSO]: 'Em Curso',
  [PrescricaoStatusEnum.CONCLUIDA]: 'Concluída',
  [PrescricaoStatusEnum.SUSPENSA]: 'Suspensa',
  [PrescricaoStatusEnum.SUBSTITUIDA]: 'Substituída',
  [PrescricaoStatusEnum.CANCELADA]: 'Cancelada'
}

export function usePrescricaoStatus() {
  const prescricaoStore = usePrescricaoStore()
  const carregando = ref(false)

    const statusOptions = computed(() => [
      {value: PrescricaoStatusEnum.SUSPENSA, label: statusLabels[PrescricaoStatusEnum.SUSPENSA]},
      {value: PrescricaoStatusEnum.CANCELADA, label: statusLabels[PrescricaoStatusEnum.CANCELADA]}
    ])

  const formatarStatus = (status?: string) => {
    if (!status) return '-'
    return statusLabels[status] || status
  }

  const alterarStatus = async (id: string, status: PrescricaoStatusEnum, motivo?: string) => {
    carregando.value = true
    try {
      return await prescricaoStore.alterarStatusPrescricao(id, status, motivo)
    } finally {
      carregando.value = false
    }
  }

  const substituir = async (id: string, prescricaoSubstitutaId: string, motivo?: string) => {
    if (!prescricaoSubstitutaId) {
      toast.error('Informe a prescrição substituta')
      return
    }
    carregando.value = true
    try {
      return await prescricaoStore.substituirPrescricao(id, prescricaoSubstitutaId, motivo)
    } finally {
      carregando.value = false
    }
  }

  return {
    carregando,
    statusOptions,
    formatarStatus,
    alterarStatus,
    substituir
  }
}
