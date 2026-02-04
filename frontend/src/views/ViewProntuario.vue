<script lang="ts" setup>
import {computed, onActivated, onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/storeGeral.ts'
import {useAuthStore} from '@/stores/storeAuth.ts'
import {Card} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {ArrowLeft, Edit, FileText, Save, X} from 'lucide-vue-next'
import {toast} from "vue-sonner"
import AgendamentoModalDetalhes from '@/components/comuns/AgendamentoModalDetalhes.vue'
import PrescricaoModalDetalhes from '@/components/comuns/PrescricaoModalDetalhes.vue'
import ProntuarioCabecalho from '@/components/pacientes/ProntuarioCabecalho.vue'
import ProntuarioFormulario from '@/components/pacientes/ProntuarioFormulario.vue'
import ProntuarioHistorico from '@/components/pacientes/ProntuarioHistorico.vue'
import {usePacienteFormulario} from '@/composables/usePacienteFormulario.ts'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()

const {
  pacienteSelecionado,
  modoEdicao,
  podeEditar,
  protocoloAtual,
  ultimoAgendamento,
  fields,
  contatos,
  errors,
  selecionarPaciente,
  salvar,
  cancelarEdicao,
  limparSelecao
} = usePacienteFormulario()

const agendamentoDetalhesOpen = ref(false)
const prescricaoDetalhesOpen = ref(false)
const agendamentoSelecionado = ref<any>(null)
const prescricaoSelecionada = ref<any>(null)

const atualizarListas = async () => {
  if (!pacienteSelecionado.value?.id) return
  await Promise.all([
    appStore.fetchPrescricoes(pacienteSelecionado.value.id),
    appStore.fetchAgendamentos(undefined, undefined, pacienteSelecionado.value.id)
  ])
}

onMounted(async () => {
  const id = route.params.id as string
  if (id) {
    let p = appStore.getPacienteById(id)
    if (!p) p = await appStore.carregarPaciente(id)
    if (p) {
      await selecionarPaciente(p)
    } else {
      toast.error("Paciente não encontrado")
      await router.push({name: 'Pacientes'})
    }
  } else {
    await router.push({name: 'Pacientes'})
  }
})

onActivated(async () => {
  await atualizarListas()
})

const handleVoltar = () => {
  limparSelecao()
  router.push({name: 'Pacientes'})
}

const handleVerDetalhesAgendamento = (ag: any) => {
  agendamentoSelecionado.value = ag
  agendamentoDetalhesOpen.value = true
}

const handleVerDetalhesPrescricao = (presc: any) => {
  prescricaoSelecionada.value = presc
  prescricaoDetalhesOpen.value = true
}

const handleVerPrescricaoDoAgendamento = () => {
  if (agendamentoSelecionado.value?.prescricao) {
    prescricaoSelecionada.value = agendamentoSelecionado.value.prescricao
    agendamentoDetalhesOpen.value = false
    prescricaoDetalhesOpen.value = true
  } else {
    toast.error("Prescrição não encontrada nos detalhes do agendamento.")
  }
}

const agendamentosFiltrados = computed(() => {
  if (!pacienteSelecionado.value) return []
  return [...appStore.agendamentos]
      .filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      .sort((a, b) => {
        const dataA = new Date(a.data).getTime()
        const dataB = new Date(b.data).getTime()
        if (dataB !== dataA) return dataB - dataA
        return b.horarioInicio.localeCompare(a.horarioInicio)
      })
})

const prescricoesFiltradas = computed(() => {
  if (!pacienteSelecionado.value) return []
  return [...appStore.prescricoes]
      .filter(p => p.pacienteId === pacienteSelecionado.value?.id)
      .sort((a, b) => {
        const dataA = new Date(a.dataEmissao).getTime()
        const dataB = new Date(b.dataEmissao).getTime()
        if (dataB !== dataA) return dataB - dataA
        const cicloA = a.conteudo?.protocolo?.cicloAtual || 0
        const cicloB = b.conteudo?.protocolo?.cicloAtual || 0
        return cicloB - cicloA
      })
})
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Prontuário</h1>
    <AgendamentoModalDetalhes
        :agendamento="agendamentoSelecionado"
        :open="agendamentoDetalhesOpen"
        :paciente-nome="pacienteSelecionado?.nome"
        @update:open="agendamentoDetalhesOpen = $event"
        @abrir-prescricao="handleVerPrescricaoDoAgendamento"
    />

    <PrescricaoModalDetalhes
        :open="prescricaoDetalhesOpen"
        :paciente-nome="pacienteSelecionado?.nome"
        :prescricao="prescricaoSelecionada"
        @update:open="prescricaoDetalhesOpen = $event"
    />

    <div class="flex items-center justify-between">
      <Button class="flex items-center gap-2" variant="outline" @click="handleVoltar">
        <ArrowLeft class="h-4 w-4"/>
        Voltar para Lista
      </Button>

      <div v-if="pacienteSelecionado" class="flex items-center gap-3">
        <Button
            v-if="['medico', 'admin'].includes(authStore.user?.role || '')"
            class="flex items-center gap-2"
            @click="router.push({ name: 'Prescricao', query: { pacienteId: pacienteSelecionado.id } })"
        >
          <FileText class="h-4 w-4"/>
          Nova Prescrição
        </Button>

        <template v-if="podeEditar">
          <Button
              v-if="!modoEdicao"
              class="flex items-center gap-2"
              variant="outline"
              @click="modoEdicao = true"
          >
            <Edit class="h-4 w-4"/>
            Editar
          </Button>
          <div v-else class="flex gap-2">
            <Button class="flex items-center gap-2" @click="salvar">
              <Save class="h-4 w-4"/>
              Salvar
            </Button>
            <Button class="flex items-center gap-2" variant="outline" @click="cancelarEdicao">
              <X class="h-4 w-4"/>
              Cancelar
            </Button>
          </div>
        </template>
      </div>
    </div>

    <div v-if="pacienteSelecionado" class="space-y-6">
      <Card>
        <ProntuarioCabecalho
            :ciclo-atual="ultimoAgendamento?.detalhes?.infusao?.cicloAtual"
            :dia-ciclo="ultimoAgendamento?.detalhes?.infusao?.diaCiclo"
            :paciente="pacienteSelecionado"
            :protocolo-nome="protocoloAtual?.nome"
        />

        <ProntuarioFormulario
            :contatos="contatos"
            :errors="errors"
            :fields="fields"
            :modo-edicao="modoEdicao"
        />
      </Card>

      <ProntuarioHistorico
          :agendamentos="agendamentosFiltrados"
          :prescricoes="prescricoesFiltradas"
          @ver-agendamento="handleVerDetalhesAgendamento"
          @ver-prescricao="handleVerDetalhesPrescricao"
      />
    </div>

    <div v-else class="py-12 text-center text-gray-500">
      Carregando dados do paciente...
    </div>
  </div>
</template>
