<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {ChevronDown, ChevronLeft, ChevronRight, Clock, FileText} from 'lucide-vue-next'
import type {StatusFarmacia} from '@/types'

const router = useRouter()
const appStore = useAppStore()
const dataSelecionada = ref(new Date().toISOString().split('T')[0])

const handleDiaAnterior = () => {
  const d = new Date(dataSelecionada.value)
  d.setDate(d.getDate() - 1)
  dataSelecionada.value = d.toISOString().split('T')[0]
}

const handleProximoDia = () => {
  const d = new Date(dataSelecionada.value)
  d.setDate(d.getDate() + 1)
  dataSelecionada.value = d.toISOString().split('T')[0]
}

const agendamentosDoDia = computed(() => {
  return appStore.agendamentos
      .filter(a => a.data === dataSelecionada.value)
      .sort((a, b) => a.horarioInicio.localeCompare(b.horarioInicio))
})

const metricas = computed(() => {
  const total = agendamentosDoDia.value.length
  const pendente = agendamentosDoDia.value.filter(a => a.statusFarmacia === 'pendente').length
  const emPreparacao = agendamentosDoDia.value.filter(a => a.statusFarmacia === 'em-preparacao').length
  const pronta = agendamentosDoDia.value.filter(a => a.statusFarmacia === 'pronta').length
  const enviada = agendamentosDoDia.value.filter(a => a.statusFarmacia === 'enviada').length
  return {total, pendente, emPreparacao, pronta, enviada}
})

const handleAlterarStatus = (agendamentoId: string, event: Event) => {
  const novoStatus = (event.target as HTMLSelectElement).value as StatusFarmacia
  appStore.atualizarStatusFarmacia(agendamentoId, novoStatus)
}

const handleAlterarHorario = (agendamentoId: string, novoHorario: string | number) => {
  appStore.atualizarHorarioPrevisao(agendamentoId, String(novoHorario))
}

const opcoesStatusFarmacia = computed(() => {
  return appStore.statusConfig.filter(s => s.tipo === 'farmacia')
})

const getStatusDotColor = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config ? config.cor.split(' ')[0] : 'bg-gray-200'
}

const irParaProntuario = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const formatarStatus = (status: string) => {
  if (!status) return ''
  return status.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const isBloqueado = (status: string) => ['suspenso', 'remarcado'].includes(status)

watch(dataSelecionada, async (novaData) => {
  await appStore.fetchAgendamentos(novaData, novaData)
  const pacientesIds = [...new Set(appStore.agendamentos.map(a => a.pacienteId))]
  if (pacientesIds.length > 0) {
    await Promise.all(pacientesIds.map(id => appStore.fetchPrescricoes(id)))
  }
}, {immediate: true})

const getProtocoloInferido = (pid: string) => appStore.getProtocoloPeloHistorico(pid)
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Farmácia</h1>
    <Card>
      <CardContent class="pt-6">
        <div class="flex items-center gap-4">
          <!--           <label class="text-sm text-gray-600 font-medium">Data:</label> -->

          <div class="flex items-center gap-2">
            <Button size="icon" variant="outline" @click="handleDiaAnterior">
              <ChevronLeft class="h-4 w-4"/>
            </Button>

            <Input v-model="dataSelecionada" class="w-auto" type="date"/>

            <Button size="icon" variant="outline" @click="handleProximoDia">
              <ChevronRight class="h-4 w-4"/>
            </Button>
          </div>
          <div class="ml-auto text-sm text-gray-600">
            {{
              new Date(dataSelecionada).toLocaleDateString('pt-BR', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              })
            }}
          </div>
        </div>
      </CardContent>
    </Card>

    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <Card>
        <CardContent class="pt-6"><p class="text-3xl font-bold">{{ metricas.total }}</p>
          <p class="text-xs">Total</p></CardContent>
      </Card>
      <Card>
        <CardContent class="pt-6"><p class="text-3xl font-bold text-yellow-600">{{ metricas.pendente }}</p>
          <p class="text-xs">Pendentes</p></CardContent>
      </Card>
      <Card>
        <CardContent class="pt-6"><p class="text-3xl font-bold text-blue-600">{{ metricas.emPreparacao }}</p>
          <p class="text-xs">Preparando</p></CardContent>
      </Card>
      <Card>
        <CardContent class="pt-6"><p class="text-3xl font-bold text-green-600">{{ metricas.pronta }}</p>
          <p class="text-xs">Prontas</p></CardContent>
      </Card>
      <Card>
        <CardContent class="pt-6"><p class="text-3xl font-bold text-gray-600">{{ metricas.enviada }}</p>
          <p class="text-xs">Enviadas</p></CardContent>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Preparações do Dia</CardTitle>
      </CardHeader>
      <CardContent>
        <div v-if="agendamentosDoDia.length === 0" class="text-center py-12 text-gray-500">
          <FileText class="h-12 w-12 mx-auto mb-3 text-gray-300"/>
          <p>Nenhuma preparação agendada para este dia</p>
        </div>

        <Table v-else>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[100px]">Horário</TableHead>
              <TableHead class="min-w-[150px]">Paciente</TableHead>
              <TableHead class="min-w-[100px]">Protocolo</TableHead>
              <TableHead class="w-[140px]">Status Paciente</TableHead>
              <TableHead class="w-[200px]">Status Farmácia</TableHead>
              <TableHead class="w-[140px]">Previsão Entrega</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="agendamento in agendamentosDoDia" :key="agendamento.id"
                      :class="{'opacity-75 bg-gray-50': isBloqueado(agendamento.status)}">
              <TableCell>
                <div class="font-mono text-sm">{{ agendamento.horarioInicio }}</div>
                <div class="text-xs text-muted-foreground capitalize">{{ agendamento.turno }}</div>
              </TableCell>

              <TableCell>
                <button
                    class="text-left font-medium hover:text-blue-600 underline truncate max-w-[180px]"
                    @click="irParaProntuario(agendamento.pacienteId)"
                >
                  {{agendamento.paciente?.nome || 'Paciente não carregado'}}
                </button>
                <div class="text-xs text-gray-500">{{agendamento.paciente?.registro}}</div>
              </TableCell>

              <TableCell>
                <span :title="getProtocoloInferido(agendamento.pacienteId)?.nome || '-'"
                      class="text-sm font-medium text-gray-700 block">
                  {{ getProtocoloInferido(agendamento.pacienteId)?.nome || '-' }}
                </span>
              </TableCell>

              <TableCell>
                <Badge :variant="isBloqueado(agendamento.status) ? 'destructive' : 'secondary'">
                  {{ formatarStatus(agendamento.status) }}
                </Badge>
              </TableCell>

              <TableCell>
                <div class="flex items-center gap-2">

                  <div
                      :class="[
                      'h-2.5 w-2.5 rounded-full flex-shrink-0',
                      getStatusDotColor(isBloqueado(agendamento.status) ? 'pendente' : agendamento.statusFarmacia)
                    ]"
                  />

                  <div class="relative w-[160px]">
                    <select
                        :disabled="isBloqueado(agendamento.status)"
                        :value="isBloqueado(agendamento.status) ? 'pendente' : agendamento.statusFarmacia"
                        class="flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-1 pr-8 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none truncate"
                        @change="(e) => handleAlterarStatus(agendamento.id, e)"
                    >
                      <option
                          v-for="opcao in opcoesStatusFarmacia"
                          :key="opcao.id"
                          :value="opcao.id"
                      >
                        {{ opcao.label }}
                      </option>
                    </select>

                    <ChevronDown class="absolute right-2 top-2.5 h-4 w-4 opacity-50 pointer-events-none"/>
                  </div>
                </div>
              </TableCell>

              <TableCell>
                <div class="flex items-center gap-1">
                  <Clock class="h-3 w-3 text-gray-400"/>
                  <Input
                      :disabled="isBloqueado(agendamento.status)"
                      :model-value="isBloqueado(agendamento.status) ? '' : agendamento.horarioPrevisaoEntrega"
                      class="w-32 h-9"
                      type="time"
                      @update:model-value="(v) => handleAlterarHorario(agendamento.id, v)"
                  />
                </div>
              </TableCell>

            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
</template>
