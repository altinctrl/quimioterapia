import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {ConfigStatus, ParametrosAgendamento} from "@/types/typesAjustes.ts";
import {AgendamentoStatusEnum, FarmaciaStatusEnum} from "@/types/typesAgendamento.ts";
import {
  CORES_PADRAO_AGENDAMENTO,
  CORES_PADRAO_FARMACIA,
  LABELS_STATUS_AGENDAMENTO,
  LABELS_STATUS_FARMACIA
} from "@/constants/constStatus.ts";

const defaultStatusConfig: ConfigStatus[] = [
  ...Object.values(AgendamentoStatusEnum).map(status => ({
    id: status,
    label: LABELS_STATUS_AGENDAMENTO[status],
    cor: CORES_PADRAO_AGENDAMENTO[status],
    tipo: 'paciente' as const
  })),
  ...Object.values(FarmaciaStatusEnum).map(status => ({
    id: status,
    label: LABELS_STATUS_FARMACIA[status],
    cor: CORES_PADRAO_FARMACIA[status].cor,
    corBadge: CORES_PADRAO_FARMACIA[status].corBadge,
    tipo: 'farmacia' as const
  }))
];

export const useConfiguracaoStore = defineStore('configuracao', () => {
  const statusConfig = ref<ConfigStatus[]>(defaultStatusConfig)
  const parametros = ref<ParametrosAgendamento>({
    horarioAbertura: '',
    horarioFechamento: '',
    diasFuncionamento: [],
    vagas: {
      infusao_rapido: 16,
      infusao_medio: 8,
      infusao_longo: 4,
      infusao_extra_longo: 4,
      consultas: 10,
      procedimentos: 10
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