<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useAppStore} from '@/stores/app'
import {useAuthStore} from '@/stores/auth'
import RelatoriosFiltros from '@/components/relatorios/RelatoriosFiltros.vue'
import RelatoriosFarmacia from '@/components/relatorios/RelatoriosFarmacia.vue'
import RelatoriosFimPlantao from '@/components/relatorios/RelatoriosFimPlantao.vue'
import RelatoriosTabela from '@/components/relatorios/RelatoriosTabela.vue'
import {getDataLocal} from '@/lib/utils.ts';

const appStore = useAppStore()
const authStore = useAuthStore()

const filtros = ref({
  tipoRelatorio: authStore.user?.role === 'farmacia' ? 'medicamentos-farmacia' : 'fim-plantao',
  periodoTipo: 'dia' as 'dia' | 'mes',
  diaSelecionado: getDataLocal(),
  mesSelecionado: String(new Date().getMonth() + 1),
  anoSelecionado: String(new Date().getFullYear()),
  dataInicio: getDataLocal(),
  dataFim: getDataLocal()
})

watch(() => [
  filtros.value.tipoRelatorio,
  filtros.value.periodoTipo,
  filtros.value.diaSelecionado,
  filtros.value.mesSelecionado,
  filtros.value.anoSelecionado,
  filtros.value.dataInicio,
  filtros.value.dataFim
], async () => {
  let inicio = filtros.value.diaSelecionado
  let fim = filtros.value.diaSelecionado

  if (filtros.value.tipoRelatorio === 'ocupacao-clinica' || filtros.value.tipoRelatorio === 'absenteismo') {
    inicio = filtros.value.dataInicio
    fim = filtros.value.dataFim
  } else if (filtros.value.periodoTipo === 'mes') {
    const y = parseInt(filtros.value.anoSelecionado)
    const m = parseInt(filtros.value.mesSelecionado)
    inicio = `${y}-${m.toString().padStart(2, '0')}-01`
    const lastDay = new Date(y, m, 0).getDate()
    fim = `${y}-${m.toString().padStart(2, '0')}-${lastDay}`
  }

  await appStore.fetchAgendamentos(inicio, fim)

  const uniquePacientes = [...new Set(appStore.agendamentos.map(a => a.pacienteId))]
  if (uniquePacientes.length > 0) {
    await Promise.all(uniquePacientes.map(id => appStore.fetchPrescricoes(id)))
  }
}, {immediate: true, deep: true})

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

const formatarStatus = (slug: string) => {
  return appStore.getStatusConfig(slug).label
}

const formatarDataLocal = (dataIso: string) => {
  if (!dataIso) return '-'
  return dataIso.split('-').reverse().join('/')
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
  if (['ocupacao-clinica', 'absenteismo'].includes(tipoRelatorio)) {
     const inicioDt = new Date(dataInicio + 'T00:00:00')
     const fimDt = new Date(dataFim + 'T23:59:59')
     agendamentosBase = appStore.agendamentos.filter(a => {
        const d = new Date(a.data + 'T12:00:00')
        return d >= inicioDt && d <= fimDt
     })
  } else if (periodoTipo === 'dia') {
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
      const prot = appStore.getProtocoloPeloHistorico(a.pacienteId)

      if (prot) {
        if (prot.duracao < 120) gruposProtocolo.ate2h++
        else if (prot.duracao <= 240) gruposProtocolo.de2a4h++
        else gruposProtocolo.acima4h++

        const nome = prot.nome.toLowerCase()
        const meds = prot.medicamentos ? prot.medicamentos.map(m => m.nome.toLowerCase()) : []

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
      periodo: periodoTipo === 'dia' ? formatarDataLocal(diaSelecionado) : mesFormatado,
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
      if (a.tipo !== 'infusao') return

      const statusFarmacia = a.detalhes?.infusao?.status_farmacia
      if (statusFarmacia === 'enviada') totalEnviadas++

      if (a.status === 'suspenso' && (a.observacoes?.toLowerCase().includes('ausência') || a.observacoes?.toLowerCase().includes('falta'))) {
        totalAusencia++
      }

      const prot = appStore.getProtocoloPeloHistorico(a.pacienteId)
      if (prot && prot.medicamentos) {
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