<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRoute} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Textarea} from '@/components/ui/textarea'

const props = defineProps<{
  pacienteId?: string | null
  peso?: number | string | null
  altura?: number | string | null
  creatinina?: number | string | null
  diagnostico?: string | null
  sc?: number | null
  sexo?: string
  errors?: Record<string, string | undefined>
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

const createSmartInput = (propName: 'peso' | 'altura' | 'creatinina', emitName: string) => {
  const localValue = ref(props[propName]?.toString() || '')
  watch(() => props[propName], (newVal) => {
    const numProp = Number(newVal)
    const numLocal = Number(localValue.value.replace(',', '.'))
    if (Math.abs(numProp - numLocal) > 0.001) {
      localValue.value = newVal?.toString() || ''
    }
  })
  return computed({
    get: () => localValue.value,
    set: (val) => {
      localValue.value = val
      emit(emitName as any, val)
    }
  })
}

const localPeso = createSmartInput('peso', 'update:peso')
const localAltura = createSmartInput('altura', 'update:altura')
const localCreatinina = createSmartInput('creatinina', 'update:creatinina')

const localPacienteId = computed({
  get: () => props.pacienteId || '',
  set: (v) => emit('update:pacienteId', v)
})
const localDiagnostico = computed({
  get: () => props.diagnostico || '',
  set: (v) => emit('update:diagnostico', v)
})
</script>

<template>
  <Card class="p-6">
    <div class="grid grid-cols-2 gap-4">
      <div class="col-span-2">
        <Label :class="{'text-red-500': errors?.pacienteId}">Paciente *</Label>
        <Select v-model="localPacienteId" :disabled="!!route.query.pacienteId">
          <SelectTrigger
              :class="{'border-red-500': errors?.pacienteId}"
              class="disabled:opacity-100 disabled:cursor-default [&>svg]:hidden"
          >
            <SelectValue placeholder="Selecione..."/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="p in appStore.pacientes" :key="p.id" :value="p.id">
              {{ p.nome }} - {{ p.registro }}
            </SelectItem>
          </SelectContent>
        </Select>
        <span v-if="errors?.pacienteId" class="text-xs text-red-500">{{ errors.pacienteId }}</span>
      </div>

      <div class="col-span-2 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div>
          <Label :class="{'text-red-500': errors?.peso}" class="whitespace-nowrap">Peso (kg) *</Label>
          <Input
              v-model="localPeso"
              :class="{'border-red-500': errors?.peso}"
              class="mt-1.5"
              inputmode="decimal"
              placeholder="00,0"
              type="text"
          />
          <span v-if="errors?.peso" class="text-xs text-red-500">{{ errors.peso }}</span>
        </div>
        <div>
          <Label :class="{'text-red-500': errors?.altura}" class="whitespace-nowrap">Altura (cm) *</Label>
          <Input
              v-model="localAltura"
              :class="{'border-red-500': errors?.altura}"
              class="mt-1.5"
              inputmode="decimal"
              placeholder="000"
              type="text"
          />
          <span v-if="errors?.altura" class="text-xs text-red-500">{{ errors.altura }}</span>
        </div>
        <div>
          <Label :class="{'text-red-500': errors?.creatinina}" class="whitespace-nowrap">Creatinina</Label>
          <Input
              v-model="localCreatinina"
              :class="{'border-red-500': errors?.creatinina}"
              class="mt-1.5"
              inputmode="decimal"
              placeholder="0,00"
              type="text"
          />
          <span v-if="errors?.creatinina" class="text-xs text-red-500">{{ errors.creatinina }}</span>
        </div>
        <div>
          <Label :class="{'text-red-500': errors?.sc}" class="whitespace-nowrap">SC (m²)</Label>
          <Input
              :class="{'border-red-500': errors?.sc}"
              :value="sc ? sc.toFixed(2) : ''"
              class="bg-gray-50 mt-1.5 disabled:opacity-100 disabled:cursor-default"
              disabled
              placeholder="-"
          />
          <span v-if="errors?.sc" class="text-xs text-red-500">{{ errors.sc }}</span>
        </div>
        <div>
          <Label :class="{'text-red-500': errors?.sexo}" class="whitespace-nowrap">Sexo</Label>
          <Input
              :class="{'border-red-500': errors?.sexo}"
              :value="sexo"
              class="mt-1.5 bg-gray-50 uppercase disabled:opacity-100 disabled:cursor-default"
              disabled
              placeholder="-"
          />
          <span v-if="errors?.sexo" class="text-xs text-red-500">{{ errors.sexo }}</span>
        </div>
      </div>

      <div class="col-span-2">
        <Label :class="{'text-red-500': errors?.diagnostico}">Hipótese Diagnóstica</Label>
        <Textarea v-model="localDiagnostico" :class="{'border-red-500': errors?.diagnostico}" rows="2"/>
        <span v-if="errors?.diagnostico" class="text-xs text-red-500">{{ errors.diagnostico }}</span>
      </div>
    </div>
  </Card>
</template>
