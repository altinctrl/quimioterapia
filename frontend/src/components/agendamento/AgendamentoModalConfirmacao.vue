<script lang="ts" setup>
import {computed} from 'vue'
import {Button} from '@/components/ui/button'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {AlertTriangle} from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  avisos: string[]
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'confirmar'): void
}>()

const isOpen = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogContent>
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2 text-amber-600">
          <AlertTriangle class="h-5 w-5"/>
          Atenção Necessária
        </DialogTitle>
        <DialogDescription>
          O agendamento apresenta os seguintes alertas. Como enfermeiro(a), você tem autonomia para prosseguir se
          julgar necessário.
        </DialogDescription>
      </DialogHeader>

      <div class="py-4">
        <ul class="list-disc list-inside space-y-2 text-sm text-gray-700">
          <li v-for="(aviso, idx) in avisos" :key="idx">
            {{ aviso }}
          </li>
        </ul>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="isOpen = false">Cancelar</Button>
        <Button variant="destructive" @click="emit('confirmar')">Agendar Mesmo Assim</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
