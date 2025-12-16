<script lang="ts" setup>
import {reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Checkbox} from '@/components/ui/checkbox'
import {Badge} from '@/components/ui/badge'
import {Calendar as CalendarIcon, Clock, FileText, Plus, Tag, X} from 'lucide-vue-next'
import {toast} from 'vue-sonner'

const router = useRouter()
const appStore = useAppStore()

const horarioAbertura = ref(appStore.parametros.horarioAbertura)
const horarioFechamento = ref(appStore.parametros.horarioFechamento)

const diasSemana = [
  {value: 0, label: 'Domingo'},
  {value: 1, label: 'Segunda'},
  {value: 2, label: 'Terça'},
  {value: 3, label: 'Quarta'},
  {value: 4, label: 'Quinta'},
  {value: 5, label: 'Sexta'},
  {value: 6, label: 'Sábado'}
]

const diasSelecionados = ref<number[]>([...appStore.parametros.diasFuncionamento])

const toggleDia = (dia: number) => {
  if (diasSelecionados.value.includes(dia)) {
    diasSelecionados.value = diasSelecionados.value.filter(d => d !== dia)
  } else {
    diasSelecionados.value = [...diasSelecionados.value, dia].sort()
  }
}

const grupos = reactive({
  rapido: {...appStore.parametros.gruposInfusao.rapido},
  medio: {...appStore.parametros.gruposInfusao.medio},
  longo: {...appStore.parametros.gruposInfusao.longo}
})

const tags = ref(['1ª vez', 'Mudança de protocolo', 'Reação prévia', 'Quimio adiada', 'Redução de dose'])
const novaTag = ref('')

const handleAdicionarTag = () => {
  if (novaTag.value.trim() && !tags.value.includes(novaTag.value.trim())) {
    tags.value.push(novaTag.value.trim())
    novaTag.value = ''
  }
}

const handleRemoverTag = (tag: string) => {
  tags.value = tags.value.filter(t => t !== tag)
}

const handleSalvar = () => {
  appStore.parametros.horarioAbertura = horarioAbertura.value
  appStore.parametros.horarioFechamento = horarioFechamento.value
  appStore.parametros.diasFuncionamento = [...diasSelecionados.value]
  appStore.parametros.gruposInfusao = grupos

  toast.success('Configurações salvas com sucesso!')
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-8 pb-10">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Configurações</h1>
      </div>
      <Button class="shadow-sm" size="lg" @click="handleSalvar">Salvar Alterações</Button>
    </div>

    <div class="grid grid-cols-1 gap-8">

      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2 text-gray-800">
            <CalendarIcon class="h-5 w-5 text-gray-500"/>
            Funcionamento da Clínica
          </CardTitle>
        </CardHeader>
        <CardContent class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-gray-50 p-4 rounded-lg border">
              <Label class="text-base text-gray-700 mb-2 block">Horário de Atendimento</Label>
              <div class="flex gap-4 items-center">
                <div class="flex-1">
                  <span class="text-xs text-gray-500 uppercase font-bold">Abertura</span>
                  <Input v-model="horarioAbertura" class="mt-1 bg-white" type="time"/>
                </div>
                <div class="flex-1">
                  <span class="text-xs text-gray-500 uppercase font-bold">Fechamento</span>
                  <Input v-model="horarioFechamento" class="mt-1 bg-white" type="time"/>
                </div>
              </div>
            </div>

            <div>
              <Label class="text-base text-gray-700 mb-3 block">Dias da Semana</Label>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div v-for="dia in diasSemana" :key="dia.value"
                     :class="[
                    'flex items-center space-x-2 border p-2 rounded-md transition-colors',
                    diasSelecionados.includes(dia.value) ? 'bg-blue-50 border-blue-200' : 'bg-white hover:bg-gray-50'
                  ]"
                >
                  <Checkbox
                      :id="`dia-${dia.value}`"
                      :checked="diasSelecionados.includes(dia.value)"
                      @update:checked="toggleDia(dia.value)"
                  />
                  <Label :for="`dia-${dia.value}`" class="cursor-pointer font-normal text-sm w-full py-1">
                    {{ dia.label }}
                  </Label>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2 text-gray-800">
            <Clock class="h-5 w-5 text-gray-500"/>
            Capacidade por Tempo de Infusão
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-sm text-gray-500 mb-6">Defina quantas vagas simultâneas ou diárias existem para cada categoria
            de duração.</p>

          <div class="space-y-4">
            <div
                class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-green-50/50 border border-green-100">
              <div class="sm:w-1/3">
                <span class="text-green-800 font-semibold text-lg flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-green-500"></span> Rápido
                </span>
                <p class="text-xs text-green-700 mt-1">Infusões de curta duração</p>
              </div>
              <div class="flex-1 w-full">
                <Label class="text-xs text-green-800 uppercase font-bold">Descrição (Tempo)</Label>
                <Input v-model="grupos.rapido.duracao" class="bg-white mt-1"/>
              </div>
              <div class="flex-1 w-full">
                <Label class="text-xs text-green-800 uppercase font-bold">Vagas Totais</Label>
                <Input v-model="grupos.rapido.vagas" class="bg-white mt-1" type="number"/>
              </div>
            </div>

            <div class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-blue-50/50 border border-blue-100">
              <div class="sm:w-1/3">
                <span class="text-blue-800 font-semibold text-lg flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-blue-500"></span> Médio
                </span>
                <p class="text-xs text-blue-700 mt-1">Infusões padrão</p>
              </div>
              <div class="flex-1 w-full">
                <Label class="text-xs text-blue-800 uppercase font-bold">Descrição (Tempo)</Label>
                <Input v-model="grupos.medio.duracao" class="bg-white mt-1"/>
              </div>
              <div class="flex-1 w-full">
                <Label class="text-xs text-blue-800 uppercase font-bold">Vagas Totais</Label>
                <Input v-model="grupos.medio.vagas" class="bg-white mt-1" type="number"/>
              </div>
            </div>

            <div
                class="flex flex-col sm:flex-row items-end gap-4 p-4 rounded-lg bg-purple-50/50 border border-purple-100">
              <div class="sm:w-1/3">
                <span class="text-purple-800 font-semibold text-lg flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-purple-500"></span> Longo
                </span>
                <p class="text-xs text-purple-700 mt-1">Infusões extensas</p>
              </div>
              <div class="flex-1 w-full">
                <Label class="text-xs text-purple-800 uppercase font-bold">Descrição (Tempo)</Label>
                <Input v-model="grupos.longo.duracao" class="bg-white mt-1"/>
              </div>
              <div class="flex-1 w-full">
                <Label class="text-xs text-purple-800 uppercase font-bold">Vagas Totais</Label>
                <Input v-model="grupos.longo.vagas" class="bg-white mt-1" type="number"/>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2 text-gray-800">
            <Tag class="h-5 w-5 text-gray-500"/>
            Tags de Agendamento
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="flex gap-3 mb-4">
            <Input
                v-model="novaTag"
                class="max-w-md"
                placeholder="Digite o nome da nova tag..."
                @keypress.enter="handleAdicionarTag"
            />
            <Button variant="secondary" @click="handleAdicionarTag">
              <Plus class="h-4 w-4 mr-2"/>
              Adicionar
            </Button>
          </div>

          <div class="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300 min-h-[80px]">
            <span v-if="tags.length === 0" class="text-gray-400 text-sm italic w-full text-center py-2">Nenhuma tag cadastrada</span>

            <Badge v-for="tag in tags" :key="tag" class="pl-3 pr-1 py-1.5 flex items-center gap-2 bg-white text-sm"
                   variant="outline">
              {{ tag }}
              <button class="hover:bg-red-100 hover:text-red-600 rounded-full p-0.5 transition-colors"
                      @click="handleRemoverTag(tag)">
                <X class="h-3.5 w-3.5"/>
              </button>
            </Badge>
          </div>
        </CardContent>
      </Card>

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

    </div>
  </div>
</template>
