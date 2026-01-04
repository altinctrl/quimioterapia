<script lang="ts" setup>
import {computed} from 'vue'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Alert, AlertDescription} from '@/components/ui/alert'
import {Clock, ListPlus, Pill, Plus, Trash2} from 'lucide-vue-next'
import type {Medicamento} from '@/types'

const props = defineProps<{
  medicamentos: Medicamento[]
  protocoloSelecionado: string
}>()

const emit = defineEmits<{
  (e: 'adicionar'): void
  (e: 'remover', index: number): void
  (e: 'carregarPadrao'): void
}>()

const tempoTotalInfusao = computed(() => {
  return props.medicamentos.reduce((acc, med) => acc + (med.tempoInfusao || 0), 0)
})
</script>

<template>
  <Card class="border-blue-200 bg-blue-50/30">
    <CardHeader>
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <CardTitle class="flex items-center gap-2 text-blue-900">
            <Pill class="h-5 w-5"/>
            4. Quimioterapia (QT)
          </CardTitle>
          <CardDescription>Fármacos principais do protocolo</CardDescription>
        </div>

        <Button
            v-if="medicamentos.length === 0 && protocoloSelecionado"
            class="bg-white border-blue-200 text-blue-700 hover:bg-blue-50 w-full sm:w-auto"
            size="sm"
            variant="outline"
            @click="emit('carregarPadrao')"
        >
          <ListPlus class="h-4 w-4 mr-2"/>
          Carregar Padrão
        </Button>
      </div>
    </CardHeader>
    <CardContent class="space-y-4">
      <div v-for="(med, idx) in medicamentos" :key="med.id"
           class="border border-blue-100 rounded-lg p-4 bg-white relative shadow-sm">
        <Button class="absolute top-2 right-2 text-red-500 hover:text-red-700 hover:bg-red-50" size="sm"
                variant="ghost"
                @click="emit('remover', idx)">
          <Trash2 class="h-4 w-4"/>
        </Button>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="col-span-2"><Label>Medicamento *</Label><Input v-model="med.nome" placeholder="Ex: Paclitaxel"/>
          </div>
          <div><Label>Dose *</Label><Input v-model="med.dose"/></div>
          <div>
            <Label>Unidade</Label>
            <Select v-model="med.unidade">
              <SelectTrigger>
                <SelectValue/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="mg">mg</SelectItem>
                <SelectItem value="g">g</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Via</Label>
            <Select v-model="med.via">
              <SelectTrigger>
                <SelectValue/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="IV">IV</SelectItem>
                <SelectItem value="SC">SC</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div><Label>Tempo (min)</Label><Input v-model="med.tempoInfusao" type="number"/></div>
          <div><Label>Veículo</Label><Input v-model="med.veiculo" placeholder="SF 0.9%"/></div>
          <div><Label>Vol (ml)</Label><Input v-model="med.volumeVeiculo" placeholder="500"/></div>
        </div>
      </div>

      <Button class="w-full border-blue-300 text-blue-700 hover:bg-blue-50" variant="outline"
              @click="emit('adicionar')">
        <Plus class="h-4 w-4 mr-2"/>
        Adicionar QT
      </Button>

      <Alert v-if="medicamentos.length > 0 && tempoTotalInfusao > 0" class="bg-blue-100 border-blue-200">
        <Clock class="h-4 w-4 text-blue-700"/>
        <AlertDescription class="text-blue-800">
          <strong>Tempo total estimado de infusão:</strong> {{ tempoTotalInfusao }} minutos
          ({{ (tempoTotalInfusao / 60).toFixed(1) }}h)
        </AlertDescription>
      </Alert>
    </CardContent>
  </Card>
</template>
