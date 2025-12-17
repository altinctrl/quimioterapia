<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {useAuthStore} from '@/stores/auth'
import type {Paciente} from '@/types'

import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {ArrowLeft, Edit, FileText, Save, Search, UserPlus, X} from 'lucide-vue-next'

import AgendamentoDetalhesModal from '@/components/modals/AgendamentoDetalhesModal.vue'
import PrescricaoHistoricoModal from '@/components/modals/PrescricaoHistoricoModal.vue'

import PacientesTable from '@/components/pacientes/PacientesTable.vue'
import PacienteImportModal from '@/components/pacientes/PacienteImportModal.vue'
import ProntuarioHeader from '@/components/pacientes/ProntuarioHeader.vue'
import ProntuarioForm from '@/components/pacientes/ProntuarioForm.vue'
import ProntuarioHistorico from '@/components/pacientes/ProntuarioHistorico.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()

const page = ref(1)
const perPage = ref(10)
const termoBusca = ref('')
const dialogNovoPaciente = ref(false)

const pacienteSelecionado = ref<Paciente | null>(null)
const modoEdicao = ref(false)
const dadosEditados = ref<Partial<Paciente>>({})

const agendamentoDetalhesOpen = ref(false)
const prescricaoDetalhesOpen = ref(false)
const agendamentoSelecionado = ref<any>(null)
const prescricaoSelecionada = ref<any>(null)

const podeEditar = computed(() => authStore.user?.role !== 'farmacia')

const pacientesFiltrados = computed(() => {
  if (!termoBusca.value || termoBusca.value.length < 2) return appStore.pacientes
  const termo = termoBusca.value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  return appStore.pacientes.filter((paciente) => {
    const nomeNormalizado = paciente.nome.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    const cpfLimpo = paciente.cpf?.replace(/[.\-]/g, '') || ''
    const termoBuscaLimpo = termo.replace(/[.\-]/g, '')
    return (
        nomeNormalizado.includes(termo) ||
        paciente.registro.toLowerCase().includes(termo) ||
        cpfLimpo.includes(termoBuscaLimpo)
    )
  })
})

const protocoloAtual = computed(() => {
  if (!pacienteSelecionado.value) return null
  const prescricoes = appStore.prescricoes.filter(p => p.pacienteId === pacienteSelecionado.value?.id)
  if (prescricoes.length > 0) {
    const ultima = prescricoes.sort((a, b) => new Date(b.dataPrescricao).getTime() - new Date(a.dataPrescricao).getTime())[0]
    if (ultima.protocoloId) {
      return appStore.protocolos.find(p => p.id === ultima.protocoloId)
    }
    if (ultima.protocolo) return {nome: ultima.protocolo} as any
  }
  return null
})

const ultimoAgendamento = computed(() => {
  if (!pacienteSelecionado.value) return null
  const agendamentos = appStore.agendamentos
      .filter(a => a.pacienteId === pacienteSelecionado.value?.id)
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
  return agendamentos[0] || null
})

const carregarPacienteDaUrl = async () => {
  if (route.query.pacienteId) {
    const pid = route.query.pacienteId as string
    const p = appStore.getPacienteById(pid)
    if (p) {
      pacienteSelecionado.value = p
      dadosEditados.value = JSON.parse(JSON.stringify(p))
      await Promise.all([
        appStore.fetchPrescricoes(pid),
        appStore.fetchAgendamentos(pid)
      ])
    }
  } else {
    pacienteSelecionado.value = null
  }
}

const carregarDadosPagina = async () => {
  await appStore.fetchPacientes(page.value, perPage.value, termoBusca.value)
  const promises = appStore.pacientes.map(p => appStore.fetchPrescricoes(p.id))
  await Promise.all(promises)
}

onMounted(() => {
  carregarPacienteDaUrl()
})

watch([page, termoBusca], () => {
  carregarDadosPagina()
}, {immediate: true})

watch(() => route.query.pacienteId, () => {
  carregarPacienteDaUrl()
})

const handleSelecionarPaciente = (paciente: Paciente) => {
  router.push({query: {pacienteId: paciente.id}})
}

const handlePacienteImportado = (paciente: Paciente) => {
  handleSelecionarPaciente(paciente)
}

const handleVoltar = () => {
  if (route.query.pacienteId) {
    router.push({query: {}})
  } else {
    pacienteSelecionado.value = null
    modoEdicao.value = false
  }
}

const handleSalvarEdicao = () => {
  if (pacienteSelecionado.value && pacienteSelecionado.value.id) {
    const idx = appStore.pacientes.findIndex(p => p.id === pacienteSelecionado.value?.id)
    if (idx !== -1) {
      appStore.pacientes[idx] = {...appStore.pacientes[idx], ...dadosEditados.value} as Paciente
      pacienteSelecionado.value = appStore.pacientes[idx]
    }
  }
  modoEdicao.value = false
}

const handleCancelarEdicao = () => {
  dadosEditados.value = JSON.parse(JSON.stringify(pacienteSelecionado.value))
  modoEdicao.value = false
}

const handleVerDetalhesAgendamento = (ag: any) => {
  agendamentoSelecionado.value = ag
  agendamentoDetalhesOpen.value = true
}

const handleVerDetalhesPrescricao = (presc: any) => {
  prescricaoSelecionada.value = presc
  prescricaoDetalhesOpen.value = true
}

const agendamentosFiltrados = computed(() =>
    pacienteSelecionado.value ? appStore.agendamentos.filter(a => a.pacienteId === pacienteSelecionado.value?.id) : []
)
const prescricoesFiltradas = computed(() =>
    pacienteSelecionado.value ? appStore.prescricoes.filter(p => p.pacienteId === pacienteSelecionado.value?.id) : []
)

</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Pacientes</h1>

    <AgendamentoDetalhesModal
        :agendamento="agendamentoSelecionado"
        :open="agendamentoDetalhesOpen"
        :paciente-nome="pacienteSelecionado?.nome"
        @update:open="agendamentoDetalhesOpen = $event"
    />

    <PrescricaoHistoricoModal
        :open="prescricaoDetalhesOpen"
        :paciente-nome="pacienteSelecionado?.nome"
        :prescricao="prescricaoSelecionada"
        @update:open="prescricaoDetalhesOpen = $event"
    />

    <div v-if="!pacienteSelecionado" class="space-y-6">
      <Card>
        <CardContent class="pt-6">
          <div class="flex gap-3">
            <div class="flex-1 relative">
              <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"/>
              <Input
                  v-model="termoBusca"
                  class="pl-10"
                  placeholder="Buscar por nome, CPF ou prontuário..."
              />
            </div>

            <div v-if="podeEditar">
              <Button class="flex items-center gap-2" @click="dialogNovoPaciente = true">
                <UserPlus class="h-4 w-4"/>
                Novo Paciente
              </Button>

              <PacienteImportModal
                  v-model:open="dialogNovoPaciente"
                  @paciente-importado="handlePacienteImportado"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            {{ termoBusca ? `${pacientesFiltrados.length} paciente(s) encontrado(s)` : 'Todos os Pacientes' }}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <PacientesTable
              v-model:page="page"
              :pacientes="pacientesFiltrados"
              :per-page="perPage"
              :total="appStore.totalPacientes"
              @select="handleSelecionarPaciente"
          />
        </CardContent>
      </Card>
    </div>

    <div v-else class="space-y-6">
      <div class="flex items-center justify-between">
        <Button class="flex items-center gap-2" variant="outline" @click="handleVoltar">
          <ArrowLeft class="h-4 w-4"/>
          Voltar
        </Button>

        <div class="flex items-center gap-3">
          <Button
              v-if="authStore.user?.role === 'medico'"
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
              <Button class="flex items-center gap-2" variant="outline" @click="handleCancelarEdicao">
                <X class="h-4 w-4"/>
                Cancelar
              </Button>
              <Button class="flex items-center gap-2" @click="handleSalvarEdicao">
                <Save class="h-4 w-4"/>
                Salvar
              </Button>
            </div>
          </template>
        </div>
      </div>

      <Card>
        <ProntuarioHeader
            :ciclo-atual="ultimoAgendamento?.cicloAtual"
            :dia-ciclo="ultimoAgendamento?.diaCiclo"
            :paciente="pacienteSelecionado"
            :protocolo-nome="protocoloAtual?.nome"
        />

        <ProntuarioForm
            v-model="dadosEditados"
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
  </div>
</template>