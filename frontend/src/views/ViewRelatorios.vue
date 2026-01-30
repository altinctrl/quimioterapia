<script lang="ts" setup>
import {ref} from 'vue'
import api from "@/services/api.ts";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {toast} from "vue-sonner";

const tipoRelatorio = ref('fim-plantao')
const dataSelecionada = ref(new Date().toISOString().split('T')[0])
const loading = ref(false)

const opcoes = [
  {label: 'Fechamento de Plantão', value: 'fim-plantao'},
  {label: 'Farmácia', value: 'medicacoes'}
]

const gerarRelatorio = async () => {
  if (!dataSelecionada.value) return

  loading.value = true
  try {
    const url = `/api/relatorios/${tipoRelatorio.value}?data=${dataSelecionada.value}`
    const {data} = await api.get(url, {responseType: 'blob'})
    const downloadUrl = window.URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `relatorio-${tipoRelatorio.value}-${dataSelecionada.value}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    console.error(error)
    toast.error('Erro ao gerar relatório. Verifique se existem dados para a data selecionada.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto my-auto">
    <Card class="bg-card shadow rounded-lg">
      <CardHeader class="text-2xl font-bold">
        <CardTitle>
          Relatórios
        </CardTitle>
      </CardHeader>

      <CardContent class="space-y-4">
        <div>
          <Label>
            Tipo de Relatório
          </Label>
          <Select v-model="tipoRelatorio">
            <SelectTrigger>
              <SelectValue/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="op in opcoes" :key="op.value" :value="op.value">
                {{ op.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>
            Data de Referência
          </Label>
          <Input
              v-model="dataSelecionada"
              type="date"
          />
        </div>

        <div class="pt-4">
          <Button
              :disabled="loading"
              class="w-full"
              @click="gerarRelatorio"
          >
            <span v-if="loading">Gerando PDF...</span>
            <span v-else>Baixar Relatório</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
