<script lang="ts" setup>
import {useRouter} from 'vue-router'
import {Button} from '@/components/ui/button'
import {CheckCircle2, Download} from 'lucide-vue-next'

defineProps<{
  concluida: boolean
}>()

const emit = defineEmits<{
  (e: 'confirmar'): void
  (e: 'baixar'): void
}>()

const router = useRouter()
</script>

<template>
  <div v-if="concluida"
       class="flex flex-col items-center justify-center py-12 space-y-6 animate-in fade-in slide-in-from-bottom-4">
    <div class="bg-green-100 p-4 rounded-full">
      <CheckCircle2 class="h-16 w-16 text-green-600"/>
    </div>
    <div class="text-center">
      <h2 class="text-2xl font-bold text-gray-900">Prescrição Emitida!</h2>
      <p class="text-gray-500">O documento foi salvo no histórico do paciente.</p>
    </div>

    <div class="flex gap-4">
      <Button class="gap-2" variant="outline" @click="emit('baixar')">
        <Download class="h-4 w-4"/>
        Baixar PDF
      </Button>
      <Button @click="router.back()">
        Voltar para Lista
      </Button>
    </div>
  </div>

  <div v-else class="space-y-6">
    <div class="flex items-center justify-end gap-4 pt-4">
      <Button variant="ghost" @click="router.back()">Cancelar</Button>
      <Button class="bg-green-600 hover:bg-green-700 text-white min-w-[200px]" size="lg" @click="emit('confirmar')">
        <CheckCircle2 class="h-5 w-5 mr-2"/>
        Confirmar Prescrição
      </Button>
    </div>
  </div>
</template>
