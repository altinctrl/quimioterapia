import {computed, ref, watch} from 'vue'
import {useAppStore} from '@/stores/app'
import type {FiltrosPacientes} from '@/components/pacientes/PacientesControls.vue'

export function usePacientesList() {
  const appStore = useAppStore()

  const loading = ref(false)
  const page = ref(1)
  const termoBusca = ref('')
  const filtros = ref<FiltrosPacientes>({
    ordenacao: 'recentes',
    perPage: 20
  })

  const totalPages = computed(() => Math.ceil(appStore.totalPacientes / filtros.value.perPage) || 1)

  const carregarDados = async () => {
    loading.value = true
    try {
      await appStore.fetchPacientes(
        page.value,
        filtros.value.perPage,
        termoBusca.value,
        filtros.value.ordenacao
      )
    } finally {
      loading.value = false
    }
  }

  let timeoutBusca: number
  const handleBuscaInput = (valor: any) => {
    termoBusca.value = typeof valor === 'string' ? valor : valor?.target?.value || ''
    clearTimeout(timeoutBusca)
    timeoutBusca = setTimeout(() => {
      page.value = 1
      carregarDados().catch(console.error)
    }, 500)
  }

  const resetFiltros = () => {
    filtros.value = {ordenacao: 'recentes', perPage: 20}
    termoBusca.value = ''
    page.value = 1
    carregarDados().catch(console.error)
  }

  watch(() => filtros.value.ordenacao, carregarDados)
  watch(() => filtros.value.perPage, () => {
    page.value = 1
    carregarDados().catch(console.error)
  })
  watch(page, carregarDados)

  return {
    filtros,
    page,
    termoBusca,
    loading,
    totalPages,
    carregarDados,
    handleBuscaInput,
    resetFiltros
  }
}
