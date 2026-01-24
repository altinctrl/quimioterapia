import {defineStore, storeToRefs} from 'pinia'
import {usePacienteStore} from './paciente'
import {useAgendamentoStore} from './agendamento'
import {useConfiguracaoStore} from './configuracao'
import {useProtocoloStore} from './protocolo'
import {usePrescricaoStore} from './prescricao'

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
    importarProtocolos,
    atualizarProtocolo,
    desativarProtocolo
  } = protocoloStore

  const {
    getPrescricoesPorPaciente,
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
    fetchProtocolos,
    adicionarProtocolo,
    importarProtocolos,
    atualizarProtocolo,
    desativarProtocolo,
    adicionarPrescricao
  }
})
