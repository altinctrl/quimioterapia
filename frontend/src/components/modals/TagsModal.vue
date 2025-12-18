<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {Checkbox} from '@/components/ui/checkbox'
import {Label} from '@/components/ui/label'
import {Tag} from 'lucide-vue-next'
import {useAppStore} from '@/stores/app'

const props = defineProps<{
  open: boolean
  agendamentoId: string
  tagsAtuais: string[]
}>()

const emit = defineEmits(['update:open', 'salvar'])
const appStore = useAppStore()

const tagsSelecionadas = ref<string[]>([])
const tagsDisponiveis = computed(() => appStore.parametros.tags || [])

watch(() => props.open, (val) => {
  if (val) tagsSelecionadas.value = [...props.tagsAtuais]
})

const toggleTag = (tag: string, checked: boolean) => {
  if (checked) {
    if (!tagsSelecionadas.value.includes(tag)) {
      tagsSelecionadas.value.push(tag)
    }
  } else {
    tagsSelecionadas.value = tagsSelecionadas.value.filter(t => t !== tag)
  }
}

const handleSalvar = () => {
  emit('salvar', props.agendamentoId, tagsSelecionadas.value)
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-xl">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Tag class="h-5 w-5"/>
          Selecionar Tags
        </DialogTitle>
        <DialogDescription>Tags aplicáveis para este agendamento</DialogDescription>
      </DialogHeader>

      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-2 max-h-[600px] overflow-y-auto pr-2">
          <div
            v-for="tag in tagsDisponiveis"
            :key="tag"
            class="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer group"
            @click="toggleTag(tag, !tagsSelecionadas.includes(tag))"
          >
            <Checkbox
              :id="`tag-${tag}`"
              :checked="tagsSelecionadas.includes(tag)"
              @update:checked="(val) => toggleTag(tag, val as boolean)"
              @click.stop />
            <Label
              :for="`tag-${tag}`"
              class="flex-1 cursor-pointer font-medium text-sm"
              @click.stop
            >
              {{ tag }}
            </Label>
          </div>
        </div>

        <div class="flex gap-2 pt-4 pr-2">
          <Button class="flex-1" variant="outline" @click="emit('update:open', false)">Cancelar</Button>
          <Button class="flex-1" @click="handleSalvar">Salvar</Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
