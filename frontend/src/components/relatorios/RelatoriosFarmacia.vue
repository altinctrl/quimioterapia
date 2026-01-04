<script lang="ts" setup>
import {computed} from 'vue'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Download} from 'lucide-vue-next'

const props = defineProps<{
  dados: {
    summary: { totalEnviadas: number; totalAusencia: number }
    data: any[]
  }
}>()

const colunas = computed(() => {
  return Object.keys(props.dados.data[0] || {})
})
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-4">
      <Card class="bg-blue-50 border-blue-200">
        <CardContent class="pt-6">
          <p class="text-sm text-blue-700 font-medium">Total de Medicações Enviadas</p>
          <p class="text-3xl font-bold text-blue-900">{{ dados.summary.totalEnviadas }}</p>
        </CardContent>
      </Card>
      <Card class="bg-red-50 border-red-200">
        <CardContent class="pt-6">
          <p class="text-sm text-red-700 font-medium">Não Preparadas (Ausência)</p>
          <p class="text-3xl font-bold text-red-900">{{ dados.summary.totalAusencia }}</p>
        </CardContent>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Detalhes por Medicamento</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead v-for="col in colunas" :key="col">{{ col }}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="(row, i) in dados.data" :key="i">
              <TableCell v-for="col in colunas" :key="col">{{ row[col] }}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
        <Button class="w-full mt-4" variant="outline">
          <Download class="h-4 w-4 mr-2"/>
          Exportar CSV
        </Button>
      </CardContent>
    </Card>
  </div>
</template>