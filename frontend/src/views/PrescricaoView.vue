<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAppStore} from '@/stores/app'
import {useEquipeStore} from '@/stores/equipe'
import {Button} from '@/components/ui/button'
import {Activity, ArrowLeft, Pill, RefreshCw, User} from 'lucide-vue-next'
import {toast} from 'vue-sonner'
import PrescricaoIdentificacao from '@/components/prescricao/PrescricaoIdentificacao.vue'
import PrescricaoProtocolo from '@/components/prescricao/PrescricaoProtocolo.vue'
import PrescricaoFooter from '@/components/prescricao/PrescricaoFooter.vue'
import PrescricaoBlocos from '@/components/prescricao/PrescricaoBlocos.vue'
import api from "@/services/api.ts";
import {Card} from "@/components/ui/card";

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const equipeStore = useEquipeStore()

const pacienteSelecionado = ref('')
const sexo = ref('')
const peso = ref('')
const altura = ref('')
const creatinina = ref('')
const diagnostico = ref('')
const protocoloNome = ref('')
const templateSelecionadoId = ref('')
const numeroCiclo = ref('1')
const blocosPrescricao = ref<any[]>([])
const prescricaoConcluida = ref(false)
const prescricaoAtualId = ref('')

const dadosPacienteCalculo = computed(() => {
  const p = parseFloat(peso.value) || 0
  const a = parseFloat(altura.value) || 0
  const c = parseFloat(creatinina.value) || 0
  const s = sexo.value
  const pacienteObj = appStore.pacientes.find(x => x.id === pacienteSelecionado.value)
  const idade = pacienteObj?.idade || 60
  const sc = (p && a) ? Math.sqrt((a * p) / 3600) : 0
  return {peso: p, altura: a, sc, creatinina: c, idade, sexo: s}
})

const templatesDisponiveis = computed(() => {
  const proto = appStore.protocolos.find(p => p.nome === protocoloNome.value)
  return proto?.templatesCiclo || []
})

watch(protocoloNome, (novoNome) => {
  if (!novoNome) {
    blocosPrescricao.value = []
    templateSelecionadoId.value = ''
    return
  }
  const proto = appStore.protocolos.find(p => p.nome === novoNome)
  if (proto && proto.templatesCiclo && proto.templatesCiclo.length > 0) {
    templateSelecionadoId.value = proto.templatesCiclo[0].idTemplate
  }
})

watch(templateSelecionadoId, (novoId) => {
  if (!novoId) return
  const template = templatesDisponiveis.value.find(t => t.idTemplate === novoId)
  if (template) {
    aplicarTemplate(template)
  }
})

const ultimaPrescricao = computed(() => {
  if (!pacienteSelecionado.value) return null
  const lista = appStore.getPrescricoesPorPaciente(pacienteSelecionado.value)
  if (!lista || lista.length === 0) return null

  return [...lista].sort((a, b) =>
      new Date(b.dataEmissao).getTime() - new Date(a.dataEmissao).getTime()
  )[0]
})

watch(pacienteSelecionado, async (novoId) => {
  if (novoId) {
    const p = appStore.getPacienteById(novoId)
    if (p) {
      sexo.value = p.sexo || ''
      peso.value = p.peso?.toString() || ''
      altura.value = p.altura?.toString() || ''
      creatinina.value = ''
    }
    await appStore.fetchPrescricoes(novoId)
  }
})

watch(protocoloNome, (novoNome) => {
  if (!novoNome) {
    blocosPrescricao.value = []
    return
  }
  carregarTemplatePadrao(novoNome)
})

const carregarTemplatePadrao = (nomeProto: string) => {
  const proto = appStore.protocolos.find(p => p.nome === nomeProto)
  if (!proto) return

  const template = proto.templatesCiclo?.[0]
  if (!template) {
    toast.error("Este protocolo não possui templates de infusão configurados.")
    return
  }

  aplicarTemplate(template)
}

const aplicarTemplate = (template: any) => {
  const blocosClonados = JSON.parse(JSON.stringify(template.blocos))

  blocosClonados.forEach((bloco: any) => {
    bloco.itens.forEach((item: any) => {
      if (item.tipo === 'medicamento_unico') {
        item.dados.percentualAjuste = 100
        item.dados.diluicaoFinal = item.dados.configuracaoDiluicao?.selecionada || ''
      } else if (item.tipo === 'grupo_alternativas') {
        item.selectedOptionIndex = null
        item.itemSelecionado = null
      }
    })
  })

  blocosPrescricao.value = blocosClonados
}

const repetirUltimaPrescricao = () => {
  if (!ultimaPrescricao.value) return

  const ultima = ultimaPrescricao.value
  protocoloNome.value = ultima.conteudo.protocolo.nome
  const proxCiclo = (ultima.conteudo.protocolo.cicloAtual + 1)

  const protoDef = appStore.protocolos.find(p => p.nome === protocoloNome.value)
  if (protoDef?.totalCiclos && proxCiclo > protoDef.totalCiclos) {
    toast.warning("O próximo ciclo sugerido excede o total previsto.")
  }

  numeroCiclo.value = protoDef?.totalCiclos === 0 ? '0' : proxCiclo.toString()

  if (ultima.conteudo.blocos) {
    const blocosRecuperados = JSON.parse(JSON.stringify(ultima.conteudo.blocos))

    blocosRecuperados.forEach((bloco: any) => {
      bloco.itens = bloco.itens.map((itemBackend: any) => ({
        tipo: 'medicamento_unico',
        dados: {
          ...itemBackend,
          percentualAjuste: itemBackend.percentualAjuste || 100,
          configuracaoDiluicao: buscarConfiguracaoDiluicaoOriginal(itemBackend.medicamento)
        }
      }))
    })

    blocosPrescricao.value = blocosRecuperados
  } else {
    toast.error("Erro ao ler dados da prescrição anterior.")
  }
}

const buscarConfiguracaoDiluicaoOriginal = (nomeMedicamento: string) => {
  const proto = appStore.protocolos.find(p => p.nome === protocoloNome.value)
  if (!proto) return null
  for (const t of proto.templatesCiclo) {
    for (const b of t.blocos) {
      for (const item of b.itens) {
        if (item.tipo === 'medicamento_unico' && item.dados.medicamento === nomeMedicamento) {
          return item.dados.configuracaoDiluicao
        }
        if (item.tipo === 'grupo_alternativas') {
          const op = item.opcoes.find((o: any) => o.medicamento === nomeMedicamento)
          if (op) return op.configuracaoDiluicao
        }
      }
    }
  }
  return null
}

const validarPrescricao = () => {
  if (!pacienteSelecionado.value) return "Selecione um paciente"
  if (!peso.value || parseFloat(peso.value) <= 0) return "Peso do paciente é obrigatório"
  if (!altura.value || parseFloat(altura.value) <= 0) return "Altura do paciente é obrigatória"
  if (!protocoloNome.value) return "Selecione um protocolo"

  let temAUC = false
  for (const b of blocosPrescricao.value) {
    for (const item of b.itens) {
      if (item.tipo === 'grupo_alternativas' && !item.itemSelecionado) {
        return `Bloco ${b.ordem}: Selecione uma opção para "${item.labelGrupo}"`
      }
      const dados = item.tipo === 'grupo_alternativas' ? item.itemSelecionado : item.dados
      if (dados.unidade === 'AUC') temAUC = true
    }
  }

  if (temAUC) {
    if (!creatinina.value || parseFloat(creatinina.value) <= 0) {
      return "Para medicamentos com dosagem em AUC, a Creatinina é obrigatória."
    }
  }

  return null
}

const confirmarPrescricao = async () => {
  const erro = validarPrescricao()
  if (erro) {
    toast.error(erro)
    return
  }

  try {
    const medicoIdFinal = "med.carlos" // TODO: Usar usuário logado. Fixo aqui porque admin não tem CRM

    const blocosPayload = blocosPrescricao.value.map(bloco => ({
      ordem: bloco.ordem,
      categoria: bloco.categoria,
      itens: bloco.itens.map((itemVisual: any) => {
        const dados = itemVisual.tipo === 'grupo_alternativas'
            ? itemVisual.itemSelecionado
            : itemVisual.dados

        return {
          idItem: dados.idItem || `new-${Date.now()}-${Math.random()}`,
          medicamento: dados.medicamento,
          doseReferencia: dados.doseReferencia.toString(),
          unidade: dados.unidade,
          doseMaxima: dados.doseMaxima,
          doseTeorica: dados.doseTeorica,
          percentualAjuste: dados.percentualAjuste,
          doseFinal: dados.doseFinal,
          via: dados.via,
          tempoMinutos: dados.tempoMinutos,
          diluicaoFinal: dados.diluicaoFinal,
          diasDoCiclo: dados.diasDoCiclo,
          notasEspecificas: dados.notasEspecificas
        }
      })
    }))

    const paciente = appStore.getPacienteById(pacienteSelecionado.value)
    const payload = {
      pacienteId: pacienteSelecionado.value,
      medicoId: medicoIdFinal,
      protocolo: {
        nome: protocoloNome.value,
        cicloAtual: parseInt(numeroCiclo.value)
      },
      dadosPaciente: {
        nome: paciente?.nome,
        prontuario: paciente?.registro,
        nascimento: paciente?.dataNascimento,
        sexo: paciente?.sexo,
        peso: parseFloat(peso.value),
        altura: parseFloat(altura.value),
        sc: parseFloat(dadosPacienteCalculo.value.sc.toFixed(2)),
        creatinina: parseFloat(creatinina.value)
      },
      blocos: blocosPayload
    }

    const res = await appStore.adicionarPrescricao(payload)
    prescricaoAtualId.value = res.id
    prescricaoConcluida.value = true
  } catch (e) {
    console.error(e)
    toast.error("Erro ao salvar prescrição")
  }
}

onMounted(async () => {
  await Promise.all([
    appStore.fetchPacientes(),
    appStore.fetchProtocolos(),
    equipeStore.fetchProfissionais()
  ])

  if (route.query.pacienteId) {
    pacienteSelecionado.value = route.query.pacienteId as string
  }
})

const handleBaixar = async () => {
  if (!prescricaoConcluida.value && !ultimaPrescricao.value) {
    toast.error("É necessário confirmar a prescrição antes de baixar.")
    return
  }
  const idParaBaixar = prescricaoAtualId.value || (ultimaPrescricao.value ? ultimaPrescricao.value.id : null)

  if (!idParaBaixar) {
    toast.error("ID da prescrição não encontrado.")
    return
  }

  toast.info('Gerando PDF...')
  try {
    const response = await api.get(`/api/prescricoes/${idParaBaixar}/pdf`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `prescricao_${idParaBaixar}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    toast.error("Erro ao gerar PDF.")
    console.error(e)
  }
}
</script>

<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-20">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button size="icon" variant="outline" @click="router.back()">
          <ArrowLeft class="h-4 w-4"/>
        </Button>
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Nova Prescrição</h1>
        </div>
      </div>
    </div>

    <div class="pt-6 space-y-4 animate-in slide-in-from-bottom-4 duration-500">
      <div class="flex items-center gap-2">
        <User/>
        <h2 class="text-xl font-semibold text-gray-800">Identificação e Dados Antropométricos</h2>
      </div>
      <PrescricaoIdentificacao
          v-model:altura="altura"
          v-model:creatinina="creatinina"
          v-model:diagnostico="diagnostico"
          v-model:pacienteId="pacienteSelecionado"
          v-model:peso="peso"
          v-model:sexo="sexo"
      />
    </div>

    <div class="pt-6 space-y-4 animate-in slide-in-from-bottom-4 duration-500">
      <div class="flex items-center gap-2">
        <Activity/>
        <h2 class="text-xl font-semibold text-gray-800">Protocolo e Ciclo</h2>
      </div>
      <PrescricaoProtocolo
          v-model:numeroCiclo="numeroCiclo"
          v-model:protocolo="protocoloNome"
          :ultima-prescricao="ultimaPrescricao"
          @repetir="repetirUltimaPrescricao"
      />
    </div>

    <div v-if="blocosPrescricao.length > 0" class="pt-6 space-y-4 animate-in slide-in-from-bottom-4 duration-500">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Pill/>
          <h2 class="text-xl font-semibold text-gray-800">Medicações</h2>
        </div>
        <Button size="sm" variant="ghost" @click="carregarTemplatePadrao(protocoloNome)">
          <RefreshCw class="h-4 w-4 mr-2"/>
          Reiniciar Padrão
        </Button>
      </div>

      <div class="flex flex-col gap-1 mb-2">
        <Label class="text-sm font-semibold text-gray-700">Selecione a Variante do Protocolo</Label>
      </div>

      <Card v-if="templatesDisponiveis.length > 1" class="p-4 flex items-center gap-1 mb-4 w-full">
        <div
            class="flex items-center gap-2 overflow-x-auto flex-1 px-1 w-0"
            style="scrollbar-width: thin; -ms-overflow-style: -ms-autohiding-scrollbar;"
        >
          <Button
              v-for="(template, idx) in templatesDisponiveis"
              :key="idx"
              :variant="templateSelecionadoId === template.idTemplate ? 'default' : 'outline'"
              class="h-8 text-sm whitespace-nowrap flex-shrink-0"
              @click="templateSelecionadoId = template.idTemplate"
          >
            {{ template.idTemplate || `Template ${idx + 1}` }}
          </Button>
        </div>
      </Card>

      <PrescricaoBlocos
          :blocos="blocosPrescricao"
          :dados-paciente="dadosPacienteCalculo"
      />
    </div>

    <div v-else-if="protocoloNome" class="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border border-dashed">
      Carregando estrutura do protocolo...
    </div>

    <PrescricaoFooter
        :concluida="prescricaoConcluida"
        @baixar="handleBaixar"
        @confirmar="confirmarPrescricao"
    />
  </div>
</template>
