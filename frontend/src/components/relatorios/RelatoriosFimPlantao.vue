<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Download} from 'lucide-vue-next'

defineProps<{
  dados: {
    periodo: string
    censo: any
    gruposProtocolo: any
  }
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Relatório de Fim de Plantão - {{ dados.periodo }}</CardTitle>
    </CardHeader>
    <CardContent class="space-y-6">
      <div class="grid grid-cols-5 gap-3">
        <Card class="bg-blue-50">
          <CardContent class="pt-4"><p class="text-xs">Agendados</p>
            <p class="text-2xl">{{ dados.censo.agendados }}</p></CardContent>
        </Card>
        <Card class="bg-green-50">
          <CardContent class="pt-4"><p class="text-xs">Atendidos</p>
            <p class="text-2xl">{{ dados.censo.atendidos }}</p></CardContent>
        </Card>
        <Card class="bg-yellow-50">
          <CardContent class="pt-4"><p class="text-xs">Remarcados</p>
            <p class="text-2xl">{{ dados.censo.remarcados }}</p></CardContent>
        </Card>
        <Card class="bg-purple-50">
          <CardContent class="pt-4"><p class="text-xs">Internados</p>
            <p class="text-2xl">{{ dados.censo.internados }}</p></CardContent>
        </Card>
        <Card class="bg-orange-50">
          <CardContent class="pt-4"><p class="text-xs">Extra</p>
            <p class="text-2xl">{{ dados.censo.extra }}</p></CardContent>
        </Card>
      </div>

      <div>
        <h3 class="font-semibold mb-3">Grupos de Protocolo</h3>
        <div class="grid grid-cols-3 gap-3">
          <div class="bg-gray-50 rounded p-3"><p class="text-sm text-gray-600">Até 2h</p>
            <p class="text-xl">{{ dados.gruposProtocolo.ate2h }}</p></div>
          <div class="bg-gray-50 rounded p-3"><p class="text-sm text-gray-600">2h a 4h</p>
            <p class="text-xl">{{ dados.gruposProtocolo.de2a4h }}</p></div>
          <div class="bg-gray-50 rounded p-3"><p class="text-sm text-gray-600">> 4h</p>
            <p class="text-xl">{{ dados.gruposProtocolo.acima4h }}</p></div>
        </div>
      </div>

      <Button class="w-full" variant="outline">
        <Download class="h-4 w-4 mr-2"/>
        Exportar PDF
      </Button>
    </CardContent>
  </Card>
</template>