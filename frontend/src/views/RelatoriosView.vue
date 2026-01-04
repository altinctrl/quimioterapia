<script lang="ts" setup>
import {computed, ref} from 'vue'
import {useAppStore} from '@/stores/app'
import {useAuthStore} from '@/stores/auth'
import RelatoriosFiltros from '@/components/relatorios/RelatoriosFiltros.vue'
import RelatoriosFarmacia from '@/components/relatorios/RelatoriosFarmacia.vue'
import RelatoriosFimPlantao from '@/components/relatorios/RelatoriosFimPlantao.vue'
import RelatoriosTabela from '@/components/relatorios/RelatoriosTabela.vue'

const appStore = useAppStore()
const authStore = useAuthStore()

const filtros = ref({
  tipoRelatorio: authStore.user?.role === 'farmacia' ? 'medicamentos-farmacia' : 'fim-plantao',
  periodoTipo: 'dia' as 'dia' | 'mes',
  diaSelecionado: new Date().toISOString().split('T')[0],
  mesSelecionado: String(new Date().getMonth() + 1),
  anoSelecionado: String(new Date().getFullYear()),
  dataInicio: new Date().toISOString().split('T')[0],
  dataFim: new Date().toISOString().split('T')[0]
})

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
    ['ocupacao-clinica', 'absenteismo'].includes(filtros.value.tipoRelatorio)
)

const getPaciente = (id: string) => appStore.getPacienteById(id)
const getProtocolo = (id?: string) => id ? appStore.getProtocoloById(id) : null

const formatarStatus = (slug: string) => {
  return appStore.getStatusConfig(slug).label
}

const dadosRelatorio = computed(() => {
  const {
    tipoRelatorio,
    periodoTipo,
    diaSelecionado,
    anoSelecionado,
    mesSelecionado,
    dataInicio,
    dataFim
  } = filtros.value
  const mesFormatado = `${anoSelecionado}-${mesSelecionado.padStart(2, '0')}`

  let agendamentosBase = []
  if (periodoTipo === 'dia') {
    agendamentosBase = appStore.agendamentos.filter(a => a.data === diaSelecionado)
  } else {
    agendamentosBase = appStore.agendamentos.filter(a => a.data.startsWith(mesFormatado))
  }

  if (tipoRelatorio === 'fim-plantao') {
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
      periodo: periodoTipo === 'dia' ? new Date(diaSelecionado).toLocaleDateString('pt-BR') : mesFormatado,
      horarios: {inicio: '07:00', fim: '19:00'},
      censo,
      gruposProtocolo,
      intercorrencias
    }
  }

  if (tipoRelatorio === 'medicamentos-farmacia') {
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

  const inicio = new Date(dataInicio)
  const fim = new Date(dataFim)
  const filteredRange = appStore.agendamentos.filter(a => {
    const d = new Date(a.data)
    return d >= inicio && d <= fim
  })

  if (tipoRelatorio === 'ocupacao-clinica') {
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

  if (tipoRelatorio === 'absenteismo') {
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
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Relatórios</h1>

    <RelatoriosFiltros
        :filtros="filtros"
        :opcoes-relatorio="opcoesRelatorio"
        :usa-range-datas="usaRangeDatas"
    />

    <template v-if="dadosRelatorio">

      <RelatoriosFarmacia
          v-if="(dadosRelatorio as any).type === 'farmacia'"
          :dados="dadosRelatorio as any"
      />

      <RelatoriosFimPlantao
          v-else-if="(dadosRelatorio as any).type === 'complex'"
          :dados="dadosRelatorio as any"
      />

      <RelatoriosTabela
          v-else-if="Array.isArray(dadosRelatorio) && dadosRelatorio.length > 0"
          :dados="dadosRelatorio"
      />

      <div v-else class="text-center text-gray-500 py-8">
        Nenhum dado encontrado para o período selecionado.
      </div>

    </template>
  </div>
</template>