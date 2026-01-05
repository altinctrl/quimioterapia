<script lang="ts" setup>
import {ref, watch} from 'vue'
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Checkbox} from '@/components/ui/checkbox'
import {Label} from '@/components/ui/label'
import {Tag} from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  agendamentoId: string
  tagsAtuais: string[]
}>()

const emit = defineEmits(['update:open', 'salvar'])

const tagsSelecionadas = ref<string[]>([])
const TAGS_DISPONIVEIS = [
  'Primeira Sessão', 'Última Sessão', 'Pré-medicação', 'Hidratação',
  'Antiemético', 'Paciente Idoso', 'Atenção Especial', 'Jejum Necessário'
]

watch(() => props.open, (val) => {
  if (val) tagsSelecionadas.value = [...props.tagsAtuais]
})

const toggleTag = (tag: string) => {
  if (tagsSelecionadas.value.includes(tag)) {
    tagsSelecionadas.value = tagsSelecionadas.value.filter(t => t !== tag)
  } else {
    tagsSelecionadas.value.push(tag)
  }
}

const handleSalvar = () => {
  emit('salvar', props.agendamentoId, tagsSelecionadas.value)
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-md">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Tag class="h-5 w-5"/>
          Selecionar Tags
        </DialogTitle>
        <DialogDescription>Tags aplicáveis para este agendamento</DialogDescription>
      </DialogHeader>

      <div class="space-y-4">
        <div class="space-y-3 max-h-[300px] overflow-y-auto">
          <div v-for="tag in TAGS_DISPONIVEIS" :key="tag" class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded">
            <Checkbox :id="`tag-${tag}`" :checked="tagsSelecionadas.includes(tag)" @update:checked="toggleTag(tag)"/>
            <Label :for="`tag-${tag}`" class="flex-1 cursor-pointer">{{ tag }}</Label>
          </div>
        </div>

        <div class="flex gap-3 pt-4">
          <Button class="flex-1" variant="outline" @click="emit('update:open', false)">Cancelar</Button>
          <Button class="flex-1" @click="handleSalvar">Salvar</Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
