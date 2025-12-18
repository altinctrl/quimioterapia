import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import type {
  Agendamento,
  ConfigStatus,
  Paciente,
  ParametrosAgendamento,
  PrescricaoMedica,
  Protocolo,
  StatusFarmacia,
  StatusPaciente
} from '@/types'

const defaultStatusConfig: ConfigStatus[] = [{
  id: 'agendado', label: 'Agendado', cor: 'bg-slate-500 text-white hover:bg-slate-600', tipo: 'paciente'
}, {
  id: 'em-triagem', label: 'Em Triagem', cor: 'bg-blue-500 text-white hover:bg-blue-600', tipo: 'paciente'
}, {
  id: 'aguardando-consulta',
  label: 'Aguardando Consulta',
  cor: 'bg-indigo-500 text-white hover:bg-indigo-600',
  tipo: 'paciente'
}, {
  id: 'aguardando-exame',
  label: 'Aguardando Exame',
  cor: 'bg-violet-500 text-white hover:bg-violet-600',
  tipo: 'paciente'
}, {
  id: 'aguardando-medicamento',
  label: 'Aguardando Medicação',
  cor: 'bg-purple-500 text-white hover:bg-purple-600',
  tipo: 'paciente'
}, {
  id: 'em-infusao', label: 'Em Infusão', cor: 'bg-green-600 text-white hover:bg-green-700', tipo: 'paciente'
}, {
  id: 'pos-qt', label: 'Pós-QT', cor: 'bg-emerald-600 text-white hover:bg-emerald-700', tipo: 'paciente'
}, {
  id: 'concluido', label: 'Concluído', cor: 'bg-teal-600 text-white hover:bg-teal-700', tipo: 'paciente'
}, {
  id: 'internado', label: 'Internado', cor: 'bg-orange-500 text-white hover:bg-orange-600', tipo: 'paciente'
}, {
  id: 'suspenso', label: 'Suspenso', cor: 'bg-red-600 text-white hover:bg-red-700', tipo: 'paciente'
}, {
  id: 'ausente', label: 'Ausente', cor: 'bg-rose-600 text-white hover:bg-rose-700', tipo: 'paciente'
}, {
  id: 'intercorrencia', label: 'Intercorrência', cor: 'bg-amber-500 text-white hover:bg-amber-600', tipo: 'paciente'
}, {id: 'obito', label: 'Óbito', cor: 'bg-gray-900 text-white hover:bg-black', tipo: 'paciente'}, {
  id: 'remarcado', label: 'Remarcado', cor: 'bg-gray-200 text-gray-500 border-gray-300', tipo: 'paciente'
}, {id: 'pendente', label: 'Pendente', cor: 'bg-gray-500 text-white', tipo: 'farmacia'}, {
  id: 'em-preparacao', label: 'Em Preparação', cor: 'bg-blue-500 text-white', tipo: 'farmacia'
}, {id: 'pronta', label: 'Pronta', cor: 'bg-green-500 text-white', tipo: 'farmacia'}, {
  id: 'enviada', label: 'Enviada', cor: 'bg-purple-600 text-white', tipo: 'farmacia'
}]

export const useAppStore = defineStore('app', () => {
  const pacientes = ref<Paciente[]>([])
  const totalPacientes = ref(0)
  const resultadosBusca = ref<Paciente[]>([])
  const agendamentos = ref<Agendamento[]>([])
  const protocolos = ref<Protocolo[]>([])
  const prescricoes = ref<PrescricaoMedica[]>([])
  const statusConfig = ref<ConfigStatus[]>(defaultStatusConfig)

  const parametros = ref<ParametrosAgendamento>(
    {
    horarioAbertura: '',
    horarioFechamento: '',
    diasFuncionamento: [],
    gruposInfusao: {
      rapido: {vagas: 0, duracao: ''},
      medio: {vagas: 0, duracao: ''},
      longo: {vagas: 0, duracao: ''}
    },
    tags: []
  })


  function getPacienteById(id: string) {
    const p = pacientes.value.find(p => p.id === id)
    if (p && !p.idade && p.dataNascimento) {
      const nascimento = new Date(p.dataNascimento)
      const hoje = new Date()
      let idade = hoje.getFullYear() - nascimento.getFullYear()
      const m = hoje.getMonth() - nascimento.getMonth()
      if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) {
        idade--
      }
      p.idade = idade
    }
    return p
  }

  function getProtocoloById(id: string) {
    return protocolos.value.find(p => p.id === id)
  }

  function getStatusConfig(id: string) {
    return statusConfig.value.find(s => s.id === id) || defaultStatusConfig[0]
  }

  function getAgendamentosDoDia(data: string) {
    return agendamentos.value.filter(a => a.data === data)
  }

  function getPrescricoesPorPaciente(pacienteId: string) {
    return prescricoes.value.filter(p => p.pacienteId === pacienteId)
  }

  function getProtocoloPeloHistorico(pacienteId: string) {
    const lista = prescricoes.value.filter(p => p.pacienteId === pacienteId)

    if (lista.length === 0) return null

    const ultima = lista.sort((a, b) =>
      new Date(b.dataPrescricao).getTime() - new Date(a.dataPrescricao).getTime()
    )[0]

    if (ultima.protocoloId) {
      const proto = protocolos.value.find(p => p.id === ultima.protocoloId)
      if (proto) return proto
    }

    if (ultima.protocolo) {
      return {nome: ultima.protocolo} as any
    }

    return null
  }


  async function fetchInitialData() {
    try {
      await Promise.all([fetchPacientes(), fetchProtocolos(), fetchConfiguracoes()])
      const hoje = new Date().toISOString().split('T')[0]
      await fetchAgendamentos(hoje, hoje)
    } catch (error) {
      console.error("Erro ao carregar dados iniciais", error)
      toast.error("Erro de conexão ao carregar dados.")
    }
  }

  async function fetchPacientes(page = 1, size = 10, termo = '') {
    try {
      const params: any = {page, size}
      if (termo) params.termo = termo

      const res = await api.get('/api/pacientes', {params})

      pacientes.value = res.data.items
      totalPacientes.value = res.data.total

    } catch (e) {
      console.error(e)
    }
  }

  async function buscarPacientesDropdown(termo: string) {
    if (!termo || termo.length < 2) {
      resultadosBusca.value = []
      return
    }
    try {
      const res = await api.get('/api/pacientes', {params: {termo, page: 1, size: 20}})
      resultadosBusca.value = res.data.items
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchProtocolos() {
    try {
      const res = await api.get('/api/protocolos', {params: {ativo: true}})
      protocolos.value = res.data
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchAgendamentos(inicio?: string, fim?: string) {
    try {
      const params: any = {}
      if (inicio) params.data_inicio = inicio
      if (fim) params.data_fim = fim

      const res = await api.get('/api/agendamentos', {params})
      agendamentos.value = res.data
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchConfiguracoes() {
    try {
      const res = await api.get('/api/configuracoes')
      parametros.value = res.data
    } catch (e) {
    console.error("Erro na API de configurações:", e)
    throw e
    }
  }

  async function salvarConfiguracoes(dados: ParametrosAgendamento) {
    try {
      const res = await api.put('/api/configuracoes', dados)
      parametros.value = res.data
      toast.success("Configurações salvas com sucesso")
    } catch (e) {
      console.error(e)
      toast.error("Erro ao salvar configurações")
      throw e
    }
  }

  async function adicionarPaciente(paciente: any) {
    try {
      const res = await api.post('/api/pacientes', paciente)
      pacientes.value.push(res.data)
      // toast.success("Paciente cadastrado com sucesso")
      return res.data
    } catch (e) {
      // toast.error("Erro ao cadastrar paciente")
      throw e
    }
  }

  async function atualizarPaciente(id: string, dados: any) {
    try {
      const res = await api.put(`/api/pacientes/${id}`, dados)
      const idx = pacientes.value.findIndex(p => p.id === id)
      if (idx !== -1) pacientes.value[idx] = res.data
      toast.success("Dados do paciente atualizados")
    } catch (e) {
      toast.error("Erro ao atualizar paciente")
    }
  }

  async function adicionarAgendamento(agendamento: any) {
    try {
      const res = await api.post('/api/agendamentos', agendamento)
      agendamentos.value.push(res.data)
      // Recarregar lista para garantir ordenação
      return res.data
    } catch (e) {
      toast.error("Erro ao criar agendamento")
      throw e
    }
  }

  async function atualizarStatusAgendamento(
  id: string,
  status: StatusPaciente,
  detalhes?: any
) {
    try {
      const payload: any = {status}
      if (detalhes) payload.detalhes = detalhes
      else payload.detalhes = null

      const res = await api.put(`/api/agendamentos/${id}`, payload)

      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data

      toast.success(`Status atualizado para: ${status}`)
    } catch (e) {
      toast.error("Erro ao atualizar status")
    }
  }

  async function atualizarStatusFarmacia(id: string, status: StatusFarmacia) {
    try {
      const res = await api.put(`/api/agendamentos/${id}`, {statusFarmacia: status})
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data
      toast.success("Status farmácia atualizado")
    } catch (e) {
      toast.error("Erro na atualização")
    }
  }

  async function atualizarHorarioPrevisao(id: string, horario: string) {
    try {
      const res = await api.put(`/api/agendamentos/${id}`, {horarioPrevisaoEntrega: horario})
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data
    } catch (e) {
      toast.error("Erro ao atualizar horário")
    }
  }

  async function remarcarAgendamento(idOriginal: string, novaData: string, novoHorario: string, motivo: string) {
    // Rever lógica de remarcação. Foi implementada no Backend?

    try {
      const detalhesPayload = {
        tipo: 'remarcacao', motivo: motivo, data_nova: novaData
      }

      await atualizarStatusAgendamento(idOriginal, 'remarcado', detalhesPayload)

      const original = agendamentos.value.find(a => a.id === idOriginal)
      if (!original) return

      await adicionarAgendamento({
        pacienteId: original.pacienteId,
        data: novaData,
        turno: parseInt(novoHorario.split(':')[0]) < 13 ? 'manha' : 'tarde',
        horarioInicio: novoHorario,
        horarioFim: original.horarioFim, // Idealmente recalcular
        status: 'agendado',
        statusFarmacia: 'pendente',
        encaixe: true,
        observacoes: `Remarcado de ${original.data}. Motivo: ${motivo}`,
        cicloAtual: original.cicloAtual,
        diaCiclo: original.diaCiclo
      })
      toast.success("Agendamento remarcado")
    } catch (e) {
      toast.error("Erro ao remarcar")
    }
  }

  async function atualizarTagsAgendamento(id: string, tags: string[]) {
    try {
      const res = await api.put(`/api/agendamentos/${id}`, {tags})
      const idx = agendamentos.value.findIndex(a => a.id === id)
      if (idx !== -1) agendamentos.value[idx] = res.data
      toast.success("Tags atualizadas")
    } catch (e) {
      console.error(e)
      toast.error("Erro ao salvar tags")
      throw e
    }
  }

  async function adicionarProtocolo(protocolo: any) {
    try {
      const res = await api.post('/api/protocolos', protocolo)
      protocolos.value.push(res.data)
    } catch (e) {
      toast.error("Erro ao salvar protocolo")
    }
  }

  async function atualizarProtocolo(id: string, dados: any) {
    try {
      const res = await api.put(`/api/protocolos/${id}`, dados)
      const idx = protocolos.value.findIndex(p => p.id === id)
      if (idx !== -1) protocolos.value[idx] = res.data
    } catch (e) {
      toast.error("Erro ao atualizar protocolo")
    }
  }

  async function desativarProtocolo(id: string) {
    try {
      await api.delete(`/api/protocolos/${id}`)
      const idx = protocolos.value.findIndex(p => p.id === id)
      if (idx !== -1) protocolos.value[idx].ativo = false
    } catch (e) {
      toast.error("Erro ao desativar")
    }
  }

  async function fetchPrescricoes(pacienteId: string) {
    try {
      const res = await api.get(`/api/prescricoes/paciente/${pacienteId}`)
      prescricoes.value = prescricoes.value.filter(p => p.pacienteId !== pacienteId).concat(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  async function adicionarPrescricao(prescricao: any) {
    try {
      const res = await api.post('/api/prescricoes', prescricao)
      prescricoes.value.push(res.data)
      return res.data
    } catch (e) {
      toast.error("Erro ao criar prescrição")
      throw e
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
    buscarPacientesDropdown,
    fetchAgendamentos,
    fetchPrescricoes,
    adicionarPaciente,
    atualizarPaciente,
    adicionarAgendamento,
    atualizarStatusAgendamento,
    atualizarStatusFarmacia,
    atualizarHorarioPrevisao,
    remarcarAgendamento,
    atualizarTagsAgendamento,
    adicionarProtocolo,
    atualizarProtocolo,
    desativarProtocolo,
    adicionarPrescricao
  }
})