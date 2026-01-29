<script lang="ts" setup>
import {onMounted} from 'vue'
import {useRoute} from 'vue-router'
import ProtocolosFormulario from '@/components/protocolos/ProtocolosFormulario.vue'
import {Button} from "@/components/ui/button"
import {Save} from 'lucide-vue-next'
import {useProtocoloFormulario} from '@/composables/useProtocoloFormulario.ts'

const route = useRoute()
const id = route.params.id as string | undefined

const {
  formData,
  loading,
  isEditMode,
  initForm,
  saveProtocolo,
  cancelEdit
} = useProtocoloFormulario(id)

onMounted(() => {
  initForm()
})
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    <div v-if="loading" class="flex justify-center py-12">
      <p class="text-muted-foreground animate-pulse">Carregando dados...</p>
    </div>

    <template v-else>
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">
            {{ isEditMode ? 'Editar Protocolo' : 'Novo Protocolo' }}
          </h1>
        </div>

        <div class="flex items-center gap-3">
          <Button variant="outline" @click="cancelEdit">
            Cancelar
          </Button>
          <Button class="flex items-center gap-2" @click="saveProtocolo">
            <Save class="h-4 w-4"/>
            Salvar
          </Button>
        </div>
      </div>

      <ProtocolosFormulario
          v-model="formData"
      />
    </template>
  </div>
</template>
