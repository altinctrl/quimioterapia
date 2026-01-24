import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import type {ConfigStatus, ParametrosAgendamento} from '@/types'

const defaultStatusConfig: ConfigStatus[] = [
  {
    id: 'agendado',
    label: 'Agendado',
    cor: 'bg-slate-500 text-white hover:bg-slate-600',
    tipo: 'paciente'
  },
  {
    id: 'aguardando-consulta',
    label: 'Aguardando Consulta',
    cor: 'bg-indigo-500 text-white hover:bg-indigo-600',
    tipo: 'paciente'
  },
  {
    id: 'aguardando-exame',
    label: 'Aguardando Exame',
    cor: 'bg-violet-500 text-white hover:bg-violet-600',
    tipo: 'paciente'
  },
  {
    id: 'aguardando-medicamento',
    label: 'Aguardando Medicação',
    cor: 'bg-purple-500 text-white hover:bg-purple-600',
    tipo: 'paciente'
  },
  {
    id: 'internado',
    label: 'Internado',
    cor: 'bg-orange-500 text-white hover:bg-orange-600',
    tipo: 'paciente'
  },
  {
    id: 'suspenso',
    label: 'Suspenso',
    cor: 'bg-red-600 text-white hover:bg-red-700',
    tipo: 'paciente'
  },
  {
    id: 'remarcado',
    label: 'Remarcado',
    cor: 'bg-gray-200 text-gray-500 border-gray-300',
    tipo: 'paciente'
  },
  {
    id: 'em-triagem',
    label: 'Em Triagem',
    cor: 'bg-blue-500 text-white hover:bg-blue-600',
    tipo: 'paciente'
  },
  {
    id: 'em-infusao',
    label: 'Em Infusão',
    cor: 'bg-green-600 text-white hover:bg-green-700',
    tipo: 'paciente'
  },
  {
    id: 'intercorrencia',
    label: 'Intercorrência',
    cor: 'bg-amber-500 text-white hover:bg-amber-600',
    tipo: 'paciente'
  },
  {
    id: 'concluido',
    label: 'Concluído',
    cor: 'bg-teal-600 text-white hover:bg-teal-700',
    tipo: 'paciente'
  },
  {
    id: 'aguarda-prescricao',
    label: 'Aguarda Prescrição',
    cor: 'bg-red-600 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200',
    tipo: 'farmacia'
  },
  {
    id: 'validando-prescricao',
    label: 'Validando Prescrição',
    cor: 'bg-purple-500 text-white',
    corBadge: 'bg-yellow-100 hover:bg-yellow-100 text-yellow-800 border-yellow-200',
    tipo: 'farmacia'
  },
  {
    id: 'pendente',
    label: 'Pendente',
    cor: 'bg-yellow-500 text-white',
    corBadge: 'bg-gray-100 hover:bg-gray-100 text-gray-800 border-gray-200',
    tipo: 'farmacia'
  },
  {
    id: 'em-preparacao',
    label: 'Em Preparação',
    cor: 'bg-blue-500 text-white',
    corBadge: 'bg-blue-100 hover:bg-blue-100 text-blue-800 border-blue-200',
    tipo: 'farmacia'
  },
  {
    id: 'pronto',
    label: 'Pronto',
    cor: 'bg-green-500 text-white',
    corBadge: 'bg-green-100 hover:bg-green-100 text-green-800 border-green-200',
    tipo: 'farmacia'
  },
  {
    id: 'enviado',
    label: 'Enviado',
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-gray-100 hover:bg-gray-100 text-gray-800 border-gray-200',
    tipo: 'farmacia'
  },
  {
    id: 'med-em-falta',
    label: 'Med. em Falta',
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200',
    tipo: 'farmacia'
  },
  {
    id: 'med-jud-em-falta',
    label: 'Med. Jud. em Falta',
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200',
    tipo: 'farmacia'
  },
  {
    id: 'sem-processo',
    label: 'Sem Processo',
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200',
    tipo: 'farmacia'
  },
  {
    id: 'prescricao-devolvida',
    label: 'Prescrição Devolvida',
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200',
    tipo: 'farmacia'
  }
]

export const useConfiguracaoStore = defineStore('configuracao', () => {
  const statusConfig = ref<ConfigStatus[]>(defaultStatusConfig)
  const parametros = ref<ParametrosAgendamento>({
    horarioAbertura: '',
    horarioFechamento: '',
    diasFuncionamento: [],
    gruposInfusao: {
      rapido: {vagas: 0, duracao: ''},
      medio: {vagas: 0, duracao: ''},
      longo: {vagas: 0, duracao: ''}
    },
    tags: [],
    cargos: [],
    funcoes: [],
    diluentes: [],
  })

  function getStatusConfig(id: string) {
    return statusConfig.value.find(s => s.id === id) || defaultStatusConfig[0]
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

  return {
    statusConfig,
    parametros,
    getStatusConfig,
    fetchConfiguracoes,
    salvarConfiguracoes
  }
})