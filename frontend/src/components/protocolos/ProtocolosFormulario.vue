<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Checkbox} from '@/components/ui/checkbox'
import {Card, CardContent} from '@/components/ui/card'
import {ClipboardList, Copy, Info, Layers, Plus, Trash2} from 'lucide-vue-next'
import {diasSemanaOptions} from '@/constants/constProtocolos.ts'
import ProtocolosBlocoMedicamentos from './ProtocolosBlocoMedicamentos.vue'
import {CategoriaBlocoEnum, FaseEnum} from "@/types/typesProtocolo.ts";

const props = defineProps<{
  modelValue: any
}>()

const activeTemplateIndex = ref(0)
const tabsContainerRef = ref<HTMLElement | null>(null)

watch(() => props.modelValue.templatesCiclo.length, (newLen) => {
  if (activeTemplateIndex.value >= newLen) {
    activeTemplateIndex.value = Math.max(0, newLen - 1)
  }
})

watch(() => props.modelValue, (newVal) => {
  if (newVal && (!newVal.diasSemanaPermitidos || newVal.diasSemanaPermitidos.length === 0)) {
    newVal.diasSemanaPermitidos = [1, 2, 3, 4, 5]
  }
}, { immediate: true })

const currentTemplate = computed(() => {
  if (!props.modelValue.templatesCiclo || props.modelValue.templatesCiclo.length === 0) {
    props.modelValue.templatesCiclo = [{
      idTemplate: 'Padrão',
      aplicavelAosCiclos: '',
      blocos: []
    }]
  }
  return props.modelValue.templatesCiclo[activeTemplateIndex.value]
})

const getUniqueName = (baseName: string, isCopy = false, excludeIndex = -1) => {
  const existingNames = props.modelValue.templatesCiclo
      .filter((_: any, idx: number) => idx !== excludeIndex)
      .map((t: any) => t.idTemplate)

  let candidate = baseName
  if (isCopy && existingNames.includes(candidate)) {
    candidate = `${baseName} (Cópia)`
  }

  let counter = 1
  const baseForCounter = isCopy ? `${baseName} (Cópia` : baseName.replace(/\s\d+$/, '')

  while (existingNames.includes(candidate)) {
    if (isCopy) {
      counter++
      candidate = `${baseName} (Cópia ${counter})`
    } else {
      candidate = `${baseForCounter} ${counter}`
      counter++
    }
  }
  return candidate
}

const handleNameBlur = () => {
  if (!currentTemplate.value) return
  const currentName = currentTemplate.value.idTemplate || 'Sem Nome'
  const uniqueName = getUniqueName(currentName, false, activeTemplateIndex.value)
  if (uniqueName !== currentName) {
    currentTemplate.value.idTemplate = uniqueName
  }
}

const addTemplate = () => {
  const newName = getUniqueName('Variante', false)

  props.modelValue.templatesCiclo.push({
    idTemplate: newName,
    aplicavelAosCiclos: '',
    blocos: []
  })

  activeTemplateIndex.value = props.modelValue.templatesCiclo.length - 1
}

const duplicateTemplate = () => {
  const original = currentTemplate.value
  const newName = getUniqueName(original.idTemplate, true)

  const clone = JSON.parse(JSON.stringify(original))
  clone.idTemplate = newName

  props.modelValue.templatesCiclo.push(clone)

  activeTemplateIndex.value = props.modelValue.templatesCiclo.length - 1
}

const removeTemplate = () => {
  if (props.modelValue.templatesCiclo.length <= 1) return
  props.modelValue.templatesCiclo.splice(activeTemplateIndex.value, 1)
}

const handleFaseChange = (value: string) => {
  if (value === 'none') {
    props.modelValue.fase = null
  } else {
    props.modelValue.fase = value
  }
}

const createEmptyBloco = (ordem: number) => ({
  ordem,
  categoria: CategoriaBlocoEnum.QT,
  itens: []
})

const addBloco = () => {
  const template = currentTemplate.value
  const novaOrdem = (template.blocos.length || 0) + 1
  template.blocos.push(createEmptyBloco(novaOrdem))
}

const removeBloco = (index: number) => {
  currentTemplate.value.blocos.splice(index, 1)
  reorderBlocos()
}

const moveBloco = (index: number, direction: 'up' | 'down') => {
  const blocos = currentTemplate.value.blocos
  if (direction === 'up' && index > 0) {
    [blocos[index], blocos[index - 1]] = [blocos[index - 1], blocos[index]]
  } else if (direction === 'down' && index < blocos.length - 1) {
    [blocos[index], blocos[index + 1]] = [blocos[index + 1], blocos[index]]
  }
  reorderBlocos()
}

const reorderBlocos = () => {
  currentTemplate.value.blocos.forEach((b: any, idx: number) => {
    b.ordem = idx + 1
  })
}

const toggleDia = (dia: number, isChecked: boolean) => {
  let current = props.modelValue.diasSemanaPermitidos || []
  if (isChecked) {
    if (!current.includes(dia)) current.push(dia)
  } else {
    current = current.filter((d: number) => d !== dia)
  }
  props.modelValue.diasSemanaPermitidos = current.sort((a: number, b: number) => a - b)
}
</script>

<template>
  <div class="space-y-6">

    <div class=" space-y-4 ">
      <div class="flex items-center gap-2">
        <ClipboardList/>
        <h2 class="text-xl font-semibold text-gray-800">Dados Gerais</h2>
      </div>
      <Card>
        <CardContent class="p-6 space-y-6">
          <div class="grid grid-cols-12 gap-4">
            <div class="col-span-12">
              <Label>Nome do Protocolo</Label>
              <Input v-model="modelValue.nome"/>
            </div>

            <div class="col-span-12 md:col-span-12">
              <Label>Indicação</Label>
              <Input v-model="modelValue.indicacao"/>
            </div>

            <div class="col-span-2">
              <Label>Duração do Ciclo</Label>
              <Input v-model="modelValue.duracaoCicloDias" type="number"/>
            </div>
            <div class="col-span-2">
              <Label>Total de Ciclos</Label>
              <Input v-model="modelValue.totalCiclos" placeholder="Indefinido = 0" type="number"/>
            </div>
            <div class="col-span-3">
              <Label>Tempo de Administração</Label>
              <Input v-model="modelValue.tempoTotalMinutos" type="number"/>
            </div>

            <div class="col-span-3">
              <Label>Fase do Tratamento</Label>
              <Select
                  :model-value="modelValue.fase || 'none'"
                  @update:model-value="handleFaseChange"
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione"/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Selecione</SelectItem>
                  <SelectItem v-for="f in FaseEnum" :key="f" :value="f">{{ f }}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="col-span-2">
              <Label>Linha</Label>
              <Input v-model="modelValue.linha" type="number"/>
            </div>

            <div class="col-span-12">
              <Label>Observações</Label>
              <Textarea v-model="modelValue.observacoes" rows="2"/>
            </div>
            <div class="col-span-12">
              <Label>Precauções</Label>
              <Textarea v-model="modelValue.precaucoes" class="border-red-100 bg-red-50/20" rows="2"/>
            </div>

            <div class="col-span-12 border rounded-lg p-3 bg-gray-50">
              <Label class="mb-2 block">Dias da Semana Permitidos</Label>
              <div class="flex flex-wrap gap-4">
                <div v-for="dia in diasSemanaOptions" :key="dia.value" class="flex items-center space-x-2">
                  <Checkbox
                      :id="`dia-${dia.value}`"
                      :checked="modelValue.diasSemanaPermitidos?.includes(dia.value)"
                      @update:checked="(val) => toggleDia(dia.value, val as boolean)"
                  />
                  <Label :for="`dia-${dia.value}`" class="cursor-pointer">{{ dia.label }}</Label>
                </div>
              </div>
            </div>

            <div class="col-span-12 flex items-center justify-end space-x-2 border border-transparent rounded-lg">
              <Label for="ativo">Protocolo Ativo</Label>
              <Checkbox id="ativo" :checked="modelValue.ativo" @update:checked="modelValue.ativo = $event"/>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <div class="pt-6 space-y-4">
      <div class="flex items-center gap-2">
        <Layers/>
        <h2 class="text-xl font-semibold text-gray-800">Templates</h2>
      </div>

      <Card class="p-4 flex items-center gap-1 mb-4 w-full">

        <div
            ref="tabsContainerRef"
            class="flex items-center gap-2 overflow-x-auto flex-1 px-1 w-0"
            style="scrollbar-width: thin; -ms-overflow-style: -ms-autohiding-scrollbar;"
        >
          <Button
              v-for="(template, idx) in modelValue.templatesCiclo"
              :key="idx"
              :variant="activeTemplateIndex === idx ? 'default' : 'outline'"
              class="h-8 text-sm whitespace-nowrap flex-shrink-0"
              @click="activeTemplateIndex = idx"
          >
            {{ template.idTemplate || `Template ${idx + 1}` }}
          </Button>
        </div>

        <div class="w-px h-5 bg-gray-300 mx-1 shrink-0"></div>

        <Button
            class="h-8 w-8 shrink-0 hover:bg-gray-200 text-blue-600"
            size="icon"
            title="Novo Template"
            variant="ghost"
            @click="addTemplate"
        >
          <Plus class="h-4 w-4"/>
        </Button>
      </Card>

      <Card class="p-6">
        <div class=" bg-white space-y-4 relative">
          <div class="flex justify-between items-start gap-4 pb-4 border-b">
            <div class="grid grid-cols-12 gap-4 flex-1">
              <div class="col-span-12 md:col-span-8">
                <Label class="text-xs uppercase text-gray-500 font-bold">Nome do Template / Variante</Label>
                <Input
                    v-model="currentTemplate.idTemplate"
                    placeholder="Ex: Padrão, D1 e D8, etc"
                    @blur="handleNameBlur"
                />
              </div>
              <div class="col-span-12 md:col-span-4">
                <Label class="text-xs uppercase text-gray-500 font-bold">Aplicável aos Ciclos</Label>
                <Input v-model="currentTemplate.aplicavelAosCiclos" placeholder="Ex: 1, 3, 5 ou vazio (todos)"/>
              </div>
            </div>

            <div class="flex flex-col gap-2">
              <Label class="text-xs">&nbsp;</Label>
              <div class="flex gap-2">
                <Button size="icon" title="Duplicar Template" variant="outline" @click="duplicateTemplate">
                  <Copy class="h-4 w-4 text-blue-600"/>
                </Button>
                <Button
                    :disabled="modelValue.templatesCiclo.length <= 1"
                    class="hover:bg-red-50 hover:text-red-600 border-red-100"
                    size="icon"
                    title="Remover Template"
                    variant="outline"
                    @click="removeTemplate"
                >
                  <Trash2 class="h-4 w-4"/>
                </Button>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-1 mt-2">
            <h3 class="text-lg font-medium">Blocos de Medicação</h3>
            <p class="text-sm text-gray-500 flex items-center gap-1">
              <Info class="h-4 w-4"/>
              A ordem numérica define a sequência. Itens dentro do mesmo bloco são simultâneos (Via Y).
            </p>
          </div>

          <div class="space-y-4 pt-2">
            <div v-if="currentTemplate.blocos.length === 0"
                 class="text-center py-8 text-gray-400 border-2 border-dashed rounded-lg bg-gray-50/50">
              Nenhum bloco de medicação configurado para este template.
            </div>

            <ProtocolosBlocoMedicamentos
                v-for="(bloco, bIndex) in currentTemplate.blocos"
                :key="bIndex"
                :bloco="bloco"
                :index="bIndex"
                :isFirst="bIndex === 0"
                :isLast="bIndex === currentTemplate.blocos.length - 1"
                @remove="removeBloco(bIndex)"
                @move-up="moveBloco(bIndex, 'up')"
                @move-down="moveBloco(bIndex, 'down')"
            />
          </div>

          <div class="flex justify-center pt-2">
            <Button class="w-full border-dashed py-6" variant="outline" @click="addBloco">
              <Plus class="h-5 w-5 mr-2"/>
              Adicionar Novo Bloco ao Template "{{ currentTemplate.idTemplate }}"
            </Button>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
