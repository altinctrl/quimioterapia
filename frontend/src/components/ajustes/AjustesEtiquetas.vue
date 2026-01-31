<script lang="ts" setup>
import {ref} from 'vue'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Badge} from '@/components/ui/badge'
import {Plus, Tag, X} from 'lucide-vue-next'

defineProps<{
  tags: string[]
}>()

const emit = defineEmits<{
  (e: 'adicionar', tag: string): void
  (e: 'remover', tag: string): void
}>()

const novaTag = ref('')

const handleAdicionarTag = () => {
  if (novaTag.value.trim()) {
    emit('adicionar', novaTag.value.trim())
    novaTag.value = ''
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-gray-800">
        <Tag class="h-5 w-5 text-gray-500"/>
        Tags de Agendamento
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="flex gap-3 mb-4">
        <Input
            v-model="novaTag"
            class="max-w-md"
            placeholder="Digite o nome da nova tag..."
            @keypress.enter="handleAdicionarTag"
        />
        <Button variant="secondary" @click="handleAdicionarTag">
          <Plus class="h-4 w-4 mr-2"/>
          Adicionar
        </Button>
      </div>

      <div class="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300 min-h-[80px]">
        <span v-if="tags.length === 0" class="text-gray-400 text-sm italic w-full text-center py-2">Nenhuma tag cadastrada</span>

        <Badge v-for="tag in tags" :key="tag" class="pl-3 pr-1 py-1.5 flex items-center gap-2 bg-white text-sm"
               variant="outline">
          {{ tag }}
          <button class="hover:bg-red-100 hover:text-red-600 rounded-full p-0.5 transition-colors"
                  @click="emit('remover', tag)">
            <X class="h-3.5 w-3.5"/>
          </button>
        </Badge>
      </div>
    </CardContent>
  </Card>
</template>