import {computed, reactive, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {addDays, format} from 'date-fns'
import {useEquipeStore} from '@/stores/storeEquipe'
import {toast} from 'vue-sonner'

export function useEquipeEscala(funcoesDisponiveis: string[]) {
  const store = useEquipeStore()
  const {escalaDia, profissionais} = storeToRefs(store)

  const dataSelecionada = ref<Date>(new Date())

  const formState = reactive({
    profissional_id: '',
    funcao: '',
    turno: 'Integral' as 'Manhã' | 'Tarde' | 'Integral'
  })

  const escalaOrdenada = computed(() => {
    return [...escalaDia.value].sort((a, b) => {
      const funcCompare = a.funcao.localeCompare(b.funcao)
      if (funcCompare !== 0) return funcCompare

      const turnoCompare = a.turno.localeCompare(b.turno)
      if (turnoCompare !== 0) return turnoCompare

      return (a.profissional?.nome || '').localeCompare(b.profissional?.nome || '')
    })
  })

  const profissionaisDisponiveis = computed(() => {
    return profissionais.value.filter(p =>
      p.ativo && (p.cargo.includes('Enfermeiro') || p.cargo.includes('Técnico'))
    )
  })

  async function adicionarEscala() {
    if (!formState.profissional_id) {
      toast.error('Selecione um profissional.')
      return
    }

    try {
      await store.adicionarEscala({
        data: format(dataSelecionada.value, 'yyyy-MM-dd'),
        ...formState
      })
      toast.success('Adicionado à escala')
      formState.profissional_id = '' // Reset parcial
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  async function removerEscala(id: string) {
    try {
      await store.removerEscala(id)
      toast.success('Removido da escala')
    } catch (e: any) {
      toast.error('Erro ao remover')
    }
  }

  function mudarDia(delta: number) {
    dataSelecionada.value = addDays(dataSelecionada.value, delta)
  }

  watch(dataSelecionada, async (novaData) => {
    await store.fetchEscalaDia(format(novaData, 'yyyy-MM-dd'))
  }, {immediate: true})

  watch(() => funcoesDisponiveis, (newVal) => {
    if (newVal.length > 0 && !formState.funcao) {
      formState.funcao = newVal[0]
    }
  }, {immediate: true})

  return {
    dataSelecionada,
    escalaOrdenada,
    profissionaisDisponiveis,
    formState,
    mudarDia,
    adicionarEscala,
    removerEscala
  }
}
