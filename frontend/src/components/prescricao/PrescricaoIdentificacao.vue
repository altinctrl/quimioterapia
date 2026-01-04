<script lang="ts" setup>
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Textarea} from '@/components/ui/textarea'
import {User} from 'lucide-vue-next'

const props = defineProps<{
  pacienteId: string
  peso: string
  altura: string
  diagnostico: string
}>()

const emit = defineEmits<{
  (e: 'update:pacienteId', value: string): void
  (e: 'update:peso', value: string): void
  (e: 'update:altura', value: string): void
  (e: 'update:diagnostico', value: string): void
}>()

const route = useRoute()
const appStore = useAppStore()

const localPacienteId = computed({
  get: () => props.pacienteId,
  set: (val) => emit('update:pacienteId', val)
})

const localPeso = computed({
  get: () => props.peso,
  set: (val) => emit('update:peso', val)
})

const localAltura = computed({
  get: () => props.altura,
  set: (val) => emit('update:altura', val)
})

const localDiagnostico = computed({
  get: () => props.diagnostico,
  set: (val) => emit('update:diagnostico', val)
})

const calcularSC = computed(() => {
  if (props.peso && props.altura) {
    const p = parseFloat(props.peso)
    const a = parseFloat(props.altura)
    return (0.007184 * Math.pow(a, 0.725) * Math.pow(p, 0.425)).toFixed(2)
  }
  return ''
})
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <User class="h-5 w-5"/>
        1. Identificação
      </CardTitle>
    </CardHeader>
    <CardContent class="grid grid-cols-2 gap-4">
      <div class="col-span-2">
        <Label>Paciente *</Label>
        <Select v-model="localPacienteId" :disabled="!!route.query.pacienteId">
          <SelectTrigger>
            <SelectValue placeholder="Selecione..."/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="p in appStore.pacientes" :key="p.id" :value="p.id">
              {{ p.nome }} - {{ p.registro }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <Label class="whitespace-nowrap">Peso (kg)</Label>
          <Input v-model="localPeso" class="min-w-[100px] mt-1.5" placeholder="00.0" type="number"/>
        </div>
        <div>
          <Label class="whitespace-nowrap">Altura (cm)</Label>
          <Input v-model="localAltura" class="min-w-[100px] mt-1.5" placeholder="000" type="number"/>
        </div>
        <div>
          <Label class="whitespace-nowrap">SC (m²)</Label>
          <Input :value="calcularSC" class="bg-gray-100 font-medium text-gray-700 min-w-[100px] mt-1.5" disabled/>
        </div>
      </div>

      <div class="col-span-2">
        <Label>Diagnóstico</Label>
        <Textarea v-model="localDiagnostico" rows="2"/>
      </div>
    </CardContent>
  </Card>
</template>
