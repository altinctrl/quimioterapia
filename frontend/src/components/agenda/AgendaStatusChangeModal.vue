<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Checkbox} from '@/components/ui/checkbox'
import {AlertTriangle, Ban, Syringe} from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  statusDestino: string
  pacienteNome: string
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'confirm', motivoFinal: string): void
}>()

const observacaoLivre = ref('')
const motivoSuspensao = ref('')
const medicamentoFalta = ref('')
const tipoIntercorrencia = ref('')
const medicamentoIntercorrencia = ref('')
const vigihospFeito = ref(false)

const MOTIVOS_SUSPENSAO = [
  {value: 'alteracoes_clinicas', label: 'Alterações clínicas'},
  {value: 'mudanca_protocolo', label: 'Mudança de protocolo'},
  {value: 'medicacao_falta', label: 'Medicação em falta'},
  {value: 'alteracoes_laboratoriais', label: 'Alterações laboratoriais'},
  {value: 'obito', label: 'Óbito'},
  {value: 'sem_processo', label: 'Sem processo para liberação de QTAN'}
]

const MEDICAMENTOS_FALTA = [
  'Paclitaxel', 'Carboplatina', 'Docetaxel', '5FU',
  'Medicações judicializadas', 'Outros'
]

const TIPOS_INTERCORRENCIA = [
  {value: 'hipersensibilidade', label: 'Reação de Hipersensibilidade'},
  {value: 'extravasamento', label: 'Extravasamento'},
  {value: 'derramamento', label: 'Derramamento Acidental de QT'}
]

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    observacaoLivre.value = ''
    motivoSuspensao.value = ''
    medicamentoFalta.value = ''
    tipoIntercorrencia.value = ''
    medicamentoIntercorrencia.value = ''
    vigihospFeito.value = false
  }
})

const isSuspensao = computed(() => props.statusDestino === 'suspenso')
const isIntercorrencia = computed(() => props.statusDestino === 'intercorrencia')

const tituloModal = computed(() => {
  if (isSuspensao.value) return 'Suspender Tratamento'
  if (isIntercorrencia.value) return 'Registrar Intercorrência'
  return 'Alterar Status'
})

const isValid = computed(() => {
  if (isSuspensao.value) {
    if (!motivoSuspensao.value) return false
    if (motivoSuspensao.value === 'medicacao_falta' && !medicamentoFalta.value) return false
  }
  if (isIntercorrencia.value) {
    if (!tipoIntercorrencia.value) return false
    if (!medicamentoIntercorrencia.value) return false
  }
  return true
})

const handleConfirm = () => {
  const payloadDetalhes: any = {}

  if (isSuspensao.value) {
    payloadDetalhes.suspensao = {}
    payloadDetalhes.suspensao.motivo_suspensao = motivoSuspensao.value
    if (motivoSuspensao.value === 'medicacao_falta')
      payloadDetalhes.suspensao.medicamento_falta = medicamentoFalta.value
    if (observacaoLivre.value)
      payloadDetalhes.suspensao.observacoes = observacaoLivre.value
  } else if (isIntercorrencia.value) {
    payloadDetalhes.intercorrencia = {}
    payloadDetalhes.intercorrencia.tipo_intercorrencia = tipoIntercorrencia.value
    payloadDetalhes.intercorrencia.medicamento_intercorrencia = medicamentoIntercorrencia.value
    if (tipoIntercorrencia.value === 'hipersensibilidade')
      payloadDetalhes.intercorrencia.vigihosp = vigihospFeito.value
    if (observacaoLivre.value)
      payloadDetalhes.intercorrencia.observacoes = observacaoLivre.value
  }

  emit('confirm', payloadDetalhes)
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[500px]">
      <DialogHeader>
        <DialogTitle :class="isSuspensao ? 'text-red-600' : 'text-amber-600'"
                     class="flex items-center gap-2">
          <Ban v-if="isSuspensao" class="h-5 w-5"/>
          <AlertTriangle v-else-if="isIntercorrencia" class="h-5 w-5"/>
          {{ tituloModal }}
        </DialogTitle>
        <DialogDescription>
          Registro clínico para o paciente <strong>{{ pacienteNome }}</strong>.
        </DialogDescription>
      </DialogHeader>

      <div class="py-4 space-y-4">

        <div v-if="isSuspensao" class="space-y-4">
          <div class="space-y-2">
            <Label>Motivo da Suspensão <span class="text-red-500">*</span></Label>
            <Select v-model="motivoSuspensao">
              <SelectTrigger>
                <SelectValue placeholder="Selecione o motivo..."/>
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem v-for="m in MOTIVOS_SUSPENSAO" :key="m.value" :value="m.value">
                    {{ m.label }}
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div v-if="motivoSuspensao === 'medicacao_falta'"
               class="space-y-2 bg-red-50 p-3 rounded-md border border-red-100">
            <Label>Qual medicamento está em falta? <span class="text-red-500">*</span></Label>
            <Select v-model="medicamentoFalta">
              <SelectTrigger>
                <SelectValue placeholder="Selecione a droga..."/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="d in MEDICAMENTOS_FALTA" :key="d" :value="d">
                  {{ d }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div v-if="isIntercorrencia" class="space-y-4">
          <div class="space-y-2">
            <Label>Tipo de Intercorrência <span class="text-red-500">*</span></Label>
            <Select v-model="tipoIntercorrencia">
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo..."/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="t in TIPOS_INTERCORRENCIA" :key="t.value" :value="t.value">
                  {{ t.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label>
              {{ tipoIntercorrencia === 'derramamento' ? 'Droga derramada' : 'Droga envolvida' }}
              <span class="text-red-500">*</span>
            </Label>
            <div class="relative">
              <Syringe class="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500"/>
              <input
                  v-model="medicamentoIntercorrencia"
                  class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 pl-9 text-sm shadow-sm
                       transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  placeholder="Nome do quimioterápico..."
              />
            </div>
          </div>

          <div v-if="tipoIntercorrencia === 'hipersensibilidade'"
               class="flex items-center space-x-2 bg-amber-50 p-3 rounded-md border border-amber-100">
            <Checkbox id="vigihosp" :checked="vigihospFeito" @update:checked="vigihospFeito = $event"/>
            <div class="grid gap-1.5 leading-none">
              <Label class="font-medium cursor-pointer" for="vigihosp">
                Notificação VIGIHOSP realizada?
              </Label>
              <p class="text-[0.8rem] text-muted-foreground">
                Obrigatório para reações adversas graves.
              </p>
            </div>
          </div>
        </div>

        <div class="space-y-2">
          <Label>Observações Adicionais</Label>
          <Textarea
              v-model="observacaoLivre"
              class="min-h-[80px]"
              placeholder="Detalhes clínicos adicionais..."
          />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancelar</Button>
        <Button
            :disabled="!isValid"
            :variant="isSuspensao ? 'destructive' : 'default'"
            @click="handleConfirm"
        >
          Confirmar Registro
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>