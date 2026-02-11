<script lang="ts" setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAuthStore} from '@/stores/storeAuth.ts'
import {AlertCircle, Hospital, Lock, User} from 'lucide-vue-next'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Alert, AlertDescription} from '@/components/ui/alert'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const authStore = useAuthStore()
const router = useRouter()

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    const result = await authStore.login(username.value, password.value)

    if (!result.success) {
      error.value = result.error || 'Erro ao fazer login'
    } else {
      const role = authStore.user?.role
      if (role === 'farmacia') {
        void router.push('/farmacia')
      } else if (role === 'medico') {
        void router.push('/pacientes')
      } else {
        void router.push('/agenda')
      }
    }
  } catch (err) {
    error.value = 'Erro ao conectar com o servidor'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md relative">
      <div class="text-center mb-8 absolute bottom-full left-0 right-0">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
          <Hospital class="h-8 w-8 text-white"/>
        </div>
        <h1 class="text-gray-900 mb-2 text-2xl font-medium">Sistema de Oncologia</h1>
        <p class="text-sm text-gray-600">Hospital das Clínicas UFPE</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Acesso ao Sistema</CardTitle>
          <CardDescription>
            Entre com suas credenciais do Active Directory
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form class="space-y-4" @submit.prevent="handleSubmit">
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700" for="username">
                Usuário
              </label>
              <div class="relative">
                <User class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"/>
                <Input
                    id="username"
                    v-model="username"
                    autocomplete="username"
                    class="pl-10"
                    placeholder="seu.usuario"
                    required
                    type="text"
                />
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700" for="password">
                Senha
              </label>
              <div class="relative">
                <Lock class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"/>
                <Input
                    id="password"
                    v-model="password"
                    autocomplete="current-password"
                    class="pl-10"
                    placeholder="••••••••"
                    required
                    type="password"
                />
              </div>
            </div>

            <Alert v-if="error" class="bg-red-50 border-red-200" variant="destructive">
              <AlertCircle class="h-4 w-4"/>
              <AlertDescription class="text-red-700">{{ error }}</AlertDescription>
            </Alert>

            <Button :disabled="loading" class="w-full" type="submit">
              {{ loading ? 'Autenticando...' : 'Entrar' }}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
