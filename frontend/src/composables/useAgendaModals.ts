import {computed, ref} from 'vue'
import {Agendamento, AgendamentoStatusEnum} from "@/types/typesAgendamento.ts"
import {toast} from "vue-sonner"

export function useAgendaModals() {
  const detalhesModalOpen = ref(false)
  const agendamentoSelecionado = ref<Agendamento | null>(null)

  const prescricaoModalOpen = ref(false)
  const prescricaoParaVisualizar = ref<any>(null)

  const tagsModalOpen = ref(false)
  const tagsModalData = ref<{ id: string; tags: string[] } | null>(null)

  const remarcarModalOpen = ref(false)
  const agendamentoParaRemarcar = ref<Agendamento | null>(null)

  const statusModalOpen = ref(false)
  const statusPendingData = ref<{ id: string; novoStatus: AgendamentoStatusEnum; pacienteNome: string } | null>(null)

  const abrirDetalhesAgendamento = (ag: Agendamento | undefined | null) => {
    if (ag) {
      agendamentoSelecionado.value = ag
      detalhesModalOpen.value = true
    }
  }

  const abrirPrescricao = (ag: Agendamento | undefined | null) => {
    if (detalhesModalOpen.value) detalhesModalOpen.value = false

    if (ag?.prescricao) {
      prescricaoParaVisualizar.value = ag.prescricao
      prescricaoModalOpen.value = true
    } else {
      toast.error("Nenhuma prescrição vinculada a este agendamento.")
    }
  }

  const abrirTags = (ag: Agendamento) => {
    tagsModalData.value = {id: ag.id, tags: ag.tags || []}
    tagsModalOpen.value = true
  }

  const abrirRemarcar = (ag: Agendamento) => {
    agendamentoParaRemarcar.value = ag
    remarcarModalOpen.value = true
  }

  const abrirAlterarStatus = (ag: Agendamento, novoStatus: AgendamentoStatusEnum) => {
    statusPendingData.value = {
      id: ag.id,
      novoStatus,
      pacienteNome: ag.paciente?.nome || 'Paciente'
    }
    statusModalOpen.value = true
  }

  const isAlgumModalAberto = computed(() =>
    detalhesModalOpen.value ||
    prescricaoModalOpen.value ||
    tagsModalOpen.value ||
    remarcarModalOpen.value ||
    statusModalOpen.value
  )

  return {
    detalhesModalOpen,
    agendamentoSelecionado,
    abrirDetalhesAgendamento,

    prescricaoModalOpen,
    prescricaoParaVisualizar,
    abrirPrescricao,

    tagsModalOpen,
    tagsModalData,
    abrirTags,

    remarcarModalOpen,
    agendamentoParaRemarcar,
    abrirRemarcar,

    statusModalOpen,
    statusPendingData,
    abrirAlterarStatus,

    isAlgumModalAberto
  }
}
