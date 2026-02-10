<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useAuthStore} from '@/stores/storeAuth'
import {BadgeCheck, Briefcase, Mail, Save, User, X} from 'lucide-vue-next'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const registroInput = ref('')
const loading = ref(false)

watch(() => props.isOpen, (newVal) => {
  if (newVal && authStore.user) {
    registroInput.value = authStore.user.registro || ''
  }
})

const labelRegistro = computed(() => {
  return authStore.user?.role === 'medico' ? 'CRM (com UF)' : 'COREN'
})

async function salvar() {
  if (!registroInput.value.trim()) return

  loading.value = true
  const sucesso = await authStore.atualizarRegistro(registroInput.value)
  loading.value = false

  if (sucesso) {
    emit('close')
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
    <Card class="w-full max-w-md relative shadow-xl">
      <button
          class="absolute right-4 top-4 text-gray-500 hover:text-gray-700"
          @click="$emit('close')"
      >
        <X class="h-5 w-5"/>
      </button>

      <CardHeader>
        <div class="flex items-center gap-3">
          <div class="bg-blue-100 p-2 rounded-full">
            <User class="h-6 w-6 text-blue-700"/>
          </div>
          <div>
            <CardTitle>Perfil do Usuário</CardTitle>
            <p class="text-sm text-gray-500">Suas informações de acesso</p>
          </div>
        </div>
      </CardHeader>

      <CardContent class="space-y-4">
        <div class="grid grid-cols-1 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-medium text-gray-500 flex items-center gap-1">
              <User class="h-3 w-3"/>
              Nome
            </label>
            <div class="p-2 bg-gray-50 rounded border border-gray-100 text-sm font-medium text-gray-800">
              {{ authStore.user?.nome }}
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-xs font-medium text-gray-500 flex items-center gap-1">
              <Briefcase class="h-3 w-3"/>
              Cargo / Função
            </label>
            <div class="p-2 bg-gray-50 rounded border border-gray-100 text-sm text-gray-800 capitalize">
              {{ authStore.user?.role }} <span v-if="authStore.user?.grupo"
                                               class="text-gray-400">({{ authStore.user?.grupo }})</span>
            </div>
          </div>

          <div v-if="authStore.user?.email" class="space-y-1">
            <label class="text-xs font-medium text-gray-500 flex items-center gap-1">
              <Mail class="h-3 w-3"/>
              Email
            </label>
            <div class="p-2 bg-gray-50 rounded border border-gray-100 text-sm text-gray-800">
              {{ authStore.user?.email }}
            </div>
          </div>
        </div>

        <div v-if="authStore.user?.role && ['medico', 'enfermeiro', 'admin'].includes(authStore.user?.role)" class="border-t border-gray-100 my-4"></div>

        <div v-if="authStore.user?.role && ['medico', 'enfermeiro', 'admin'].includes(authStore.user?.role)" class="space-y-2">
          <label class="text-sm font-medium text-blue-900 flex items-center gap-2">
            <BadgeCheck class="h-4 w-4"/>
            {{ labelRegistro }}
          </label>
          <div class="flex gap-2">
            <Input
                v-model="registroInput"
                :disabled="loading"
                :placeholder="authStore.user?.role === 'medico' ? 'Ex: 12345 PE' : 'Ex: 123.456'"
            />
            <Button :disabled="loading || !registroInput" @click="salvar">
              <Save v-if="!loading" class="h-4 w-4 mr-2"/>
              {{ loading ? '...' : 'Salvar' }}
            </Button>
          </div>
          <p v-if="!authStore.user?.registro && authStore.user?.role === 'medico'" class="text-xs text-orange-600 mt-1">
            * Obrigatório para prescrições.
          </p>
        </div>

      </CardContent>
    </Card>
  </div>
</template>
