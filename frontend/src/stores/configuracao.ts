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
    id: 'pendente',
    label: 'Pendente',
    cor: 'bg-gray-500 text-white',
    tipo: 'farmacia'
  },
  {
    id: 'em-preparacao',
    label: 'Em Preparação',
    cor: 'bg-blue-500 text-white',
    tipo: 'farmacia'
  },
  {
    id: 'pronta',
    label: 'Pronta',
    cor: 'bg-green-500 text-white',
    tipo: 'farmacia'
  },
  {
    id: 'enviada',
    label: 'Enviada',
    cor: 'bg-purple-600 text-white',
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