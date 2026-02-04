import {defineStore, storeToRefs} from 'pinia'
import {usePacienteStore} from './storePaciente.ts'
import {useAgendamentoStore} from './storeAgendamento.ts'
import {useConfiguracaoStore} from './storeAjustes.ts'
import {useProtocoloStore} from './storeProtocolo.ts'
import {usePrescricaoStore} from './storePrescricao.ts'

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
    excluirProtocolo,
  } = protocoloStore

  const {
    getPrescricoesPorPaciente,
    fetchPrescricoes,
    adicionarPrescricao,
    adicionarPrescricaoSubstituicao,
    baixarPrescricao,
    alterarStatusPrescricao,
    substituirPrescricao,
  } = prescricaoStore

  const {
    getAgendamentosDoDia,
    fetchAgendamentos,
    adicionarAgendamento,
    atualizarCheckin,
    atualizarStatusAgendamento,
    atualizarStatusFarmacia,
    atualizarHorarioPrevisao,
    trocarPrescricaoAgendamento,
    remarcarAgendamento,
    atualizarTagsAgendamento,
    atualizarAgendamentosEmLote,
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
    trocarPrescricaoAgendamento,
    remarcarAgendamento,
    atualizarTagsAgendamento,
    atualizarAgendamentosEmLote,
    salvarChecklistFarmacia,

    fetchProtocolos,
    adicionarProtocolo,
    importarProtocolos,
    atualizarProtocolo,
    excluirProtocolo,
    adicionarPrescricao,
    adicionarPrescricaoSubstituicao,
    baixarPrescricao,
    alterarStatusPrescricao,
    substituirPrescricao,
  }
})
