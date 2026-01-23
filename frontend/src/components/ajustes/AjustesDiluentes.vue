<script lang="ts" setup>
import {ref} from 'vue'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Label} from '@/components/ui/label'
import {Input} from '@/components/ui/input'
import {Button} from '@/components/ui/button'
import {toast} from 'vue-sonner'
import {Trash, Upload} from 'lucide-vue-next'

const props = defineProps<{
  diluentes: string[]
}>()

const emit = defineEmits(['update:diluentes'])
const novoDiluente = ref('')

const handleAdicionar = () => {
  const val = novoDiluente.value.trim()
  if (val && !props.diluentes.includes(val)) {
    const novaLista = [...props.diluentes, val].sort((a, b) => a.localeCompare(b))
    emit('update:diluentes', novaLista)
    novoDiluente.value = ''
  }
}

const handleRemover = (item: string) => {
  emit('update:diluentes', props.diluentes.filter(d => d !== item))
}

const handleImportarCsv = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result as string
    if (!text) return
    const linhas = text.split(/\r\n|\n/).map(l => l.trim()).filter(l => l.length > 0)

    const listaAtualizada = [...props.diluentes]
    let adicionados = 0

    linhas.forEach(linha => {
      if (!listaAtualizada.includes(linha)) {
        listaAtualizada.push(linha)
        adicionados++
      }
    })

    listaAtualizada.sort((a, b) => a.localeCompare(b))
    emit('update:diluentes', listaAtualizada)
    toast.success(`${adicionados} diluentes importados com sucesso.`)
    ;(event.target as HTMLInputElement).value = ''
  }
  reader.readAsText(file)
}
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center justify-between">
        <div>
          <CardTitle>Opções de Diluição</CardTitle>
          <CardDescription>Gerencie a lista de diluentes disponíveis para protocolos.</CardDescription>
        </div>
        <div>
          <Label class="cursor-pointer" for="csv-upload">
            <div
                class="flex items-center gap-2 text-sm bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-md transition-colors">
              <Upload class="h-4 w-4"/>
              Importar CSV
            </div>
          </Label>
          <input id="csv-upload" accept=".csv,.txt" class="hidden" type="file" @change="handleImportarCsv"/>
        </div>
      </div>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="flex gap-2">
        <Input v-model="novoDiluente" placeholder="Ex: Soro Fisiológico 0,9% 100ml" @keyup.enter="handleAdicionar"/>
        <Button variant="secondary" @click="handleAdicionar">Adicionar</Button>
      </div>

      <div class="border rounded-md divide-y">
        <div v-if="diluentes.length === 0" class="p-4 text-center text-muted-foreground text-sm">
          Nenhum diluente cadastrado.
        </div>
        <div v-for="item in diluentes" :key="item"
             class="flex items-center justify-between px-3 py-1 hover:bg-slate-50 text-sm">
          <span>{{ item }}</span>
          <Button class="h-8 w-8 text-red-500 hover:bg-red-50 hover:text-red-500" size="icon" variant="ghost"
                  @click="handleRemover(item)">
            <Trash class="h-4 w-4"/>
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
