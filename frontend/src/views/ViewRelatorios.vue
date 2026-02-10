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
const modoSelecao = ref('dia')
const dataInicio = ref(new Date().toISOString().split('T')[0])
const dataFim = ref(new Date().toISOString().split('T')[0])
const mesSelecionado = ref(new Date().toISOString().slice(0, 7))

const opcoes = [
  {label: 'Fechamento de Plantão', value: 'fim-plantao'},
  {label: 'Farmácia', value: 'medicacoes'}
]

const getParams = () => {
  if (modoSelecao.value === 'dia') {
    return `data_inicio=${dataInicio.value}&data_fim=${dataInicio.value}`
  } else if (modoSelecao.value === 'mes') {
    const [ano, mes] = mesSelecionado.value.split('-')
    const ultimoDia = new Date(parseInt(ano), parseInt(mes), 0).getDate()
    return `data_inicio=${ano}-${mes}-01&data_fim=${ano}-${mes}-${ultimoDia}`
  } else {
    return `data_inicio=${dataInicio.value}&data_fim=${dataFim.value}`
  }
}

const gerarRelatorio = async () => {
  if (!dataSelecionada.value) return

  loading.value = true
  try {
    const params = getParams()
    const url = `/api/relatorios/${tipoRelatorio.value}?${params}`
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
          <Label>Modo de Seleção</Label>
          <Select v-model="modoSelecao">
            <SelectTrigger>
              <SelectValue/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="dia">Diário</SelectItem>
              <SelectItem value="mes">Mensal</SelectItem>
              <SelectItem value="periodo">Período Personalizado</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div v-if="modoSelecao === 'dia'">
          <Label>Data</Label>
          <Input v-model="dataInicio" type="date"/>
        </div>

        <div v-if="modoSelecao === 'mes'">
          <Label>Mês de Referência</Label>
          <Input v-model="mesSelecionado" type="month"/>
        </div>

        <div v-if="modoSelecao === 'periodo'" class="flex gap-2">
          <div class="w-1/2">
            <Label>Início</Label>
            <Input v-model="dataInicio" type="date"/>
          </div>
          <div class="w-1/2">
            <Label>Fim</Label>
            <Input v-model="dataFim" type="date"/>
          </div>
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
