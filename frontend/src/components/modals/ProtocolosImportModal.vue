<script lang="ts" setup>
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {Button} from '@/components/ui/button'
import {ScrollArea} from '@/components/ui/scroll-area'
import {Badge} from '@/components/ui/badge'
import {Protocolo} from "@/types/protocoloTypes.ts";

defineProps<{
  open: boolean
  protocolos: Protocolo[]
  ignored: number
}>()

const emit = defineEmits(['update:open', 'confirmar'])

const fechar = () => emit('update:open', false)
const confirmar = () => {
  emit('confirmar')
  fechar()
}
</script>

<template>
  <Dialog :open="open" @update:open="fechar">
    <DialogContent class="max-w-2xl max-h-[90vh] grid grid-rows-[auto_1fr_auto] p-0 gap-0 overflow-hidden">

      <DialogHeader class="p-6 pb-4 border-b">
        <DialogTitle class="flex items-center gap-2">
          Resumo da Importação
        </DialogTitle>
        <DialogDescription>
          Verifique os protocolos identificados antes de confirmar.
        </DialogDescription>
      </DialogHeader>

      <ScrollArea class="min-h-0 w-full">
        <div class="p-6 space-y-4">
          <div
              v-for="(p, idx) in protocolos"
              :key="idx"
              class="border rounded-lg p-4 bg-slate-50/50"
          >
            <h4 class="font-bold text-slate-900 mb-1">{{ p.nome }}</h4>
            <p class="text-sm text-slate-500 mb-1">{{ p.indicacao || 'Sem indicação descrita' }}</p>

            <div class="flex flex-wrap gap-2">
              <Badge
                  v-for="t in p.templatesCiclo"
                  :key="t.idTemplate"
                  class="text-xs"
                  variant="outline"
              >
                {{ t.idTemplate }}: {{ t.blocos.length }} blocos
              </Badge>
            </div>
          </div>
        </div>
      </ScrollArea>

      <DialogFooter class="p-6 border-t flex items-center justify-between sm:justify-between w-full bg-white">
        <p class="text-xs text-muted-foreground flex items-center gap-1">
          {{ protocolos.length }} protocolos validados.
          <span v-if="ignored > 0"> {{ ignored }} descartados.</span>
        </p>
        <div class="flex gap-2">
          <Button variant="ghost" @click="fechar">Cancelar</Button>
          <Button @click="confirmar">Confirmar Importação</Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
