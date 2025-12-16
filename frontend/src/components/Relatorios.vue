<script lang="ts" setup>
import {computed, ref} from 'vue'
import {useAppStore} from '@/stores/app'
import {useAuthStore} from '@/stores/auth'
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import {ChevronDown, ClipboardList, Download} from 'lucide-vue-next'

const appStore = useAppStore()
const authStore = useAuthStore()

const tipoRelatorio = ref(authStore.user?.role === 'farmacia' ? 'medicamentos-farmacia' : 'fim-plantao')
const periodoTipo = ref<'dia' | 'mes'>('dia')
const diaSelecionado = ref(new Date().toISOString().split('T')[0])

const mesSelecionado = ref(String(new Date().getMonth() + 1))
const anoSelecionado = ref(String(new Date().getFullYear()))

const dataInicio = ref(new Date().toISOString().split('T')[0])
const dataFim = ref(new Date().toISOString().split('T')[0])

const meses = [
  {value: '1', label: 'Janeiro'}, {value: '2', label: 'Fevereiro'}, {value: '3', label: 'Março'},
  {value: '4', label: 'Abril'}, {value: '5', label: 'Maio'}, {value: '6', label: 'Junho'},
  {value: '7', label: 'Julho'}, {value: '8', label: 'Agosto'}, {value: '9', label: 'Setembro'},
  {value: '10', label: 'Outubro'}, {value: '11', label: 'Novembro'}, {value: '12', label: 'Dezembro'}
]

const opcoesRelatorio = computed(() => {
  const role = authStore.user?.role
  if (role === 'farmacia') {
    return [{value: 'medicamentos-farmacia', label: 'Medicamentos (Farmácia)'}]
  }
  return [
    {value: 'fim-plantao', label: 'Fim de Plantão'},
    {value: 'medicamentos-farmacia', label: 'Medicamentos (Farmácia)'},
    {value: 'ocupacao-clinica', label: 'Ocupação Clínica'},
    {value: 'absenteismo', label: 'Absenteísmo'}
  ]
})

const usaRangeDatas = computed(() =>
    ['ocupacao-clinica', 'absenteismo'].includes(tipoRelatorio.value)
)

const getPaciente = (id: string) => appStore.getPacienteById(id)
const getProtocolo = (id?: string) => id ? appStore.getProtocoloById(id) : null

const formatarStatus = (slug: string) => {
  return appStore.getStatusConfig(slug).label
}

const dadosRelatorio = computed(() => {
  const mesFormatado = `${anoSelecionado.value}-${mesSelecionado.value.padStart(2, '0')}`

  let agendamentosBase = []
  if (periodoTipo.value === 'dia') {
    agendamentosBase = appStore.agendamentos.filter(a => a.data === diaSelecionado.value)
  } else {
    agendamentosBase = appStore.agendamentos.filter(a => a.data.startsWith(mesFormatado))
  }

  if (tipoRelatorio.value === 'fim-plantao') {
    const censo = {
      agendados: agendamentosBase.length,
      atendidos: agendamentosBase.filter(a => a.status === 'concluido').length,
      remarcados: 0,
      internados: 0,
      extra: 0
    }
    const gruposProtocolo = {ate2h: 0, de2a4h: 0, acima4h: 0, hormonioterapias: 0, imunoterapias: 0, zometa: 0}
    const intercorrencias = {
      suspensoes: agendamentosBase.filter(a => a.status === 'suspenso').length,
      reacoes: 0,
      extravasamentos: 0,
      derramamentos: 0,
      motivos: {} as Record<string, number>
    }

    agendamentosBase.forEach(a => {
      const p = getPaciente(a.pacienteId)
      const prot = getProtocolo(p?.protocoloId)

      if (prot) {
        if (prot.duracao < 120) gruposProtocolo.ate2h++
        else if (prot.duracao <= 240) gruposProtocolo.de2a4h++
        else gruposProtocolo.acima4h++

        const nome = prot.nome.toLowerCase()
        const meds = prot.medicamentos.map(m => m.nome.toLowerCase())

        if (nome.includes('faslodex') || nome.includes('eligard')) gruposProtocolo.hormonioterapias++
        if (meds.some(m => m.includes('mab'))) gruposProtocolo.imunoterapias++
        if (meds.some(m => m.includes('zometa'))) gruposProtocolo.zometa++
      }
      if (a.observacoes?.toLowerCase().includes('reação')) intercorrencias.reacoes++
      if (a.status === 'suspenso') {
        const motivo = a.observacoes || 'Não especificado'
        intercorrencias.motivos[motivo] = (intercorrencias.motivos[motivo] || 0) + 1
      }
    })

    return {
      type: 'complex',
      periodo: periodoTipo.value === 'dia' ? new Date(diaSelecionado.value).toLocaleDateString('pt-BR') : mesFormatado,
      horarios: {inicio: '07:00', fim: '19:00'},
      censo,
      gruposProtocolo,
      intercorrencias
    }
  }

  if (tipoRelatorio.value === 'medicamentos-farmacia') {
    const meds: Record<string, { qtd: number, prots: Set<string> }> = {}
    let totalEnviadas = 0
    let totalAusencia = 0

    agendamentosBase.forEach(a => {
      if (a.statusFarmacia === 'enviada') totalEnviadas++
      if (a.status === 'suspenso' && (a.observacoes?.toLowerCase().includes('ausência') || a.observacoes?.toLowerCase().includes('falta'))) {
        totalAusencia++
      }

      const p = getPaciente(a.pacienteId)
      const prot = getProtocolo(p?.protocoloId)
      if (prot) {
        prot.medicamentos.forEach(m => {
          const nomeMed = m.nome
          if (!meds[nomeMed]) meds[nomeMed] = {qtd: 0, prots: new Set()}
          meds[nomeMed].qtd++
          meds[nomeMed].prots.add(prot.nome)
        })
      }
    })

    const listaMeds = Object.entries(meds).map(([name, data]) => ({
      'Medicamento': name,
      'Qtd Total': data.qtd,
      'Protocolos': Array.from(data.prots).join(', ')
    }))

    return {
      type: 'farmacia',
      summary: {totalEnviadas, totalAusencia},
      data: listaMeds
    }
  }

  const inicio = new Date(dataInicio.value)
  const fim = new Date(dataFim.value)
  const filteredRange = appStore.agendamentos.filter(a => {
    const d = new Date(a.data)
    return d >= inicio && d <= fim
  })

  if (tipoRelatorio.value === 'ocupacao-clinica') {
    const agg: Record<string, any> = {}
    filteredRange.forEach(a => {
      const key = `${a.data}-${a.turno}`
      if (!agg[key]) agg[key] = {data: a.data, turno: a.turno, count: 0}
      agg[key].count++
    })
    return Object.values(agg).map(d => ({
      'Data': new Date(d.data).toLocaleDateString('pt-BR'),
      'Turno': d.turno,
      'Agendados': d.count,
      'Capacidade': 16,
      'Ocupação': `${Math.round((d.count / 16) * 100)}%`
    }))
  }

  if (tipoRelatorio.value === 'absenteismo') {
    return filteredRange
        .filter(a => a.status === 'suspenso' || a.status === 'intercorrencia' || a.status === 'ausente')
        .map(a => ({
          'Data': new Date(a.data).toLocaleDateString('pt-BR'),
          'Paciente': getPaciente(a.pacienteId)?.nome || '-',
          'Motivo': a.observacoes || 'Não informado',
          'Status': formatarStatus(a.status)
        }))
  }

  return []
})

const colunas = computed(() => {
  const data = dadosRelatorio.value
  if ((data as any).type === 'farmacia') {
    return Object.keys((data as any).data[0] || {})
  }
  if (Array.isArray(data) && data.length > 0) {
    return Object.keys(data[0])
  }
  return []
})
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Relatórios</h1>
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <ClipboardList class="h-6 w-6"/>
          Relatórios Gerenciais
        </CardTitle>
      </CardHeader>
      <CardContent class="space-y-4">
        <div>
          <Label>Tipo de Relatório</Label>
          <div class="relative">
            <select
                v-model="tipoRelatorio"
                class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
            >
              <option v-for="op in opcoesRelatorio" :key="op.value" :value="op.value">
                {{ op.label }}
              </option>
            </select>
            <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <template v-if="!usaRangeDatas">
            <div>
              <Label>Período</Label>
              <div class="relative">
                <select
                    v-model="periodoTipo"
                    class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
                >
                  <option value="dia">Dia Específico</option>
                  <option value="mes">Mês Específico</option>
                </select>
                <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
              </div>
            </div>

            <div v-if="periodoTipo === 'dia'">
              <Label>Data</Label>
              <Input v-model="diaSelecionado" type="date"/>
            </div>

            <div v-else class="grid grid-cols-2 gap-2">
              <div class="flex flex-col gap-1.5">
                <Label>Mês</Label>
                <div class="relative">
                  <select
                      v-model="mesSelecionado"
                      class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
                  >
                    <option v-for="mes in meses" :key="mes.value" :value="mes.value">
                      {{ mes.label }}
                    </option>
                  </select>
                  <ChevronDown class="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
                </div>
              </div>
              <div>
                <Label>Ano</Label>
                <Input v-model="anoSelecionado" type="number"/>
              </div>
            </div>
          </template>

          <template v-else>
            <div><Label>Data Início</Label><Input v-model="dataInicio" type="date"/></div>
            <div><Label>Data Fim</Label><Input v-model="dataFim" type="date"/></div>
          </template>
        </div>
      </CardContent>
    </Card>

    <div v-if="(dadosRelatorio as any).type === 'farmacia'">
      <div class="grid grid-cols-2 gap-4 mb-4">
        <Card class="bg-blue-50 border-blue-200">
          <CardContent class="pt-6">
            <p class="text-sm text-blue-700 font-medium">Total de Medicações Enviadas</p>
            <p class="text-3xl font-bold text-blue-900">{{ (dadosRelatorio as any).summary.totalEnviadas }}</p>
          </CardContent>
        </Card>
        <Card class="bg-red-50 border-red-200">
          <CardContent class="pt-6">
            <p class="text-sm text-red-700 font-medium">Não Preparadas (Ausência)</p>
            <p class="text-3xl font-bold text-red-900">{{ (dadosRelatorio as any).summary.totalAusencia }}</p>
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
              <TableRow v-for="(row, i) in (dadosRelatorio as any).data" :key="i">
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

    <div v-else-if="(dadosRelatorio as any).type === 'complex'">
      <Card>
        <CardHeader>
          <CardTitle>Relatório de Fim de Plantão - {{ (dadosRelatorio as any).periodo }}</CardTitle>
        </CardHeader>
        <CardContent class="space-y-6">
          <div class="grid grid-cols-5 gap-3">
            <Card class="bg-blue-50">
              <CardContent class="pt-4"><p class="text-xs">Agendados</p>
                <p class="text-2xl">{{ (dadosRelatorio as any).censo.agendados }}</p></CardContent>
            </Card>
            <Card class="bg-green-50">
              <CardContent class="pt-4"><p class="text-xs">Atendidos</p>
                <p class="text-2xl">{{ (dadosRelatorio as any).censo.atendidos }}</p></CardContent>
            </Card>
            <Card class="bg-yellow-50">
              <CardContent class="pt-4"><p class="text-xs">Remarcados</p>
                <p class="text-2xl">{{ (dadosRelatorio as any).censo.remarcados }}</p></CardContent>
            </Card>
            <Card class="bg-purple-50">
              <CardContent class="pt-4"><p class="text-xs">Internados</p>
                <p class="text-2xl">{{ (dadosRelatorio as any).censo.internados }}</p></CardContent>
            </Card>
            <Card class="bg-orange-50">
              <CardContent class="pt-4"><p class="text-xs">Extra</p>
                <p class="text-2xl">{{ (dadosRelatorio as any).censo.extra }}</p></CardContent>
            </Card>
          </div>

          <div>
            <h3 class="font-semibold mb-3">Grupos de Protocolo</h3>
            <div class="grid grid-cols-3 gap-3">
              <div class="bg-gray-50 rounded p-3"><p class="text-sm text-gray-600">Até 2h</p>
                <p class="text-xl">{{ (dadosRelatorio as any).gruposProtocolo.ate2h }}</p></div>
              <div class="bg-gray-50 rounded p-3"><p class="text-sm text-gray-600">2h a 4h</p>
                <p class="text-xl">{{ (dadosRelatorio as any).gruposProtocolo.de2a4h }}</p></div>
              <div class="bg-gray-50 rounded p-3"><p class="text-sm text-gray-600">> 4h</p>
                <p class="text-xl">{{ (dadosRelatorio as any).gruposProtocolo.acima4h }}</p></div>
            </div>
          </div>

          <Button class="w-full" variant="outline">
            <Download class="h-4 w-4 mr-2"/>
            Exportar PDF
          </Button>
        </CardContent>
      </Card>
    </div>

    <Card v-else-if="Array.isArray(dadosRelatorio) && dadosRelatorio.length > 0">
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
            <TableRow v-for="(row, i) in dadosRelatorio" :key="i">
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

    <div v-else class="text-center text-gray-500 py-8">
      Nenhum dado encontrado para o período selecionado.
    </div>
  </div>
</template>
