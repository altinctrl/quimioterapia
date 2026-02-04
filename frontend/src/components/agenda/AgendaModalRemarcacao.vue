<script lang="ts" setup>
import {ref, watch} from 'vue'
import {useAppStore} from '@/stores/storeGeral.ts'
import {toast} from 'vue-sonner'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Agendamento} from "@/types/typesAgendamento.ts";

const props = defineProps<{
  open: boolean
  agendamento: Agendamento | null
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'remarcado'): void
}>()

const appStore = useAppStore()
const loading = ref(false)

const form = ref({
  novaData: '',
  novoHorario: '',
  motivo: ''
})

watch(() => props.open, (isOpen) => {
  if (isOpen && props.agendamento) {
    form.value = {
      novaData: '',
      novoHorario: props.agendamento.horarioInicio || '',
      motivo: ''
    }
  }
})

const getPacienteNome = () => {
  if (!props.agendamento) return ''
  const p = appStore.getPacienteById(props.agendamento.pacienteId)
  return p?.nome || 'Desconhecido'
}

const formatarDataOrigem = () => {
  if (!props.agendamento?.data) return ''
  return props.agendamento.data.split('-').reverse().join('/')
}

const handleConfirmar = async () => {
  if (!props.agendamento?.id) return
  if (!form.value.novaData || !form.value.novoHorario || !form.value.motivo) {
    toast.error("Preencha data, horário e motivo.")
    return
  }
  try {
    loading.value = true
    await appStore.remarcarAgendamento(
        props.agendamento.id,
        form.value.novaData,
        form.value.novoHorario,
        form.value.motivo
    )
    emit('remarcado')
    emit('update:open', false)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Remarcar Agendamento</DialogTitle>
        <DialogDescription>
          O agendamento original será mantido como histórico.
        </DialogDescription>
      </DialogHeader>

      <div v-if="agendamento" class="bg-blue-50 p-3 rounded-md border border-blue-100 mb-2 text-sm">
        <p class="font-bold text-blue-900">{{ getPacienteNome() }}</p>
        <div class="flex gap-4 text-blue-700 mt-1">
          <span>De: <strong>{{ formatarDataOrigem() }}</strong></span>
          <span>às <strong>{{ agendamento.horarioInicio }}</strong></span>
        </div>
      </div>

      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label>Nova Data</Label>
            <Input v-model="form.novaData" type="date"/>
          </div>
          <div class="space-y-2">
            <Label>Novo Horário</Label>
            <Input v-model="form.novoHorario" type="time"/>
          </div>
        </div>

        <div class="space-y-2">
          <Label>Motivo</Label>
          <Textarea
              v-model="form.motivo"
              placeholder="Ex: Paciente gripado, solicitou adiamento..."
          />
        </div>
      </div>

      <div class="flex justify-end gap-2">
        <Button variant="outline" :disabled="loading" @click="$emit('update:open', false)">
          Cancelar
        </Button>
        <Button :disabled="loading" @click="handleConfirmar">
          <span v-if="loading">Processando...</span>
          <span v-else>Remarcar</span>
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>