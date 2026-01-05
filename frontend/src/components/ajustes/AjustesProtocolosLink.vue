<script lang="ts" setup>
import {useRouter} from 'vue-router'
import {Card, CardContent} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {FileText} from 'lucide-vue-next'

const router = useRouter()
</script>

<template>
  <Card class="border-l-4 border-l-blue-600">
    <CardContent class="flex items-center justify-between p-6">
      <div>
        <h3 class="text-lg font-medium text-gray-900 flex items-center gap-2">
          <FileText class="h-5 w-5 text-blue-600"/>
          Cadastro de Protocolos
        </h3>
        <p class="text-sm text-gray-500 mt-1">Gerencie medicamentos, doses padrão, tempos de infusão e regras
          clínicas.</p>
      </div>
      <Button class="border-blue-200 text-blue-700 hover:bg-blue-50" variant="outline"
              @click="router.push('/protocolos')">
        Acessar Gerenciador
      </Button>
    </CardContent>
  </Card>
</template>