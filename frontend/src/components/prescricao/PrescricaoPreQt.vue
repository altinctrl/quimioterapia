<script lang="ts" setup>
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {ListPlus, Pill, Plus, Trash2} from 'lucide-vue-next'
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
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <CardTitle class="flex items-center gap-2">
            <Pill class="h-5 w-5 text-gray-600"/>
            3. Pré-Quimioterapia (PRE-QT)
          </CardTitle>
          <CardDescription>Medicações administradas antes (antieméticos, corticoides)</CardDescription>
        </div>
        <Button
            v-if="medicamentos.length === 0 && protocoloSelecionado"
            class="bg-white border-blue-200 text-blue-700 hover:bg-blue-50 w-full sm:w-auto" size="sm"
            variant="outline"
            @click="emit('carregarPadrao')"
        >
          <ListPlus class="h-4 w-4 mr-2"/>
          Carregar Padrão
        </Button>
      </div>
    </CardHeader>
    <CardContent class="space-y-4">
      <div v-for="(med, idx) in medicamentos" :key="med.id" class="border rounded-lg p-4 bg-gray-50 relative">
        <Button class="absolute top-2 right-2 text-red-500 hover:bg-red-50" size="sm" variant="ghost"
                @click="emit('remover', idx)">
          <Trash2 class="h-4 w-4"/>
        </Button>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="col-span-2"><Label>Medicamento</Label><Input v-model="med.nome"/></div>
          <div><Label>Dose</Label><Input v-model="med.dose"/></div>
          <div>
            <Label>Unidade</Label>
            <Select v-model="med.unidade">
              <SelectTrigger>
                <SelectValue/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="mg">mg</SelectItem>
                <SelectItem value="g">g</SelectItem>
                <SelectItem value="mcg">mcg</SelectItem>
                <SelectItem value="UI">UI</SelectItem>
                <SelectItem value="ml">ml</SelectItem>
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
                <SelectItem value="VO">VO</SelectItem>
                <SelectItem value="SC">SC</SelectItem>
                <SelectItem value="IM">IM</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div><Label>Tempo (min)</Label><Input v-model="med.tempoInfusao" type="number"/></div>
          <div><Label>Veículo</Label><Input v-model="med.veiculo" placeholder="Ex: SF 100ml"/></div>
          <div><Label>Volume (ml)</Label><Input v-model="med.volumeVeiculo"/></div>

          <div class="col-span-2 md:col-span-4"><Label>Observações</Label><Input v-model="med.observacoes"/></div>
        </div>
      </div>
      <Button class="w-full" variant="outline" @click="emit('adicionar')">
        <Plus class="h-4 w-4 mr-2"/>
        Adicionar PRE-QT
      </Button>
    </CardContent>
  </Card>
</template>
