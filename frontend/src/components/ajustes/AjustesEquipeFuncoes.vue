<script lang="ts" setup>
import {ref} from 'vue'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Badge} from '@/components/ui/badge'
import {ClipboardList, Plus, X} from 'lucide-vue-next'

const props = defineProps<{
  funcoes: string[]
}>()

const emit = defineEmits<{
  (e: 'adicionar', funcao: string): void
  (e: 'remover', funcao: string): void
}>()

const novaFuncao = ref('')

const handleAdicionar = () => {
  if (novaFuncao.value.trim()) {
    emit('adicionar', novaFuncao.value.trim())
    novaFuncao.value = ''
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-gray-800">
        <ClipboardList class="h-5 w-5 text-gray-500"/>
        Funções de Escala
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="flex gap-3 mb-4">
        <Input
            v-model="novaFuncao"
            class="max-w-md"
            placeholder="Digite o nome da nova função..."
            @keydown.enter="handleAdicionar"
        />
        <Button variant="secondary" @click="handleAdicionar">
          <Plus class="h-4 w-4 mr-2"/>
          Adicionar
        </Button>
      </div>

      <div class="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300">
        <span v-if="funcoes.length === 0" class="text-gray-400 text-sm italic w-full text-center py-2">Nenhuma função cadastrada</span>

        <Badge v-for="f in funcoes" :key="f" class="pl-3 pr-1 py-1.5 flex items-center gap-2 bg-white text-sm"
               variant="outline">
          {{ f }}
          <button class="hover:bg-red-100 hover:text-red-600 rounded-full p-0.5 transition-colors"
                  @click="emit('remover', f)">
            <X class="h-3.5 w-3.5"/>
          </button>
        </Badge>
      </div>
    </CardContent>
  </Card>
</template>
