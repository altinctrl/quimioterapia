import {defineStore, storeToRefs} from 'pinia'
import {toast} from 'vue-sonner'
import {usePacienteStore} from './paciente'
import {useAgendamentoStore} from './agendamento'
import {useConfiguracaoStore} from './configuracao'
import {useProtocoloStore} from './protocolo'
import {usePrescricaoStore} from './prescricao'
import {getDataLocal} from '@/lib/utils.ts';

export const useAppStore = defineStore('app', () => {
  const pacienteStore = usePacienteStore()
  const agendamentoStore = useAgendamentoStore()
  const configuracaoStore = useConfiguracaoStore()
  const protocoloStore = useProtocoloStore()
  const prescricaoStore = usePrescricaoStore()

  const {pacientes, totalPacientes, resultadosBusca} = storeToRefs(pacienteStore)
  const {agendamentos} = storeToRefs(agendamentoStore)
  const {statusConfig, parametros} = storeToRefs(configuracaoStore)
  const {protocolos} = storeToRefs(protocoloStore)
  const {prescricoes} = storeToRefs(prescricaoStore)

  const {
    getStatusConfig,
    fetchConfiguracoes,
    salvarConfiguracoes
  } = configuracaoStore

  const {
    getPacienteById,
    fetchPacientes,
    carregarPaciente,
    buscarPacientesDropdown,
    adicionarPaciente,
    atualizarPaciente
  } = pacienteStore

  const {
    getProtocoloById,
    fetchProtocolos,
    adicionarProtocolo,
    atualizarProtocolo,
    desativarProtocolo
  } = protocoloStore

  const {
    getPrescricoesPorPaciente,
    getProtocoloPeloHistorico,
    fetchPrescricoes,
    adicionarPrescricao
  } = prescricaoStore

  const {
    getAgendamentosDoDia,
    fetchAgendamentos,
    adicionarAgendamento,
    atualizarCheckin,
    atualizarStatusAgendamento,
    atualizarStatusFarmacia,
    atualizarHorarioPrevisao,
    remarcarAgendamento,
    atualizarTagsAgendamento,
    salvarChecklistFarmacia
  } = agendamentoStore

  async function fetchInitialData() {
    try {
      await Promise.all([fetchPacientes(), fetchProtocolos(), fetchConfiguracoes()])
      const hoje = getDataLocal()
      await fetchAgendamentos(hoje, hoje)
    } catch (error) {
      console.error("Erro ao carregar dados iniciais", error)
      toast.error("Erro de conexão ao carregar dados.")
    }
  }

  return {
    pacientes,
    totalPacientes,
    resultadosBusca,
    agendamentos,
    protocolos,
    prescricoes,
    parametros,
    statusConfig,

    getPacienteById,
    getProtocoloById,
    getStatusConfig,
    getAgendamentosDoDia,
    getPrescricoesPorPaciente,
    getProtocoloPeloHistorico,

    fetchInitialData,
    fetchConfiguracoes,
    salvarConfiguracoes,
    fetchPacientes,
    carregarPaciente,
    buscarPacientesDropdown,
    fetchAgendamentos,
    fetchPrescricoes,
    adicionarPaciente,
    atualizarPaciente,
    adicionarAgendamento,
    atualizarCheckin,
    atualizarStatusAgendamento,
    atualizarStatusFarmacia,
    atualizarHorarioPrevisao,
    remarcarAgendamento,
    atualizarTagsAgendamento,
    salvarChecklistFarmacia,
    adicionarProtocolo,
    atualizarProtocolo,
    desativarProtocolo,
    adicionarPrescricao
  }
})