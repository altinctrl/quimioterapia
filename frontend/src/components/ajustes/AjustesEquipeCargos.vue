<script lang="ts" setup>
import {ref} from 'vue'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Badge} from '@/components/ui/badge'
import {Briefcase, Plus, X} from 'lucide-vue-next'

defineProps<{
  cargos: string[]
}>()

const emit = defineEmits<{
  (e: 'adicionar', cargo: string): void
  (e: 'remover', cargo: string): void
}>()

const novoCargo = ref('')

const handleAdicionar = () => {
  if (novoCargo.value.trim()) {
    emit('adicionar', novoCargo.value.trim())
    novoCargo.value = ''
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-gray-800">
        <Briefcase class="h-5 w-5 text-gray-500"/>
        Cargos da Equipe
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="flex gap-3 mb-4">
        <Input
            v-model="novoCargo"
            class="max-w-md"
            placeholder="Digite o nome do novo cargo..."
            @keydown.enter="handleAdicionar"
        />
        <Button variant="secondary" @click="handleAdicionar">
          <Plus class="h-4 w-4 mr-2"/>
          Adicionar
        </Button>
      </div>

      <div class="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300">
        <span
            v-if="cargos.length === 0"
            class="text-gray-400 text-sm italic w-full text-center py-2">
          Nenhum cargo cadastrado
        </span>

        <Badge
            v-for="crg in cargos"
            :key="crg"
            class="pl-3 pr-1 py-1.5 flex items-center gap-2 bg-white text-sm"
            variant="outline">
          {{ crg }}
          <button class="hover:bg-red-100 hover:text-red-600 rounded-full p-0.5 transition-colors"
                  @click="emit('remover', crg)">
            <X class="h-3.5 w-3.5"/>
          </button>
        </Badge>
      </div>
    </CardContent>
  </Card>
</template>
