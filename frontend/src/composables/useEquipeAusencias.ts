import {computed, reactive, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {addMonths, endOfMonth, format, startOfMonth} from 'date-fns'
import {useEquipeStore} from '@/stores/storeEquipe'
import {toast} from 'vue-sonner'

export function useEquipeAusencias() {
  const store = useEquipeStore()
  const {ausencias} = storeToRefs(store)

  const mesReferencia = ref<Date>(new Date())
  const isModalOpen = ref(false)

  const formState = reactive({
    profissional_id: '',
    data_inicio: format(new Date(), 'yyyy-MM-dd'),
    data_fim: format(new Date(), 'yyyy-MM-dd'),
    motivo: 'Folga',
    observacao: ''
  })

  async function carregarAusencias() {
    const start = format(startOfMonth(mesReferencia.value), 'yyyy-MM-dd')
    const end = format(endOfMonth(mesReferencia.value), 'yyyy-MM-dd')
    await store.fetchAusencias(start, end)
  }

  const ausenciasOrdenadas = computed(() => {
    return [...ausencias.value].sort((a, b) => {
      const dateA = new Date(a.data_inicio).getTime()
      const dateB = new Date(b.data_inicio).getTime()
      if (dateA !== dateB) return dateA - dateB
      const dateFimA = new Date(a.data_fim).getTime()
      const dateFimB = new Date(b.data_fim).getTime()
      if (dateFimA !== dateFimB) return dateFimA - dateFimB
      return (a.profissional?.nome || '').localeCompare(b.profissional?.nome || '')
    })
  })

  function abrirModalNovo() {
    Object.assign(formState, {
      profissional_id: '',
      data_inicio: format(new Date(), 'yyyy-MM-dd'),
      data_fim: format(new Date(), 'yyyy-MM-dd'),
      motivo: 'Folga',
      observacao: ''
    })
    isModalOpen.value = true
  }

  async function registrarAusencia() {
    if (!formState.profissional_id || !formState.data_inicio || !formState.data_fim) {
      toast.error('Preencha os campos obrigatórios.')
      return
    }

    try {
      await store.registrarAusencia({...formState})
      toast.success('Ausência registrada')
      await carregarAusencias()
      isModalOpen.value = false
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  async function removerAusencia(id: string) {
    if (!confirm('Tem certeza que deseja remover este registro?')) return

    try {
      await store.removerAusencia(id)
      toast.success('Ausência removida')
    } catch (e: any) {
      toast.error('Erro ao remover')
    }
  }

  function mudarMes(delta: number) {
    mesReferencia.value = addMonths(mesReferencia.value, delta)
  }

  watch(mesReferencia, carregarAusencias, {immediate: true})

  return {
    mesReferencia,
    ausenciasOrdenadas,
    formState,
    isModalOpen,
    mudarMes,
    abrirModalNovo,
    registrarAusencia,
    removerAusencia
  }
}
