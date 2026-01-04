<script lang="ts" setup>
import {computed} from 'vue'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {Download} from 'lucide-vue-next'

const props = defineProps<{
  dados: any[]
}>()

const colunas = computed(() => {
  if (props.dados.length > 0) {
    return Object.keys(props.dados[0])
  }
  return []
})
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Resultados</CardTitle>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead v-for="col in colunas" :key="col">{{ col }}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="(row, i) in dados" :key="i">
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
</template>