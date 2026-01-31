<script lang="ts" setup>
import {computed} from 'vue'
import {CardContent} from '@/components/ui/card'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Button} from '@/components/ui/button'
import {AlertCircle, ClipboardList, Phone, Plus, Trash2} from 'lucide-vue-next'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";

const props = defineProps<{
  fields: any
  contatos: {
    fields: any
    push: (item: any) => void
    remove: (idx: number) => void
  }
  errors: Record<string, string | undefined>
  modoEdicao: boolean
}>()

const errorClass = (field: string) =>
    props.errors[field] ? 'border-red-500 focus-visible:ring-red-500' : ''

const idadeCalculada = computed(() => {
  const dataNasc = props.fields.dataNascimento.value
  if (!dataNasc) return '-'
  const hoje = new Date()
  const nasc = new Date(dataNasc)
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const m = hoje.getMonth() - nasc.getMonth()
  if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--
  return `${idade} anos`
})

const adicionarContato = () => {
  props.contatos.push({
    nome: '',
    parentesco: '',
    telefone: ''
  })
}
</script>

<template>
  <CardContent class="space-y-8">
    <div>
      <div class="flex items-center justify-between border-b pb-2 mb-4">
        <h3 class="text-gray-900 font-medium text-lg flex items-center gap-2">
          <ClipboardList class="h-5 w-5"/>
          Dados Cadastrais
        </h3>
      </div>

      <div class="grid grid-cols-1 gap-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div class="lg:col-span-1">
            <Label :class="{'text-red-500': errors.peso}">Peso (kg)</Label>
            <Input
                v-model="fields.peso.value"
                :class="[errorClass('peso'),
                  {'border-transparent bg-transparent shadow-none px-0 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none': !modoEdicao,
                   'border-input bg-background': modoEdicao}]"
                :disabled="!modoEdicao"
                :placeholder="modoEdicao ? '' : '-'"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="number"
                v-bind="fields.pesoProps.value"
            />
            <span v-if="errors.peso" class="text-xs text-red-500">{{ errors.peso }}</span>
          </div>

          <div class="lg:col-span-1">
            <Label :class="{'text-red-500': errors.altura}">Altura (cm)</Label>
            <Input
                v-model="fields.altura.value"
                :class="[errorClass('altura'),
                  {'border-transparent bg-transparent shadow-none px-0 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none': !modoEdicao,
                   'border-input bg-background': modoEdicao}]"
                :disabled="!modoEdicao"
                :placeholder="modoEdicao ? '' : '-'"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="number"
                v-bind="fields.alturaProps.value"
            />
            <span v-if="errors.altura" class="text-xs text-red-500">{{ errors.altura }}</span>
          </div>

          <div class="lg:col-span-1">
            <Label>Sexo</Label>
            <Select
                v-model="fields.sexo.value"
                :disabled="!modoEdicao"
            >
              <SelectTrigger
                  :class="{'border-transparent bg-transparent p-0 shadow-none [&>svg]:hidden' : !modoEdicao}"
                  class="mt-1 transition-all disabled:opacity-100 disabled:cursor-default"
              >
                <SelectValue :placeholder="modoEdicao ? '' : '-'"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="M">Masculino</SelectItem>
                <SelectItem value="F">Feminino</SelectItem>
              </SelectContent>
            </Select>
            <span v-if="errors.sexo && modoEdicao" class="text-xs text-red-500">{{ errors.sexo }}</span>
          </div>

          <div class="md:col-span-1 lg:col-span-1">
            <Label :class="{'text-red-500': errors.dataNascimento}">Data de Nascimento</Label>
            <Input
                v-model="fields.dataNascimento.value"
                :class="[errorClass('dataNascimento'),
                  {'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                   'border-input bg-background': modoEdicao}]"
                :disabled="!modoEdicao"
                :placeholder="modoEdicao ? '' : '-'"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="date"
                v-bind="fields.dataNascimentoProps.value"
            />
            <span v-if="errors.dataNascimento" class="text-xs text-red-500">{{ errors.dataNascimento }}</span>
          </div>

          <div class="md:col-span-1 lg:col-span-1">
            <Label>Idade</Label>
            <Input
                :model-value="idadeCalculada"
                class="mt-1 bg-gray-50 border-transparent bg-transparent shadow-none px-0 disabled:opacity-100 disabled:cursor-default"
                disabled
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <Label :class="{'text-red-500': errors.telefone}">Telefone</Label>
            <Input
                v-model="fields.telefone.value"
                :class="[errorClass('telefone'),
                  {'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                   'border-input bg-background': modoEdicao}]"
                :disabled="!modoEdicao"
                :placeholder="modoEdicao ? '' : '-'"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                v-bind="fields.telefoneProps.value"
            />
            <span v-if="errors.telefone" class="text-xs text-red-500">{{ errors.telefone }}</span>
          </div>
          <div>
            <Label :class="{'text-red-500': errors.email}">Email</Label>
            <Input
                v-model="fields.email.value"
                :class="[errorClass('email'),
                  {'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                   'border-input bg-background': modoEdicao}]"
                :disabled="!modoEdicao"
                :placeholder="modoEdicao ? '' : '-'"
                class="mt-1 disabled:opacity-100 disabled:cursor-default transition-all"
                type="email"
                v-bind="fields.emailProps.value"
            />
            <span v-if="errors.email" class="text-xs text-red-500">{{ errors.email }}</span>
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
      </div>

      <div class="space-y-4">
        <div v-if="contatos.fields.length > 0" class="space-y-4">
          <div
              v-for="(field, idx) in contatos.fields" :key="field.key"
              class="relative grid grid-cols-1 md:grid-cols-[1fr_1fr_1fr_auto] gap-4 bg-gray-50 p-4 rounded-lg border group items-start"
          >
            <div>
              <Label class="text-xs text-gray-500 mb-1 block">Nome</Label>
              <Input
                  v-model="field.value.nome"
                  :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                           'border-input bg-background': modoEdicao}"
                  :disabled="!modoEdicao"
                  class="disabled:opacity-100 disabled:cursor-default transition-all"
              />
              <span v-if="errors[`contatosEmergencia[${idx}].nome`]" class="text-xs text-red-500">
                {{ errors[`contatosEmergencia[${idx}].nome`] }}
              </span>
            </div>

            <div>
              <Label class="text-xs text-gray-500 mb-1 block">Parentesco</Label>
              <Input
                  v-model="field.value.parentesco"
                  :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                           'border-input bg-background': modoEdicao}"
                  :disabled="!modoEdicao"
                  class="disabled:opacity-100 disabled:cursor-default transition-all"
              />
              <span v-if="errors[`contatosEmergencia[${idx}].parentesco`]" class="text-xs text-red-500">
                {{ errors[`contatosEmergencia[${idx}].parentesco`] }}
              </span>
            </div>

            <div>
              <Label class="text-xs text-gray-500 mb-1 block">Telefone</Label>
              <Input
                  v-model="field.value.telefone"
                  :class="{'border-transparent bg-transparent shadow-none px-0': !modoEdicao,
                           'border-input bg-background': modoEdicao}"
                  :disabled="!modoEdicao"
                  class="disabled:opacity-100 disabled:cursor-default transition-all"
              />
              <span v-if="errors[`contatosEmergencia[${idx}].telefone`]" class="text-xs text-red-500">
                {{ errors[`contatosEmergencia[${idx}].telefone`] }}
              </span>
            </div>

            <div :class="[modoEdicao ? 'visible' : 'invisible']">
              <Label class="text-xs mb-1 block opacity-0 select-none">Remover</Label>
              <Button
                  class="hover:bg-red-50 hover:text-red-600 hover:border-red-100 transition-colors"
                  size="icon"
                  title="Remover contato"
                  variant="outline"
                  @click="contatos.remove(idx as number)"
              >
                <Trash2 class="h-4 w-4"/>
              </Button>
            </div>
          </div>
        </div>

        <div v-if="modoEdicao"
             class="flex items-center justify-center border border-dashed rounded-lg min-h-[70px] bg-gray-50"
        >
          <Button
              class="flex items-center gap-2"
              size="sm"
              variant="outline"
              @click="adicionarContato"
          >
            <Plus class="h-4 w-4"/>
            Adicionar Contato de Emergência
          </Button>
        </div>

        <div v-else-if="contatos.fields.length === 0"
             class="flex items-center justify-center border border-dashed rounded-lg min-h-[70px] bg-gray-50"
        >
           <span class="text-gray-500 text-sm italic">
              Nenhum contato de emergência cadastrado.
            </span>
        </div>
      </div>
    </div>

    <div>
      <div class="flex items-center justify-between border-b pb-2 mb-4">
        <h3 class="text-gray-900 font-medium text-lg flex items-center gap-2">
          <AlertCircle class="h-5 w-5"/>
          Observações Clínicas
        </h3>
      </div>
      <Textarea
          v-model="fields.observacoesClinicas.value"
          :class="[{'border-transparent bg-transparent shadow-none px-0 resize-none': !modoEdicao}]"
          :disabled="!modoEdicao"
          class="mt-1 min-h-[50px] disabled:opacity-100 disabled:cursor-default transition-all"
          placeholder="Registre alergias e observações importantes..."
          v-bind="fields.observacoesClinicasProps.value"
      />
    </div>
  </CardContent>
</template>
