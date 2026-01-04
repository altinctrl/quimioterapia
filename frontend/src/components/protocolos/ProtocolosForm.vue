<script lang="ts" setup>
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Checkbox} from '@/components/ui/checkbox'
import {Separator} from '@/components/ui/separator'
import {Plus, Trash2} from 'lucide-vue-next'
import type {ItemProtocolo} from '@/types'

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
}>()

const diasSemanaOptions = [
  {value: 1, label: 'Segunda'},
  {value: 2, label: 'Terça'},
  {value: 3, label: 'Quarta'},
  {value: 4, label: 'Quinta'},
  {value: 5, label: 'Sexta'}
]

const unidadesOptions = ['mg/m²', 'mg/kg', 'mg', 'g', 'mcg', 'UI', 'AUC', 'ml']

const addItem = (lista: 'pre' | 'qt' | 'pos') => {
  const novoItem: ItemProtocolo = {nome: '', dosePadrao: '', unidadePadrao: 'mg/m²', viaPadrao: 'IV'}
  if (lista === 'pre') props.modelValue.preMedicacoes.push(novoItem)
  else if (lista === 'qt') props.modelValue.medicamentos.push(novoItem)
  else props.modelValue.posMedicacoes.push(novoItem)
}

const removeItem = (lista: 'pre' | 'qt' | 'pos', index: number) => {
  if (lista === 'pre') props.modelValue.preMedicacoes.splice(index, 1)
  else if (lista === 'qt') props.modelValue.medicamentos.splice(index, 1)
  else props.modelValue.posMedicacoes.splice(index, 1)
}

const toggleDia = (dia: number, isChecked: boolean) => {
  let current = props.modelValue.diasSemanaPermitidos || []

  if (isChecked) {
    if (!current.includes(dia)) {
      current.push(dia)
    }
  } else {
    current = current.filter((d: number) => d !== dia)
  }

  props.modelValue.diasSemanaPermitidos = current.sort((a: number, b: number) => a - b)
}
</script>

<template>
  <div class="space-y-6 py-4">
    <div class="grid grid-cols-2 gap-4">
      <div class="col-span-2">
        <Label>Nome</Label>
        <Input v-model="modelValue.nome" placeholder="Ex: FOLFOX"/>
      </div>

      <div class="col-span-2">
        <Label>Descrição</Label>
        <Input v-model="modelValue.descricao"/>
      </div>

      <div>
        <Label>Indicação</Label>
        <Input v-model="modelValue.indicacao" placeholder="Ex: CA Colorretal"/>
      </div>

      <div>
        <Label>Duração (min)</Label>
        <Input v-model="modelValue.duracao" type="number"/>
        <p class="text-[10px] text-gray-500 mt-1">
          Grupo inferido:
          <span v-if="modelValue.duracao < 120" class="text-green-600 font-medium">Rápido</span>
          <span v-else-if="modelValue.duracao <= 240" class="text-blue-600 font-medium">Médio</span>
          <span v-else class="text-purple-600 font-medium">Longo</span>
        </p>
      </div>

      <div>
        <Label>Frequência</Label>
        <Input v-model="modelValue.frequencia" placeholder="Ex: 14 dias"/>
      </div>

      <div>
        <Label>Número de Ciclos</Label>
        <Input v-model="modelValue.numeroCiclos" type="number"/>
      </div>

      <div class="col-span-2">
        <Label class="mb-2 block">Dias da Semana Permitidos</Label>
        <div class="col-span-2 border rounded-lg p-3 bg-gray-50">
          <div class="flex flex-wrap gap-4">
            <div v-for="dia in diasSemanaOptions" :key="dia.value" class="flex items-center space-x-2">
              <Checkbox
                  :id="`dia-${dia.value}`"
                  :checked="modelValue.diasSemanaPermitidos?.includes(dia.value)"
                  @update:checked="(val) => toggleDia(dia.value, val)"
              />
              <Label :for="`dia-${dia.value}`" class="cursor-pointer">{{ dia.label }}</Label>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-2">Deixe vazio para permitir todos os dias.</p>
        </div>
      </div>
    </div>

    <Separator/>

    <div class="space-y-6">

      <div>
        <div class="flex items-center justify-between mb-2">
          <Label>Pré-Medicação</Label>
          <Button size="sm" variant="outline" @click="addItem('pre')">
            <Plus class="h-3 w-3 mr-1"/>
            Adicionar
          </Button>
        </div>
        <div v-if="modelValue.preMedicacoes.length === 0"
             class="text-sm text-gray-400 italic bg-gray-50 p-2 rounded text-center border border-blue-100">
          Nenhum item
        </div>
        <div v-else class="space-y-2 bg-blue-50/50 p-4 rounded-lg border border-blue-100">
          <div v-for="(item, idx) in modelValue.preMedicacoes" :key="idx" class="flex gap-2 items-center">
            <Input v-model="item.nome" class="flex-grow" placeholder="Nome"/>
            <Input v-model="item.dosePadrao" class="w-20 bg-white" placeholder="Dose"/>

            <div class="w-24">
              <Select v-model="item.unidadePadrao">
                <SelectTrigger class="bg-white">
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="u in unidadesOptions" :key="u" :value="u">{{ u }}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Select v-model="item.viaPadrao">
              <SelectTrigger class="w-24">
                <SelectValue placeholder="Via"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="IV">IV</SelectItem>
                <SelectItem value="VO">VO</SelectItem>
                <SelectItem value="SC">SC</SelectItem>
              </SelectContent>
            </Select>
            <Button class="text-red-500" size="icon" variant="ghost" @click="removeItem('pre', idx)">
              <Trash2 class="h-4 w-4"/>
            </Button>
          </div>
        </div>
      </div>

      <div>
        <div class="flex items-center justify-between mb-2">
          <Label>Quimioterapia</Label>
          <Button size="sm" variant="outline" @click="addItem('qt')">
            <Plus class="h-3 w-3 mr-1"/>
            Adicionar
          </Button>
        </div>
        <div v-if="modelValue.medicamentos.length === 0"
             class="text-sm text-gray-400 italic bg-gray-50 p-2 rounded text-center border border-blue-100">
          Nenhum item
        </div>
        <div v-else class="space-y-2 bg-blue-50/50 p-4 rounded-lg border border-blue-100">
          <div v-for="(item, idx) in modelValue.medicamentos" :key="idx" class="flex gap-2 items-center">
            <Input v-model="item.nome" class="flex-grow bg-white" placeholder="Nome do Medicamento"/>
            <Input v-model="item.dosePadrao" class="w-20 bg-white" placeholder="Dose"/>

            <div class="w-24">
              <Select v-model="item.unidadePadrao">
                <SelectTrigger class="bg-white">
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="u in unidadesOptions" :key="u" :value="u">{{ u }}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Select v-model="item.viaPadrao">
              <SelectTrigger class="w-24 bg-white">
                <SelectValue/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="IV">IV</SelectItem>
                <SelectItem value="SC">SC</SelectItem>
              </SelectContent>
            </Select>
            <Button class="text-red-500" size="icon" variant="ghost" @click="removeItem('qt', idx)">
              <Trash2 class="h-4 w-4"/>
            </Button>
          </div>
        </div>
      </div>

      <div>
        <div class="flex items-center justify-between mb-2">
          <Label>Pós-Medicação</Label>
          <Button size="sm" variant="outline" @click="addItem('pos')">
            <Plus class="h-3 w-3 mr-1"/>
            Adicionar
          </Button>
        </div>
        <div v-if="modelValue.posMedicacoes.length === 0"
             class="text-sm text-gray-400 italic bg-gray-50 p-2 rounded text-center border border-blue-100">
          Nenhum item
        </div>
        <div v-else class="space-y-2 bg-blue-50/50 p-4 rounded-lg border border-blue-100">
          <div v-for="(item, idx) in modelValue.posMedicacoes" :key="idx" class="flex gap-2 items-center">
            <Input v-model="item.nome" class="flex-grow" placeholder="Nome"/>
            <Input v-model="item.dosePadrao" class="w-20 bg-white" placeholder="Dose"/>

            <div class="w-24">
              <Select v-model="item.unidadePadrao">
                <SelectTrigger class="bg-white">
                  <SelectValue/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="u in unidadesOptions" :key="u" :value="u">{{ u }}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Select v-model="item.viaPadrao">
              <SelectTrigger class="w-24">
                <SelectValue/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="IV">IV</SelectItem>
                <SelectItem value="SC">SC</SelectItem>
                <SelectItem value="VO">VO</SelectItem>
              </SelectContent>
            </Select>
            <Button class="text-red-500" size="icon" variant="ghost" @click="removeItem('pos', idx)">
              <Trash2 class="h-4 w-4"/>
            </Button>
          </div>
        </div>
      </div>

    </div>

    <Separator class="my-4"/>

    <div class="grid grid-cols-1 gap-4">
      <div>
        <Label>Observações</Label>
        <Textarea v-model="modelValue.observacoes" rows="2"/>
      </div>
      <div>
        <Label>Precauções</Label>
        <Textarea v-model="modelValue.precaucoes" rows="2"/>
      </div>
      <div class="flex items-center space-x-2">
        <Checkbox id="ativo" :checked="modelValue.ativo" @update:checked="modelValue.ativo = $event"/>
        <Label for="ativo">Protocolo Ativo</Label>
      </div>
    </div>
  </div>
</template>