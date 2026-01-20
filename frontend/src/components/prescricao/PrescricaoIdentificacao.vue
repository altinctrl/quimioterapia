<script lang="ts" setup>
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Textarea} from '@/components/ui/textarea'

const props = defineProps<{
  pacienteId: string
  sexo: string
  peso: string
  altura: string
  creatinina: string
  diagnostico: string
}>()

const emit = defineEmits<{
  (e: 'update:pacienteId', value: string): void
  (e: 'update:peso', value: string): void
  (e: 'update:altura', value: string): void
  (e: 'update:creatinina', value: string): void
  (e: 'update:diagnostico', value: string): void
}>()

const route = useRoute()
const appStore = useAppStore()

const localPacienteId = computed({get: () => props.pacienteId, set: (v) => emit('update:pacienteId', v)})
const localPeso = computed({get: () => props.peso, set: (v) => emit('update:peso', v)})
const localAltura = computed({get: () => props.altura, set: (v) => emit('update:altura', v)})
const localCreatinina = computed({get: () => props.creatinina, set: (v) => emit('update:creatinina', v)})
const localDiagnostico = computed({get: () => props.diagnostico, set: (v) => emit('update:diagnostico', v)})

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
  <Card class="p-6">
    <div class="grid grid-cols-2 gap-4">
      <div class="col-span-2">
        <Label>Paciente *</Label>
        <Select v-model="localPacienteId" :disabled="!!route.query.pacienteId" >
          <SelectTrigger class="disabled:opacity-100 disabled:cursor-default [&>svg]:hidden">
            <SelectValue placeholder="Selecione..."/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="p in appStore.pacientes" :key="p.id" :value="p.id">
              {{ p.nome }} - {{ p.registro }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="col-span-2 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div>
          <Label class="whitespace-nowrap">Peso (kg) *</Label>
          <Input v-model="localPeso" class="mt-1.5" placeholder="00.0" step="0.1" type="number"/>
        </div>
        <div>
          <Label class="whitespace-nowrap">Altura (cm) *</Label>
          <Input v-model="localAltura" class="mt-1.5" placeholder="000" type="number"/>
        </div>
        <div>
          <Label class="whitespace-nowrap">Creatinina (mg/dL)</Label>
          <Input v-model="localCreatinina" class="mt-1.5" placeholder="0.00" step="0.01" type="number"/>
        </div>
        <div>
          <Label class="whitespace-nowrap">SC (m²)</Label>
          <Input
              :value="calcularSC"
              class="bg-gray-50 mt-1.5 disabled:opacity-100 disabled:cursor-default"
              disabled/>
        </div>
        <div>
          <Label class="whitespace-nowrap">Sexo</Label>
          <Input
              :value="sexo"
              class="mt-1.5 bg-gray-50 uppercase disabled:opacity-100 disabled:cursor-default"
              disabled
              placeholder="-"
          />
        </div>
      </div>

      <div class="col-span-2">
        <Label>Hipótese Diagnóstica</Label>
        <Textarea v-model="localDiagnostico" rows="2"/>
      </div>
    </div>
  </Card>
</template>
