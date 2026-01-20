<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {useAppStore} from '@/stores/app'
import {Agendamento, PrescricaoMedica} from "@/types";

defineProps<{
  agendamentos: Agendamento[]
  prescricoes: PrescricaoMedica[]
}>()

const emit = defineEmits<{
  (e: 'ver-agendamento', item: any): void
  (e: 'ver-prescricao', item: any): void
}>()

const appStore = useAppStore()

const getStatusLabel = (status: string) => {
  if (!status) return '-'
  return appStore.getStatusConfig(status).label
}

const formatarStatusPrescricao = (status: string) => {
  const mapa: Record<string, string> = {
    'ativa': 'Ativa', 'concluida': 'Concluída', 'pausada': 'Pausada', 'cancelada': 'Cancelada'
  }
  return mapa[status] || status?.charAt(0).toUpperCase() + status?.slice(1)
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Histórico Clínico</CardTitle>
    </CardHeader>
    <CardContent>
      <Tabs defaultValue="agendamentos">
        <TabsList class="grid w-full grid-cols-2">
          <TabsTrigger value="agendamentos">Agendamentos</TabsTrigger>
          <TabsTrigger value="prescricoes">Prescrições</TabsTrigger>
        </TabsList>

        <TabsContent class="mt-4" value="agendamentos">
          <Table>
            <TableHeader>
              <TableRow class="hover:bg-transparent">
                <TableHead>Data</TableHead>
                <TableHead>Horário</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="agendamentos.length === 0">
                <TableCell class="text-center text-gray-500 py-8" colspan="5">Nenhum agendamento encontrado</TableCell>
              </TableRow>
              <TableRow
                  v-for="ag in agendamentos"
                  :key="ag.id"
                  class="cursor-pointer hover:bg-gray-50"
                  @click="emit('ver-agendamento', ag)"
              >
                <TableCell>{{ new Date(ag.data).toLocaleDateString('pt-BR') }}</TableCell>
                <TableCell>{{ ag.horarioInicio }}</TableCell>
                <TableCell class="capitalize">{{ ag.tipo }}</TableCell>
                <TableCell>{{ getStatusLabel(ag.status) }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TabsContent>

        <TabsContent class="mt-4" value="prescricoes">
          <Table>
            <TableHeader>
              <TableRow class="hover:bg-transparent">
                <TableHead>Data</TableHead>
                <TableHead>Protocolo</TableHead>
                <TableHead>Ciclo</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="prescricoes.length === 0">
                <TableCell class="text-center text-gray-500 py-8" colspan="5">Nenhuma prescrição encontrada</TableCell>
              </TableRow>
              <TableRow
                  v-for="p in prescricoes"
                  :key="p.id"
                  class="cursor-pointer hover:bg-gray-50"
                  @click="emit('ver-prescricao', p)"
              >
                <TableCell>{{ new Date(p.dataEmissao).toLocaleDateString('pt-BR') }}</TableCell>
                <TableCell>{{ p.conteudo?.protocolo?.nome || 'N/A' }}</TableCell>
                <TableCell>
                  {{ p.conteudo?.protocolo?.cicloAtual }}
                </TableCell>
                <TableCell>{{ formatarStatusPrescricao(p.status) }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TabsContent>
      </Tabs>
    </CardContent>
  </Card>
</template>
