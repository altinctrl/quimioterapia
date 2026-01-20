<script lang="ts" setup>
import {computed} from 'vue'
import {CardContent} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Button} from '@/components/ui/button'
import {AlertCircle, Phone, Plus, Trash2} from 'lucide-vue-next'
import type {Paciente} from '@/types'

const props = defineProps<{
  modelValue: Partial<Paciente>
  modoEdicao: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Partial<Paciente>): void
}>()

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const idadeCalculada = computed(() => {
  if (!form.value.dataNascimento) return '0 anos'
  const hoje = new Date()
  const nasc = new Date(form.value.dataNascimento)
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const m = hoje.getMonth() - nasc.getMonth()
  if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--
  return `${idade} anos`
})

const adicionarContato = () => {
  if (!form.value.contatosEmergencia) {
    form.value.contatosEmergencia = []
  }
  form.value.contatosEmergencia.push({
    nome: '',
    parentesco: '',
    telefone: ''
  })
}

const removerContato = (index: number) => {
  if (form.value.contatosEmergencia) {
    form.value.contatosEmergencia.splice(index, 1)
  }
}
</script>

<template>
  <CardContent class="space-y-8">
    <div>
      <h3 class="text-gray-900 mb-4 font-medium text-lg border-b pb-2">Dados Cadastrais</h3>
      <div class="grid grid-cols-1 gap-6">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <Label>Peso (kg)</Label>
            <Input
                v-model.number="form.peso"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="number"
            />
          </div>
          <div>
            <Label>Altura (cm)</Label>
            <Input
                v-model.number="form.altura"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="number"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <Label>Data de Nascimento</Label>
            <Input
                v-model="form.dataNascimento"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="date"
            />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <Label>Idade</Label>
              <Input
                  :model-value="idadeCalculada"
                  class="mt-1 bg-gray-50 border-transparent bg-transparent shadow-none px-0 disabled:opacity-100 disabled:cursor-default"
                  disabled
              />
            </div>
            <div>
              <Label>Sexo</Label>
              <Input
                  v-model="form.sexo"
                  class="mt-1 bg-gray-50 border-transparent bg-transparent shadow-none px-0 disabled:opacity-100 disabled:cursor-default uppercase"
                  disabled
                  title="O sexo não pode ser alterado"
              />
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <Label>Telefone</Label>
            <Input
                v-model="form.telefone"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
            />
          </div>
          <div>
            <Label>Email</Label>
            <Input
                v-model="form.email"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="email"
            />
          </div>
        </div>
      </div>
    </div>

    <div>
      <div class="flex items-center justify-between border-b pb-2 mb-4">
        <h3 class="text-gray-900 font-medium text-lg flex items-center gap-2">
          <Phone class="h-5 w-5"/>
          Contatos de Emergência
        </h3>
        <Button
            v-if="modoEdicao"
            class="h-8"
            size="sm"
            variant="outline"
            @click="adicionarContato"
        >
          <Plus class="h-4 w-4 mr-2"/>
          Adicionar
        </Button>
      </div>

      <div v-if="form.contatosEmergencia && form.contatosEmergencia.length > 0" class="space-y-4">
        <div
            v-for="(contato, idx) in form.contatosEmergencia" :key="idx"
            class="relative grid grid-cols-1 md:grid-cols-[1fr_1fr_1fr_auto] gap-4 bg-gray-50 p-4 rounded-lg border group items-end"
        >
          <div>
            <Label class="text-xs text-gray-500 mb-1 block">Nome</Label>
            <Input
                v-model="contato.nome"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="disabled:opacity-100 disabled:cursor-default transition-all"
            />
          </div>
          <div>
            <Label class="text-xs text-gray-500 mb-1 block">Parentesco</Label>
            <Input
                v-model="contato.parentesco"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="disabled:opacity-100 disabled:cursor-default transition-all"
            />
          </div>
          <div>
            <Label class="text-xs text-gray-500 mb-1 block">Telefone</Label>
            <Input
                v-model="contato.telefone"
                :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                         'border-input bg-background': modoEdicao}"
                :disabled="!modoEdicao"
                class="disabled:opacity-100 disabled:cursor-default transition-all"
            />
          </div>
          <Button
              v-if="modoEdicao"
              class="hover:bg-red-50 hover:text-red-600"
              size="icon"
              title="Remover contato"
              variant="outline"
              @click="removerContato(idx)"
          >
            <Trash2 class="h-4 w-4"/>
          </Button>
        </div>
      </div>
      <div v-else class="text-gray-500 text-sm italic py-4 text-center bg-gray-50/50 rounded-md border border-dashed">
        {{ modoEdicao ? 'Aperte "Adicionar" para incluir um contato.' : 'Nenhum contato de emergência cadastrado.' }}
      </div>
    </div>

    <div>
      <h3 class="text-red-700 mb-2 font-medium text-lg flex items-center gap-2">
        <AlertCircle class="h-5 w-5"/>
        Observações Clínicas / Alergias
      </h3>
      <Textarea
          v-model="form.observacoesClinicas"
          :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                   'border-red-200 focus:border-red-400 bg-red-50/30': modoEdicao}"
          :disabled="!modoEdicao"
          class="mt-1 min-h-[100px] disabled:opacity-100 disabled:cursor-default transition-all"
          placeholder="Registre alergias e observações importantes..."
      />
    </div>
  </CardContent>
</template>
