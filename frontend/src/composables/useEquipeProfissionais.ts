import {computed, reactive, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useEquipeStore} from '@/stores/storeEquipe'
import {Profissional} from '@/types/typesEquipe'
import {toast} from 'vue-sonner'

export function useEquipeProfissionais() {
  const store = useEquipeStore()
  const {profissionais} = storeToRefs(store)

  const isModalOpen = ref(false)
  const isEditing = ref(false)

  const filtros = reactive({
    cargo: 'Todos',
    ativo: 'Todos'
  })

  const formState = reactive<Profissional>({
    username: '',
    nome: '',
    cargo: '',
    registro: '',
    ativo: true
  })

  const profissionaisFiltrados = computed(() => {
    return profissionais.value
      .filter(p => {
        const matchCargo = filtros.cargo === 'Todos' || p.cargo === filtros.cargo
        const matchAtivo = filtros.ativo === 'Todos'
          ? true
          : filtros.ativo === 'Ativos' ? p.ativo : !p.ativo
        return matchCargo && matchAtivo
      })
      .sort((a, b) => a.nome.localeCompare(b.nome))
  })

  function prepararNovoCadastro(cargoPadrao: string) {
    isEditing.value = false
    Object.assign(formState, {
      username: '',
      nome: '',
      cargo: cargoPadrao,
      registro: '',
      ativo: true
    })
    isModalOpen.value = true
  }

  function prepararEdicao(profissional: Profissional) {
    isEditing.value = true
    Object.assign(formState, {...profissional, registro: profissional.registro || ''})
    isModalOpen.value = true
  }

  async function salvarProfissional() {
    if (!formState.username || !formState.nome || !formState.cargo) {
      toast.error('Preencha os campos obrigatórios.')
      return
    }

    try {
      if (isEditing.value) {
        await store.atualizarProfissional(formState.username, {...formState})
        toast.success('Profissional atualizado')
      } else {
        await store.criarProfissional({...formState})
        toast.success('Profissional cadastrado')
      }
      isModalOpen.value = false
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  return {
    profissionaisFiltrados,
    filtros,
    formState,
    isModalOpen,
    isEditing,
    prepararNovoCadastro,
    prepararEdicao,
    salvarProfissional
  }
}
