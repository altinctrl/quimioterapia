import {computed, reactive, ref} from 'vue'
import {useFieldArray, useForm} from 'vee-validate'
import {toast} from 'vue-sonner'
import {useAppStore} from '@/stores/app'
import {useAuthStore} from '@/stores/auth'
import {pacienteFormSchema} from '@/schemas/pacienteSchema'
import {ContatoEmergencia, Paciente} from "@/types/pacienteTypes.ts";

export function usePacienteForm() {
  const appStore = useAppStore()
  const authStore = useAuthStore()

  const pacienteSelecionado = ref<Paciente | null>(null)
  const modoEdicao = ref(false)

  const {
    handleSubmit,
    resetForm,
    values,
    errors,
    defineField,
    setValues
  } = useForm({
    validationSchema: pacienteFormSchema,
    initialValues: {contatosEmergencia: []}
  })

  const [nome, nomeProps] = defineField('nome')
  const [cpf, cpfProps] = defineField('cpf')
  const [registro, registroProps] = defineField('registro')
  const [dataNascimento, dataNascimentoProps] = defineField('dataNascimento')
  const [sexo, sexoProps] = defineField('sexo')
  const [peso, pesoProps] = defineField('peso')
  const [altura, alturaProps] = defineField('altura')
  const [telefone, telefoneProps] = defineField('telefone')
  const [email, emailProps] = defineField('email')
  const [observacoesClinicas, observacoesClinicasProps] = defineField('observacoesClinicas')

  const {
    fields: contatosFields,
    push: pushContato,
    remove: removeContato
  } = useFieldArray('contatosEmergencia')

  const podeEditar = computed(() => authStore.user?.role !== 'farmacia')

  const protocoloAtual = computed(() => {
    if (!pacienteSelecionado.value) return null
    const prescricoes = appStore.prescricoes.filter(p => {
      return p.pacienteId === pacienteSelecionado.value?.id ||
        p.conteudo?.paciente?.prontuario === pacienteSelecionado.value?.registro
    })

    if (prescricoes.length > 0) {
      const ultima = prescricoes.sort((a, b) =>
        new Date(b.dataEmissao).getTime() - new Date(a.dataEmissao).getTime()
      )[0]
      return ultima?.conteudo?.protocolo || null
    }
    return null
  })

  const ultimoAgendamento = computed(() => {
    if (!pacienteSelecionado.value) return null
    const statusIgnorados = ['agendado', 'remarcado']

    const agendamentos = appStore.agendamentos
      .filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      .filter(a => !statusIgnorados.includes(a.status))
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())

    return agendamentos[0] || null
  })


  const limparContatosVazios = () => {
    for (let i = contatosFields.value.length - 1; i >= 0; i--) {
      const contato = contatosFields.value[i].value as ContatoEmergencia
      const estaVazio = !contato.nome?.trim() &&
        !contato.parentesco?.trim() &&
        !contato.telefone?.trim()

      if (estaVazio) {
        removeContato(i)
      }
    }
  }

  const selecionarPaciente = async (paciente: Paciente) => {
    pacienteSelecionado.value = paciente

    await Promise.all([
      appStore.fetchPrescricoes(paciente.id),
      appStore.fetchAgendamentos(undefined, undefined, paciente.id)
    ])

    setValues({
      ...paciente,
      telefone: paciente.telefone ?? '',
      email: paciente.email ?? '',
      sexo: paciente.sexo ?? '',
      contatosEmergencia: paciente.contatosEmergencia?.map(c => ({...c})) || []
    } as any)

    modoEdicao.value = false
  }

  const salvar = async () => {
    limparContatosVazios()
    await _handleSave()
  }

  const _handleSave = handleSubmit(async (formValues) => {
    if (!pacienteSelecionado.value?.id) return

    try {
      await appStore.atualizarPaciente(pacienteSelecionado.value.id, formValues as Partial<Paciente>)
      toast.success('Paciente atualizado com sucesso!')

      const atualizado = appStore.getPacienteById(pacienteSelecionado.value.id)
      if (atualizado) {
        pacienteSelecionado.value = atualizado
        setValues({
          ...atualizado,
          contatosEmergencia: atualizado.contatosEmergencia?.map(c => ({...c})) || []
        } as any)
      }
      modoEdicao.value = false
    } catch (error) {
      console.error(error)
      toast.error('Erro ao salvar paciente')
    }
  })

  const cancelarEdicao = () => {
    if (pacienteSelecionado.value) {
      setValues({
        ...pacienteSelecionado.value,
        telefone: pacienteSelecionado.value.telefone ?? '',
        email: pacienteSelecionado.value.email ?? '',
        contatosEmergencia: pacienteSelecionado.value.contatosEmergencia?.map(c => ({...c})) || []
      } as any)
    }
    modoEdicao.value = false
  }

  const limparSelecao = () => {
    pacienteSelecionado.value = null
    modoEdicao.value = false
    resetForm()
  }

  return {
    pacienteSelecionado,
    modoEdicao,
    podeEditar,
    protocoloAtual,
    ultimoAgendamento,

    values,
    errors,
    fields: {
      nome, nomeProps,
      cpf, cpfProps,
      registro, registroProps,
      dataNascimento, dataNascimentoProps,
      sexo, sexoProps,
      peso, pesoProps,
      altura, alturaProps,
      telefone, telefoneProps,
      email, emailProps,
      observacoesClinicas, observacoesClinicasProps
    },
    contatos: reactive({
      fields: contatosFields,
      push: pushContato,
      remove: removeContato
    }),

    selecionarPaciente,
    salvar,
    cancelarEdicao,
    limparSelecao
  }
}
