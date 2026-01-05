<script lang="ts" setup>
import {computed, ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Badge} from '@/components/ui/badge'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog'
import {Checkbox} from '@/components/ui/checkbox'
import {ArrowLeft, Ban, Beaker, CheckCircle2, Clock, Edit, Eye, Plus, Search, Trash2, XCircle} from 'lucide-vue-next'
import type {ItemProtocolo} from '@/types'
import {toast} from 'vue-sonner'

const router = useRouter()
const appStore = useAppStore()

const searchTerm = ref('')
const statusFilter = ref<'todos' | 'ativos' | 'inativos'>('todos')
const restricaoDiaFilter = ref<'todos' | 'com' | 'sem'>('todos')
const grupoInfusaoFilter = ref<'todos' | 'rapido' | 'medio' | 'longo'>('todos')

const dialogOpen = ref(false)
const detailsOpen = ref(false)
const editMode = ref(false)
const selectedProtocolo = ref<any>(null)

const diasSemanaOptions = [
  {value: 1, label: 'Segunda'},
  {value: 2, label: 'Terça'},
  {value: 3, label: 'Quarta'},
  {value: 4, label: 'Quinta'},
  {value: 5, label: 'Sexta'}
]

const formData = ref({
  nome: '',
  descricao: '',
  indicacao: '',
  duracao: 0,
  frequencia: '',
  numeroCiclos: 0,
  medicamentos: [] as ItemProtocolo[],
  preMedicacoes: [] as ItemProtocolo[],
  posMedicacoes: [] as ItemProtocolo[],
  observacoes: '',
  precaucoes: '',
  ativo: true,
  diasSemanaPermitidos: [] as number[]
})

const filteredProtocolos = computed(() => {
  return appStore.protocolos.filter(p => {
    const matchesSearch = p.nome.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
        p.indicacao.toLowerCase().includes(searchTerm.value.toLowerCase())
    if (!matchesSearch) return false

    if (statusFilter.value === 'ativos' && !p.ativo) return false
    if (statusFilter.value === 'inativos' && p.ativo) return false

    const temRestricao = p.diasSemanaPermitidos && p.diasSemanaPermitidos.length > 0
    if (restricaoDiaFilter.value === 'com' && !temRestricao) return false
    if (restricaoDiaFilter.value === 'sem' && temRestricao) return false

    let grupo = p.grupoInfusao
    if (!grupo) {
      if (p.duracao < 120) grupo = 'rapido'
      else if (p.duracao <= 240) grupo = 'medio'
      else grupo = 'longo'
    }
    return !(grupoInfusaoFilter.value !== 'todos' && grupo !== grupoInfusaoFilter.value);
  })
})

const unidadesOptions = ['mg/m²', 'mg/kg', 'mg', 'g', 'mcg', 'UI', 'AUC', 'ml']

const addItem = (lista: 'pre' | 'qt' | 'pos') => {
  const novoItem: ItemProtocolo = {nome: '', dosePadrao: '', unidadePadrao: 'mg/m²', viaPadrao: 'IV'}
  if (lista === 'pre') formData.value.preMedicacoes.push(novoItem)
  else if (lista === 'qt') formData.value.medicamentos.push(novoItem)
  else formData.value.posMedicacoes.push(novoItem)
}

const removeItem = (lista: 'pre' | 'qt' | 'pos', index: number) => {
  if (lista === 'pre') formData.value.preMedicacoes.splice(index, 1)
  else if (lista === 'qt') formData.value.medicamentos.splice(index, 1)
  else formData.value.posMedicacoes.splice(index, 1)
}

const resetForm = () => {
  formData.value = {
    nome: '', descricao: '', indicacao: '', duracao: 0,
    frequencia: '', numeroCiclos: 0,
    medicamentos: [],
    preMedicacoes: [],
    posMedicacoes: [],
    observacoes: '', precaucoes: '', ativo: true,
    diasSemanaPermitidos: []
  }
  selectedProtocolo.value = null
  editMode.value = false
}

const handleAdd = () => {
  resetForm()
  dialogOpen.value = true
}

const handleEdit = (p: any) => {
  selectedProtocolo.value = p
  formData.value = {
    nome: p.nome,
    descricao: p.descricao || '',
    indicacao: p.indicacao,
    duracao: p.duracao,
    frequencia: p.frequencia,
    numeroCiclos: p.numeroCiclos,
    medicamentos: p.medicamentos ? JSON.parse(JSON.stringify(p.medicamentos)) : [],
    preMedicacoes: p.preMedicacoes ? JSON.parse(JSON.stringify(p.preMedicacoes)) : [],
    posMedicacoes: p.posMedicacoes ? JSON.parse(JSON.stringify(p.posMedicacoes)) : [],
    observacoes: p.observacoes || '',
    precaucoes: p.precaucoes || '',
    ativo: p.ativo,
    diasSemanaPermitidos: Array.isArray(p.diasSemanaPermitidos) ? [...p.diasSemanaPermitidos] : []
  }

  editMode.value = true
  dialogOpen.value = true
}

const handleViewDetails = (p: any) => {
  selectedProtocolo.value = p
  detailsOpen.value = true
}

const handleToggleStatus = async (p: any) => {
  try {
    if (p.ativo) {
      await appStore.desativarProtocolo(p.id)
      toast.success('Protocolo desativado')
    } else {
      await appStore.atualizarProtocolo(p.id, {ativo: true})
      toast.success('Protocolo reativado')
    }
  } catch (error) {
    console.error(error)
  }
}

const toggleDia = (dia: number, isChecked: boolean) => {
  let current = formData.value.diasSemanaPermitidos || []

  if (isChecked) {
    if (!current.includes(dia)) {
      current.push(dia)
    }
  } else {
    current = current.filter(d => d !== dia)
  }

  formData.value.diasSemanaPermitidos = current.sort((a, b) => a - b)
}

const inferirGrupoInfusao = (duracao: number): 'rapido' | 'medio' | 'longo' => {
  if (duracao < 120) return 'rapido'
  if (duracao <= 240) return 'medio'
  return 'longo'
}

const handleSubmit = async () => {
  const grupoInfusao = inferirGrupoInfusao(formData.value.duracao)
  const data = {...formData.value, grupoInfusao}

  try {
    if (editMode && selectedProtocolo.value) {
      await appStore.atualizarProtocolo(selectedProtocolo.value.id, data)
      toast.success('Protocolo atualizado')
    } else {
      await appStore.adicionarProtocolo(data)
      toast.success('Protocolo criado')
    }
    dialogOpen.value = false
  } catch (error) {
    console.error(error)
  }
}
</script>

<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button size="icon" variant="outline" @click="router.back()">
          <ArrowLeft class="h-4 w-4"/>
        </Button>
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Protocolos</h1>
        </div>
      </div>
      <Button @click="handleAdd">
        <Plus class="h-4 w-4 mr-2"/>
        Novo Protocolo
      </Button>
    </div>

    <Card>
      <CardContent class="pt-6 space-y-4">
        <div class="relative w-full">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"/>
          <Input v-model="searchTerm" class="pl-10" placeholder="Buscar por nome ou indicação..."/>
        </div>

        <div class="flex flex-wrap gap-4">
          <div class="flex items-center gap-2">
            <Label class="whitespace-nowrap">Status:</Label>
            <div class="flex gap-1">
              <Button :variant="statusFilter === 'todos' ? 'default' : 'outline'" size="sm"
                      @click="statusFilter = 'todos'">Todos
              </Button>
              <Button :variant="statusFilter === 'ativos' ? 'default' : 'outline'" size="sm"
                      @click="statusFilter = 'ativos'">Ativos
              </Button>
              <Button :variant="statusFilter === 'inativos' ? 'default' : 'outline'" size="sm"
                      @click="statusFilter = 'inativos'">Inativos
              </Button>
            </div>
          </div>

          <div class="h-8 w-px bg-gray-200 mx-2 hidden md:block"></div>

          <div class="flex items-center gap-2">
            <Label class="whitespace-nowrap">Restrição:</Label>
            <div class="flex gap-1">
              <Button :variant="restricaoDiaFilter === 'todos' ? 'default' : 'outline'" size="sm"
                      @click="restricaoDiaFilter = 'todos'">Todos
              </Button>
              <Button :variant="restricaoDiaFilter === 'com' ? 'default' : 'outline'" size="sm"
                      @click="restricaoDiaFilter = 'com'">Com
              </Button>
              <Button :variant="restricaoDiaFilter === 'sem' ? 'default' : 'outline'" size="sm"
                      @click="restricaoDiaFilter = 'sem'">Sem
              </Button>
            </div>
          </div>

          <div class="h-8 w-px bg-gray-200 mx-2 hidden md:block"></div>

          <div class="flex items-center gap-2">
            <Label class="whitespace-nowrap">Tempo:</Label>
            <div class="flex gap-1">
              <Button :variant="grupoInfusaoFilter === 'todos' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'todos'">Todos
              </Button>
              <Button :variant="grupoInfusaoFilter === 'rapido' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'rapido'">&lt; 2h
              </Button>
              <Button :variant="grupoInfusaoFilter === 'medio' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'medio'">2-4h
              </Button>
              <Button :variant="grupoInfusaoFilter === 'longo' ? 'default' : 'outline'" size="sm"
                      @click="grupoInfusaoFilter = 'longo'">&gt; 4h
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card v-for="p in filteredProtocolos" :key="p.id" :class="!p.ativo ? 'opacity-70 bg-gray-50' : ''">
        <CardHeader class="p-5 pb-3">
          <div class="flex justify-between items-start gap-4">
            <div class="overflow-hidden">
              <CardTitle :title="p.nome" class="flex items-center gap-2 text-lg"> {{ p.nome }}
                <CheckCircle2 v-if="p.ativo" class="h-4 w-4 text-green-600 flex-shrink-0"/>
                <XCircle v-else class="h-4 w-4 text-gray-400 flex-shrink-0"/>
              </CardTitle>
              <CardDescription :title="p.indicacao" class="text-sm mt-1">{{ p.indicacao }}</CardDescription>
            </div>

            <div class="flex gap-1 flex-shrink-0">
              <Button class="h-8 w-8" size="icon" variant="ghost" @click="handleViewDetails(p)">
                <Eye class="h-4 w-4"/>
              </Button>
              <Button class="h-8 w-8" size="icon" variant="ghost" @click="handleEdit(p)">
                <Edit class="h-4 w-4"/>
              </Button>
              <Button class="h-8 w-8 text-orange-500 hover:text-orange-600 hover:bg-orange-50" size="icon"
                      title="Desativar/Ativar"
                      variant="ghost" @click="handleToggleStatus(p)">
                <Ban class="h-4 w-4"/>
              </Button>
            </div>

          </div>
        </CardHeader>

        <CardContent class="p-5 pt-0 space-y-3">
          <div class="flex items-center gap-4 text-sm text-gray-600 mt-2">
            <div class="flex items-center gap-1">
              <Clock class="h-4 w-4"/>
              {{ p.duracao }} min
            </div>
            <div class="flex items-center gap-1">
              <Beaker class="h-4 w-4"/>
              {{ p.medicamentos.length }} meds
            </div>
          </div>

          <div v-if="p.diasSemanaPermitidos && p.diasSemanaPermitidos.length > 0"
               class="text-xs text-orange-600 font-medium">
            Restrito: {{
              p.diasSemanaPermitidos.map((d: number) => diasSemanaOptions.find(o => o.value === d)?.label).join(', ')
            }}
          </div>

          <div class="flex flex-wrap gap-1.5 h-14 overflow-hidden content-start">
            <Badge v-for="(m, idx) in p.medicamentos.slice(0, 4)" :key="idx" class="px-2 py-0.5" variant="secondary">
              {{ m.nome }}
            </Badge>
            <span v-if="p.medicamentos.length > 4" class="text-xs text-gray-500 self-center font-medium pl-1">
              +{{ p.medicamentos.length - 4 }}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>

    <Dialog v-model:open="dialogOpen">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{{ editMode ? 'Editar' : 'Novo' }} Protocolo</DialogTitle>
        </DialogHeader>

        <div class="space-y-6 py-4">

          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <Label>Nome</Label>
              <Input v-model="formData.nome" placeholder="Ex: FOLFOX"/>
            </div>

            <div class="col-span-2">
              <Label>Descrição</Label>
              <Input v-model="formData.descricao"/>
            </div>

            <div>
              <Label>Indicação</Label>
              <Input v-model="formData.indicacao" placeholder="Ex: CA Colorretal"/>
            </div>

            <div>
              <Label>Duração (min)</Label>
              <Input v-model="formData.duracao" type="number"/>
              <p class="text-[10px] text-gray-500 mt-1">
                Grupo inferido:
                <span v-if="formData.duracao < 120" class="text-green-600 font-medium">Rápido</span>
                <span v-else-if="formData.duracao <= 240" class="text-blue-600 font-medium">Médio</span>
                <span v-else class="text-purple-600 font-medium">Longo</span>
              </p>
            </div>

            <div>
              <Label>Frequência</Label>
              <Input v-model="formData.frequencia" placeholder="Ex: 14 dias"/>
            </div>

            <div>
              <Label>Número de Ciclos</Label>
              <Input v-model="formData.numeroCiclos" type="number"/>
            </div>

            <div class="col-span-2">
              <Label class="mb-2 block">Dias da Semana Permitidos</Label>
              <div class="col-span-2 border rounded-lg p-3 bg-gray-50">
                <div class="flex flex-wrap gap-4">
                  <div v-for="dia in diasSemanaOptions" :key="dia.value" class="flex items-center space-x-2">
                    <Checkbox
                        :id="`dia-${dia.value}`"
                        :checked="formData.diasSemanaPermitidos.includes(dia.value)"
                        @update:checked="(val) => toggleDia(dia.value, val)"
                    />
                    <Label :for="`dia-${dia.value}`" class="cursor-pointer">{{ dia.label }}</Label>
                  </div>
                </div>
                <p class="text-xs text-gray-500 mt-2">Deixe vazio para permitir todos os dias.</p>
              </div>
            </div>
          </div>

          <Separator/>

          <div class="space-y-6">

            <div>
              <div class="flex items-center justify-between mb-2">
                <Label>Pré-Medicação</Label>
                <Button size="sm" variant="outline" @click="addItem('pre')">
                  <Plus class="h-3 w-3 mr-1"/>
                  Adicionar
                </Button>
              </div>
              <div v-if="formData.preMedicacoes.length === 0"
                   class="text-sm text-gray-400 italic bg-gray-50 p-2 rounded text-center border border-blue-100">Nenhum
                item
              </div>
              <div v-else class="space-y-2 bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                <div v-for="(item, idx) in formData.preMedicacoes" :key="idx" class="flex gap-2 items-center">
                  <Input v-model="item.nome" class="flex-grow" placeholder="Nome"/>
                  <Input v-model="item.dosePadrao" class="w-20 bg-white" placeholder="Dose"/>

                  <div class="w-24">
                    <Select v-model="item.unidadePadrao">
                      <SelectTrigger class="bg-white">
                        <SelectValue/>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem v-for="u in unidadesOptions" :key="u" :value="u">{{ u }}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Select v-model="item.viaPadrao">
                    <SelectTrigger class="w-24">
                      <SelectValue placeholder="Via"/>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="IV">IV</SelectItem>
                      <SelectItem value="VO">VO</SelectItem>
                      <SelectItem value="SC">SC</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button class="text-red-500" size="icon" variant="ghost" @click="removeItem('pre', idx)">
                    <Trash2 class="h-4 w-4"/>
                  </Button>
                </div>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <Label>Quimioterapia</Label>
                <Button size="sm" variant="outline" @click="addItem('qt')">
                  <Plus class="h-3 w-3 mr-1"/>
                  Adicionar
                </Button>
              </div>
              <div v-if="formData.medicamentos.length === 0"
                   class="text-sm text-gray-400 italic bg-gray-50 p-2 rounded text-center border border-blue-100">Nenhum
                item
              </div>
              <div v-else class="space-y-2 bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                <div v-for="(item, idx) in formData.medicamentos" :key="idx" class="flex gap-2 items-center">
                  <Input v-model="item.nome" class="flex-grow bg-white" placeholder="Nome do Medicamento"/>
                  <Input v-model="item.dosePadrao" class="w-20 bg-white" placeholder="Dose"/>

                  <div class="w-24">
                    <Select v-model="item.unidadePadrao">
                      <SelectTrigger class="bg-white">
                        <SelectValue/>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem v-for="u in unidadesOptions" :key="u" :value="u">{{ u }}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Select v-model="item.viaPadrao">
                    <SelectTrigger class="w-24 bg-white">
                      <SelectValue/>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="IV">IV</SelectItem>
                      <SelectItem value="SC">SC</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button class="text-red-500" size="icon" variant="ghost" @click="removeItem('qt', idx)">
                    <Trash2 class="h-4 w-4"/>
                  </Button>
                </div>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <Label>Pós-Medicação</Label>
                <Button size="sm" variant="outline" @click="addItem('pos')">
                  <Plus class="h-3 w-3 mr-1"/>
                  Adicionar
                </Button>
              </div>
              <div v-if="formData.posMedicacoes.length === 0"
                   class="text-sm text-gray-400 italic bg-gray-50 p-2 rounded text-center border border-blue-100">Nenhum
                item
              </div>
              <div v-else class="space-y-2 bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                <div v-for="(item, idx) in formData.posMedicacoes" :key="idx" class="flex gap-2 items-center">
                  <Input v-model="item.nome" class="flex-grow" placeholder="Nome"/>
                  <Input v-model="item.dosePadrao" class="w-20 bg-white" placeholder="Dose"/>

                  <div class="w-24">
                    <Select v-model="item.unidadePadrao">
                      <SelectTrigger class="bg-white">
                        <SelectValue/>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem v-for="u in unidadesOptions" :key="u" :value="u">{{ u }}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Select v-model="item.viaPadrao">
                    <SelectTrigger class="w-24">
                      <SelectValue/>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="IV">IV</SelectItem>
                      <SelectItem value="SC">SC</SelectItem>
                      <SelectItem value="VO">VO</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button class="text-red-500" size="icon" variant="ghost" @click="removeItem('pos', idx)">
                    <Trash2 class="h-4 w-4"/>
                  </Button>
                </div>
              </div>
            </div>

          </div>

          <Separator class="my-4"/>

          <div class="grid grid-cols-1 gap-4">
            <div>
              <Label>Observações</Label>
              <Textarea v-model="formData.observacoes" rows="2"/>
            </div>
            <div>
              <Label>Precauções</Label>
              <Textarea v-model="formData.precaucoes" rows="2"/>
            </div>
            <div class="flex items-center space-x-2">
              <Checkbox id="ativo" :checked="formData.ativo" @update:checked="formData.ativo = $event"/>
              <Label for="ativo">Protocolo Ativo</Label>
            </div>
          </div>

        </div>
        <DialogFooter>
          <Button variant="outline" @click="dialogOpen = false">Cancelar</Button>
          <Button @click="handleSubmit">Salvar Protocolo</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="detailsOpen">
      <DialogContent class="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{{ selectedProtocolo?.nome }}</DialogTitle>
          <DialogDescription>
            <span class="block font-medium text-foreground mb-1">{{ selectedProtocolo?.indicacao }}</span>
            <span v-if="selectedProtocolo?.descricao" class="block text-xs font-normal text-muted-foreground">
              {{ selectedProtocolo.descricao }}
            </span>
          </DialogDescription>
        </DialogHeader>

        <div v-if="selectedProtocolo" class="space-y-6">
          <div class="bg-gray-50 p-3 rounded-lg border text-sm space-y-3">
            <div class="grid grid-cols-4 gap-4">
              <div><span class="text-gray-500 block text-xs uppercase font-bold">Duração</span>
                {{ selectedProtocolo.duracao }} min
              </div>
              <div><span class="text-gray-500 block text-xs uppercase font-bold">Frequência</span>
                {{ selectedProtocolo.frequencia }}
              </div>
              <div><span class="text-gray-500 block text-xs uppercase font-bold">Ciclos</span>
                {{ selectedProtocolo.numeroCiclos }}
              </div>
              <div>
                <span class="text-gray-500 block text-xs uppercase font-bold">Grupo</span>
                <span class="capitalize">{{
                    selectedProtocolo.grupoInfusao || inferirGrupoInfusao(selectedProtocolo.duracao)
                  }}</span>
              </div>
            </div>

            <div v-if="selectedProtocolo.diasSemanaPermitidos?.length" class="pt-2 border-t border-gray-200">
              <span class="text-gray-500 text-xs uppercase font-bold mr-2">Dias Permitidos:</span>
              <span class="text-gray-700">
                {{
                  selectedProtocolo.diasSemanaPermitidos.map((d: number) => diasSemanaOptions.find(o => o.value === d)?.label).join(', ')
                }}
              </span>
            </div>
          </div>

          <div class="space-y-6">
            <div v-if="selectedProtocolo.preMedicacoes?.length">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Pré-Quimioterapia</h4>
              <ul class="space-y-2">
                <li v-for="(m, i) in selectedProtocolo.preMedicacoes" :key="i"
                    class="text-sm flex justify-between border-b border-gray-100 pb-2 last:border-0">
                  <span class="text-gray-700">{{ m.nome }}</span>
                  <span class="text-gray-500 font-medium text-xs">
                    {{ m.dosePadrao }} {{ m.unidadePadrao }} <span class="text-gray-300 mx-1">|</span> {{ m.viaPadrao }}
                  </span>
                </li>
              </ul>
            </div>

            <div v-if="selectedProtocolo.medicamentos?.length">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Quimioterapia</h4>
              <ul class="space-y-2">
                <li v-for="(m, i) in selectedProtocolo.medicamentos" :key="i"
                    class="text-sm flex justify-between border-b border-gray-100 pb-2 last:border-0">
                  <span class="text-gray-700 font-medium">{{ m.nome }}</span>
                  <span class="text-gray-500 font-medium text-xs">
                    {{ m.dosePadrao }} {{ m.unidadePadrao }} <span class="text-gray-300 mx-1">|</span> {{ m.viaPadrao }}
                  </span>
                </li>
              </ul>
            </div>

            <div v-if="selectedProtocolo.posMedicacoes?.length">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Pós-Quimioterapia</h4>
              <ul class="space-y-2">
                <li v-for="(m, i) in selectedProtocolo.posMedicacoes" :key="i"
                    class="text-sm flex justify-between border-b border-gray-100 pb-2 last:border-0">
                  <span class="text-gray-700">{{ m.nome }}</span>
                  <span class="text-gray-500 font-medium text-xs">
                    {{ m.dosePadrao }} {{ m.unidadePadrao }} <span class="text-gray-300 mx-1">|</span> {{ m.viaPadrao }}
                  </span>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="selectedProtocolo.observacoes || selectedProtocolo.precaucoes" class="space-y-3 pt-4 border-t">
            <div v-if="selectedProtocolo.observacoes">
              <span class="text-xs font-bold text-gray-500 uppercase block mb-1">Observações</span>
              <p class="text-sm text-gray-700 bg-gray-50 p-2 rounded border">{{ selectedProtocolo.observacoes }}</p>
            </div>
            <div v-if="selectedProtocolo.precaucoes">
              <span class="text-xs font-bold text-red-600 uppercase block mb-1">Precauções</span>
              <p class="text-sm text-red-800 bg-red-50 p-2 rounded border border-red-100">
                {{ selectedProtocolo.precaucoes }}</p>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="detailsOpen = false">Fechar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
