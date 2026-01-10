<script lang="ts" setup>
import {computed, ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {usePrescricaoStore} from '@/stores/prescricao'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Badge} from '@/components/ui/badge'
import {Button} from '@/components/ui/button'
import {Checkbox} from '@/components/ui/checkbox'
import {
  ChevronDown,
  ChevronRight,
  Clock,
  FileText,
  CheckCircle2,
  Beaker,
  Pill
} from 'lucide-vue-next'
import {isInfusao, type StatusFarmacia, type Agendamento} from '@/types'

const props = defineProps<{
  agendamentos: Agendamento[]
}>()

const emit = defineEmits<{
  (e: 'alterarStatus', id: string, novoStatus: StatusFarmacia): void
  (e: 'alterarHorario', id: string, novoHorario: string): void
}>()

const router = useRouter()
const appStore = useAppStore()
const prescricaoStore = usePrescricaoStore()

// Estado local para expansão e checklist
const expandedRows = ref<Set<string>>(new Set())
const checklist = ref<Record<string, Record<string, boolean>>>({})

const toggleExpand = (id: string) => {
  const newSet = new Set(expandedRows.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  expandedRows.value = newSet
}

const opcoesStatusFarmacia = computed(() => {
  return appStore.statusConfig.filter(s => s.tipo === 'farmacia')
})

const getStatusDotColor = (statusId: string) => {
  const config = appStore.getStatusConfig(statusId)
  return config ? config.cor.split(' ')[0] : 'bg-gray-200'
}

const getProtocoloInferido = (pid: string) => appStore.getProtocoloPeloHistorico(pid)

const formatarStatus = (status: string) => {
  if (!status) return ''
  return status.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const isBloqueado = (status: string) => ['suspenso', 'remarcado'].includes(status)

const irParaProntuario = (pacienteId: string) => {
  router.push({path: '/pacientes', query: {pacienteId}})
}

const onStatusChange = (id: string, event: Event) => {
  const val = (event.target as HTMLSelectElement).value as StatusFarmacia
  emit('alterarStatus', id, val)
}

// Prescricao & Checklist Logic
const getMedicamentos = (ag: Agendamento) => {
  // Prescrição mais recente do paciente
  const lista = prescricaoStore.getPrescricoesPorPaciente(ag.pacienteId)
  if (!lista || lista.length === 0) return null

  const prescricao = [...lista].sort(
    (a, b) => new Date(b.dataPrescricao).getTime() - new Date(a.dataPrescricao).getTime()
  )[0]

  const itens = prescricao.medicamentos || []
  const pre = itens.filter(i => i.tipo === 'pre')
  const qt = itens.filter(i => i.tipo === 'qt')
  const pos = itens.filter(i => i.tipo === 'pos')

  return {
    id: prescricao.id,
    total: itens.length,
    pre,
    qt,
    pos
  }
}

const toggleCheck = (agId: string, itemNome: string, statusAtual: StatusFarmacia) => {
  if (!checklist.value[agId]) {
    checklist.value[agId] = {}
  }
  checklist.value[agId][itemNome] = !checklist.value[agId][itemNome]
  
  // Lógica de Atualização Automática
  const checks = checklist.value[agId]
  const totalChecked = Object.values(checks).filter(Boolean).length
  
  if (statusAtual === 'pendente' && totalChecked > 0) {
    emit('alterarStatus', agId, 'em-preparacao')
  }
  
  // Verificar se tudos estão marcados é complexo sem saber o total exato aqui facilmente
  // Mas podemos verificar no render loop ou inferir. 
  // Por simplicidade, se o usuário marcou algo, mudamos para Em Preparação. 
  // Pronta deve ser manual ou se ele marcar tudo (implementação futura mais robusta).
}

const isChecked = (agId: string, itemNome: string) => {
  return checklist.value[agId]?.[itemNome] || false
}
</script>

<template>
  <div>
    <div v-if="agendamentos.length === 0" class="text-center py-12 text-gray-500 bg-gray-50">
      <FileText class="h-12 w-12 mx-auto mb-3 text-gray-300"/>
      <p>Nenhuma preparação corresponde aos filtros.</p>
    </div>

    <Table v-else>
      <TableHeader class="bg-gray-50/50">
        <TableRow>
          <TableHead class="w-[50px]"></TableHead> <!-- Expander -->
          <TableHead class="w-[100px]">Horário</TableHead>
          <TableHead class="min-w-[150px]">Paciente</TableHead>
          <TableHead class="min-w-[100px]">Protocolo</TableHead>
          <TableHead class="w-[140px]">Status Paciente</TableHead>
          <TableHead class="w-[220px]">Status Farmácia</TableHead>
          <TableHead class="w-[140px]">Previsão</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-for="agendamento in agendamentos" :key="agendamento.id">
          <!-- Linha Principal -->
          <TableRow 
            class="group transition-colors hover:bg-gray-50/50"
            :class="{'bg-gray-50 opacity-75': isBloqueado(agendamento.status)}"
          >
            <TableCell class="p-2 text-center">
              <Button 
                variant="ghost" 
                size="icon" 
                class="h-8 w-8 text-gray-400 hover:text-gray-900"
                @click="toggleExpand(agendamento.id)"
              >
                <ChevronDown v-if="expandedRows.has(agendamento.id)" class="h-4 w-4"/>
                <ChevronRight v-else class="h-4 w-4"/>
              </Button>
            </TableCell>

            <TableCell>
              <div class="font-mono text-sm font-medium text-gray-700">{{ agendamento.horarioInicio }}</div>
              <div class="text-xs text-muted-foreground capitalize">{{ agendamento.turno }}</div>
            </TableCell>

            <TableCell>
              <button
                  class="text-left font-medium hover:text-blue-600 hover:underline truncate max-w-[180px] text-gray-900"
                  @click="irParaProntuario(agendamento.pacienteId)"
              >
                {{ agendamento.paciente?.nome || 'Paciente não carregado' }}
              </button>
              <div class="text-xs text-gray-500">{{ agendamento.paciente?.registro }}</div>
            </TableCell>

            <TableCell>
              <span :title="getProtocoloInferido(agendamento.pacienteId)?.nome || '-'"
                    class="text-sm font-medium text-gray-700 block truncate max-w-[150px]">
                {{ getProtocoloInferido(agendamento.pacienteId)?.nome || '-' }}
              </span>
            </TableCell>

            <TableCell>
               <!-- Badge simplificado alinhado com layout -->
              <Badge :variant="isBloqueado(agendamento.status) ? 'destructive' : 'outline'" 
                     class="font-normal capitalize">
                {{ formatarStatus(agendamento.status) }}
              </Badge>
            </TableCell>

            <TableCell>
              <div class="flex items-center gap-2">
                <div
                    :class="[
                    'h-2.5 w-2.5 rounded-full flex-shrink-0 shadow-sm transition-colors',
                    getStatusDotColor(isBloqueado(agendamento.status) ? 'pendente' : (isInfusao(agendamento) ? agendamento.detalhes.infusao.status_farmacia : 'pendente'))
                  ]"
                />
                <div class="relative w-full max-w-[150px]">
                  <select
                      :disabled="isBloqueado(agendamento.status)"
                      :value="isInfusao(agendamento) ? agendamento.detalhes.infusao.status_farmacia : 'pendente'"
                      class="flex h-8 w-full items-center justify-between rounded-md border border-input bg-transparent px-2 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none truncate font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                      @change="(e) => onStatusChange(agendamento.id, e)"
                  >
                    <option
                        v-for="opcao in opcoesStatusFarmacia"
                        :key="opcao.id"
                        :value="opcao.id"
                    >
                      {{ opcao.label }}
                    </option>
                  </select>
                  <ChevronDown class="absolute right-2 top-2.5 h-3 w-3 opacity-50 pointer-events-none"/>
                </div>
              </div>
            </TableCell>

            <TableCell>
              <div class="flex items-center gap-1.5">
                <Clock class="h-3.5 w-3.5 text-gray-400"/>
                <input
                    :disabled="isBloqueado(agendamento.status)"
                    :value="isInfusao(agendamento) ? agendamento.detalhes.infusao.horario_previsao_entrega : ''"
                    class="w-24 h-8 text-sm bg-transparent border-b border-transparent hover:border-gray-300 focus:border-primary focus:outline-none transition-colors"
                    type="time"
                    @input="(e) => emit('alterarHorario', agendamento.id, (e.target as HTMLInputElement).value)"
                />
              </div>
            </TableCell>
          </TableRow>

          <!-- Linha Expandida (Checklist) -->
          <TableRow v-if="expandedRows.has(agendamento.id)" class="bg-gray-50/80 border-t-0 shadow-inner">
            <TableCell colspan="7" class="p-0">
              <div class="p-4 grid md:grid-cols-3 gap-6 animate-in slide-in-from-top-1 duration-200">
                <div v-if="!getMedicamentos(agendamento)" class="col-span-3 text-center text-muted-foreground text-sm py-4">
                  Nenhuma prescrição encontrada para hoje.
                </div>

                <template v-else>
                  <div
                      v-if="getMedicamentos(agendamento)?.total === 0"
                      class="col-span-3 text-center text-muted-foreground text-sm py-4"
                  >
                    Prescrição sem medicamentos.
                  </div>

                   <!-- PRE -->
                   <div v-if="getMedicamentos(agendamento)?.pre.length" class="space-y-3">
                      <div class="flex items-center gap-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        <Pill class="h-3 w-3"/> Pré-Quimioterapia
                      </div>
                      <div class="space-y-2">
                        <div v-for="(med, idx) in getMedicamentos(agendamento)?.pre" :key="`${med.tipo}:${med.nome}:${idx}`" 
                             class="flex items-start gap-2 group/item">
                          <Checkbox 
                            :id="`pre-${agendamento.id}-${idx}`"
                            :checked="isChecked(agendamento.id, `${med.tipo}:${med.nome}`)"
                            @update:checked="() => toggleCheck(agendamento.id, `${med.tipo}:${med.nome}`, isInfusao(agendamento) ? agendamento.detalhes.infusao.status_farmacia : 'pendente')"
                            class="mt-0.5"
                          />
                          <label :for="`pre-${agendamento.id}-${idx}`" class="text-sm leading-tight peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer">
                            <span class="font-medium text-gray-800">{{ med.nome }}</span>
                            <span class="text-gray-500 ml-1 text-xs">{{ med.dose }} {{ med.unidade }} - {{ med.via }}</span>
                          </label>
                        </div>
                      </div>
                   </div>
                   
                   <!-- QT -->
                   <div v-if="getMedicamentos(agendamento)?.qt.length" class="space-y-3">
                      <div class="flex items-center gap-2 text-xs font-semibold text-rose-600 uppercase tracking-wider">
                        <Beaker class="h-3 w-3"/> Quimioterapia
                      </div>
                      <div class="space-y-2">
                        <div v-for="(med, idx) in getMedicamentos(agendamento)?.qt" :key="`${med.tipo}:${med.nome}:${idx}`" 
                             class="flex items-start gap-2 bg-white p-2 rounded border border-gray-100 shadow-sm">
                          <Checkbox 
                            :id="`qt-${agendamento.id}-${idx}`"
                            :checked="isChecked(agendamento.id, `${med.tipo}:${med.nome}`)"
                            @update:checked="() => toggleCheck(agendamento.id, `${med.tipo}:${med.nome}`, isInfusao(agendamento) ? agendamento.detalhes.infusao.status_farmacia : 'pendente')"
                            class="mt-0.5"
                          />
                          <label :for="`qt-${agendamento.id}-${idx}`" class="text-sm leading-tight cursor-pointer w-full">
                            <span class="font-semibold text-rose-700 block">{{ med.nome }}</span>
                            <span class="text-gray-600 text-xs">{{ med.dose }} {{ med.unidade }}</span>
                          </label>
                        </div>
                      </div>
                   </div>

                   <!-- POS -->
                   <div v-if="getMedicamentos(agendamento)?.pos.length" class="space-y-3">
                      <div class="flex items-center gap-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        <CheckCircle2 class="h-3 w-3"/> Pós-Quimioterapia
                      </div>
                       <div class="space-y-2">
                        <div v-for="(med, idx) in getMedicamentos(agendamento)?.pos" :key="`${med.tipo}:${med.nome}:${idx}`" 
                             class="flex items-start gap-2">
                          <Checkbox 
                            :id="`pos-${agendamento.id}-${idx}`"
                            :checked="isChecked(agendamento.id, `${med.tipo}:${med.nome}`)"
                            @update:checked="() => toggleCheck(agendamento.id, `${med.tipo}:${med.nome}`, isInfusao(agendamento) ? agendamento.detalhes.infusao.status_farmacia : 'pendente')"
                            class="mt-0.5"
                          />
                          <label :for="`pos-${agendamento.id}-${idx}`" class="text-sm leading-tight cursor-pointer">
                            <span class="font-medium text-gray-800">{{ med.nome }}</span>
                            <span class="text-gray-500 ml-1 text-xs">{{ med.dose }} {{ med.unidade }}</span>
                          </label>
                        </div>
                      </div>
                   </div>
                </template>
              </div>
            </TableCell>
          </TableRow>
        </template>
      </TableBody>
    </Table>
  </div>
</template>
