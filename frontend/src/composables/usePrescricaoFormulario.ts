import {computed, nextTick, ref, watch} from 'vue'
import {useForm} from 'vee-validate'
import {onBeforeRouteLeave, useRoute, useRouter} from 'vue-router'
import {toast} from 'vue-sonner'
import {useAppStore} from '@/stores/storeGeral.ts'
import {usePrescricaoCalculos} from './usePrescricaoCalculos'
import {prescricaoFormSchema, type PrescricaoFormValues} from '@/schemas/esquemaPrescricao.ts'
import {TemplateCiclo} from "@/types/typesProtocolo.ts";
import {mesclarPrescricaoComTemplate} from "@/utils/utilsPrescricao.ts";
import {parseDiasCicloFromString} from "@/utils/utilsComuns.ts";

const parseNumber = (val: string | number | null | undefined): number => {
  if (val === null || val === undefined || val === '') return 0
  if (typeof val === 'number') return val
  const str = val.toString().replace(',', '.').trim()
  const num = parseFloat(str)
  return isNaN(num) ? 0 : num
}

export function usePrescricaoFormulario() {
  const route = useRoute()
  const router = useRouter()
  const appStore = useAppStore()
  const {calcularSC, calcularDoseTeorica, calcularDoseFinal} = usePrescricaoCalculos()

  const bloqueandoWatcherTemplate = ref(false)
  const bloqueandoTemplateInicial = ref(false)
  const substituicaoOriginalId = ref<string | null>(null)
  const prescricaoConcluida = ref(false)
  const prescricaoGeradaId = ref<string | null>(null)
  const templateSelecionadoId = ref<string>('')
  const templatesDisponiveis = ref<TemplateCiclo[]>([])
  const errors = ref<Record<string, string>>({})

  const {
    values,
    setValues,
    setFieldValue,
    defineField,
    validate,
    meta,
  } = useForm<PrescricaoFormValues>({
    initialValues: {
      pacienteId: '',
      peso: 0,
      altura: 0,
      creatinina: undefined,
      sc: 0,
      idade: 0,
      sexo: '',
      diagnostico: '',
      protocoloNome: '',
      numeroCiclo: 1,
      blocos: [],
      medicoNome: '',
      medicoCrm: '',
    }
  })

  const [pacienteId] = defineField('pacienteId')
  const [peso] = defineField('peso')
  const [altura] = defineField('altura')
  const [creatinina] = defineField('creatinina')
  const [sc] = defineField('sc')
  const [diagnostico] = defineField('diagnostico')
  const [protocoloNome] = defineField('protocoloNome')
  const [numeroCiclo] = defineField('numeroCiclo')
  const [medicoNome] = defineField('medicoNome')
  const [medicoCrm] = defineField('medicoCrm')

  const pacienteSelecionadoObj = computed(() =>
    appStore.pacientes.find(p => p.id === values.pacienteId)
  )

  const dadosPacienteCalculo = computed(() => ({
    peso: parseNumber(values.peso),
    altura: parseNumber(values.altura),
    sc: parseNumber(values.sc),
    creatinina: parseNumber(values.creatinina),
    sexo: pacienteSelecionadoObj.value?.sexo || '',
    idade: pacienteSelecionadoObj.value?.idade || 60
  }))

  const ultimaPrescricao = computed(() => {
    if (!values.pacienteId) return null
    const lista = appStore.prescricoes.filter(p => p.pacienteId === values.pacienteId)
    if (!lista || lista.length === 0) return null

    return [...lista].sort((a, b) =>
      new Date(b.dataEmissao).getTime() - new Date(a.dataEmissao).getTime()
    )[0]
  })

  const calcularItemInterno = (item: any) => {
    if (item.tipo === 'grupo_alternativas') {
      if (item.itemSelecionado) calcularItemInterno(item.itemSelecionado)
      return
    }
    const itemNumerico = {
      ...item,
      pisoCreatinina: parseNumber(item.pisoCreatinina),
      tetoGfr: parseNumber(item.tetoGfr),
      percentualAjuste: parseNumber(item.percentualAjuste),
      doseMaxima: parseNumber(item.doseMaxima)
    }
    const doseTeorica = calcularDoseTeorica(itemNumerico, dadosPacienteCalculo.value)
    const doseFinal = calcularDoseFinal(
      doseTeorica,
      itemNumerico.percentualAjuste,
      itemNumerico.doseMaxima
    )
    if (item.doseTeorica !== doseTeorica) item.doseTeorica = doseTeorica
    if (item.doseFinal !== doseFinal) item.doseFinal = doseFinal
  }

  const recalcularTodasDoses = () => {
    if (!values.blocos || values.blocos.length === 0) return
    const novosBlocos = JSON.parse(JSON.stringify(values.blocos))
    let houveAlteracao = false
    novosBlocos.forEach((bloco: any) => {
      bloco.itens.forEach((item: any) => {
        const doseTeoricaAntiga = item.doseTeorica
        const doseFinalAntiga = item.doseFinal
        calcularItemInterno(item)
        if (item.doseTeorica !== doseTeoricaAntiga || item.doseFinal !== doseFinalAntiga) {
          houveAlteracao = true
        }
      })
    })
    if (houveAlteracao) setFieldValue('blocos', novosBlocos)
  }

  const aplicarTemplate = async (template: TemplateCiclo) => {
    const blocosFormatados = template.blocos.map(bloco => ({
      ...bloco,
      itens: bloco.itens.map(item => {
        const uniqueId = `tmpl-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        if (item.tipo === 'grupo_alternativas') {
          return {
            ...item,
            idItem: uniqueId,
            tipo: 'grupo_alternativas',
            itemSelecionado: null,
            opcoes: item.opcoes.map(op => ({
              ...op,
              tipo: 'medicamento_unico',
              percentualAjuste: 100,
              configuracaoDiluicao: op.configuracaoDiluicao
            }))
          }
        }
        return {
          ...item.dados,
          idItem: uniqueId,
          tipo: 'medicamento_unico',
          percentualAjuste: 100,
          diluicaoFinal: item.dados.configuracaoDiluicao?.selecionada || '',
          doseTeorica: 0,
          doseFinal: 0,
          pisoCreatinina: item.dados.pisoCreatinina || 0.7,
          tetoGfr: item.dados.tetoGfr || 125
        }
      })
    }))
    setFieldValue('blocos', JSON.parse(JSON.stringify(blocosFormatados)))
    await nextTick(() => {
      recalcularTodasDoses()
    })
  }

  const repetirUltimaPrescricao = () => {
    if (!ultimaPrescricao.value) {
      toast.error('Nenhuma prescrição anterior encontrada.')
      return
    }
    const ultima = ultimaPrescricao.value
    const protoRef = ultima.conteudo.protocolo

    setFieldValue('protocoloNome', protoRef.nome)

    setTimeout(async () => {
      const protoDef = appStore.protocolos.find(p => p.nome === protoRef.nome)
      let proxCiclo = protoRef.cicloAtual + 1
      if (protoDef?.totalCiclos && proxCiclo > protoDef.totalCiclos) {
        toast.warning(`Ciclo ${proxCiclo} excede o total (${protoDef.totalCiclos}).`)
      }
      setFieldValue('numeroCiclo', proxCiclo)
      if (!ultima.conteudo.blocos) return;
      let blocosFinais = null;
      let idTemplateFinal = '';
      let melhorMergeResult = null;
      let templateDoMerge = null;
      if (templatesDisponiveis.value?.length > 0) {
        for (const template of templatesDisponiveis.value) {
          const resultado = mesclarPrescricaoComTemplate(template, ultima.conteudo.blocos);
          if (resultado.blocos) {
            melhorMergeResult = resultado;
            templateDoMerge = template;
            break;
          }
        }
      }

      const carregarModoRaw = () => {
        const rawBlocos = ultima.conteudo.blocos.map((b: any) => ({
          ordem: b.ordem,
          categoria: b.categoria,
          itens: b.itens.map((itemSalvo: any) => ({
            ...itemSalvo,
            idItem: `raw-${Date.now()}-${Math.random()}`,
            tipo: 'medicamento_unico',
            percentualAjuste: itemSalvo.percentualAjuste || 100,
            doseReferencia: parseFloat(itemSalvo.doseReferencia as any),
            doseTeorica: 0, doseFinal: 0
          }))
        }));
        setFieldValue('blocos', JSON.parse(JSON.stringify(rawBlocos)));
        templateSelecionadoId.value = '';
        toast.success('Prescrição anterior carregada exatamente como era.');
      };

      if (melhorMergeResult && templateDoMerge) {
        const {blocos, avisos} = melhorMergeResult;
        if (avisos.length > 0) {
          const msg = `O modelo atual do protocolo difere da prescrição anterior:\n\n- ${avisos.join('\n- ')}\n\nDeseja adaptar ao novo modelo?\nCancelar carregará a cópia exata da prescrição anterior.`;
          if (confirm(msg)) {
            blocosFinais = blocos;
            idTemplateFinal = templateDoMerge.idTemplate;
            toast.success('Dados adaptados ao novo modelo do protocolo.');
          } else {
            carregarModoRaw();
            await nextTick(recalcularTodasDoses);
            return;
          }
        } else {
          blocosFinais = blocos;
          idTemplateFinal = templateDoMerge.idTemplate;
          toast.success('Dados recuperados com sucesso.');
        }

        bloqueandoWatcherTemplate.value = true;
        templateSelecionadoId.value = idTemplateFinal;
        setFieldValue('blocos', JSON.parse(JSON.stringify(blocosFinais)));
      } else {
        toast.info('Nenhum modelo ou protocolo compatíveis encontrados. Carregando cópia exata.');
        carregarModoRaw();
      }

      await nextTick(recalcularTodasDoses);
    }, 500);
  }

  const aplicarPrescricaoOriginal = async (prescricao: any) => {
    if (!prescricao?.conteudo) return

    bloqueandoTemplateInicial.value = true

    setFieldValue('pacienteId', prescricao.pacienteId || '')
    setFieldValue('peso', prescricao.conteudo.paciente?.peso || 0)
    setFieldValue('altura', prescricao.conteudo.paciente?.altura || 0)
    setFieldValue('creatinina', prescricao.conteudo.paciente?.creatinina || undefined)
    setFieldValue('idade', prescricao.conteudo.paciente?.idade || 0)
    setFieldValue('sexo', prescricao.conteudo.paciente?.sexo || '')
    setFieldValue('diagnostico', prescricao.conteudo.diagnostico || '')
    setFieldValue('protocoloNome', prescricao.conteudo.protocolo?.nome || '')
    setFieldValue('numeroCiclo', prescricao.conteudo.protocolo?.cicloAtual || 1)

    const rawBlocos = (prescricao.conteudo.blocos || []).map((b: any) => ({
      ordem: b.ordem,
      categoria: b.categoria,
      itens: (b.itens || []).map((itemSalvo: any) => ({
        ...itemSalvo,
        idItem: `raw-${Date.now()}-${Math.random()}`,
        tipo: 'medicamento_unico',
        percentualAjuste: itemSalvo.percentualAjuste || 100,
        doseReferencia: parseFloat(itemSalvo.doseReferencia as any),
        doseTeorica: 0,
        doseFinal: 0
      }))
    }))

    setFieldValue('blocos', JSON.parse(JSON.stringify(rawBlocos)))
    templateSelecionadoId.value = ''

    await nextTick(() => {
      recalcularTodasDoses()
    })
    bloqueandoTemplateInicial.value = false
  }

  const executarValidacao = (): boolean => {
    errors.value = {};
    
    // Validação condicional para prescrição física
    if (route.query.prescricaoFisica === 'true') {
      if (!values.medicoNome || values.medicoNome.trim() === '') {
        errors.value['medicoNome'] = 'Nome do médico é obrigatório para prescrição física';
      }
      if (!values.medicoCrm || values.medicoCrm.trim() === '') {
        errors.value['medicoCrm'] = 'CRM é obrigatório para prescrição física';
      }
      if (Object.keys(errors.value).length > 0) {
        return false;
      }
    }
    
    const parseResult = prescricaoFormSchema.safeParse(values);
    if (!parseResult.success) {
      const formattedErrors: Record<string, string> = {};
      parseResult.error.issues.forEach(issue => {
        let pathKey = '';
        issue.path.forEach((part, index) => {
          if (typeof part === 'number') {
            pathKey += `[${part}]`;
          } else {
            pathKey += (index === 0 ? part : `.${part}`);
          }
        });
        formattedErrors[pathKey] = issue.message;
      });
      errors.value = {...errors.value, ...formattedErrors};
      return false;
    }
    return true;
  }

  const salvar = async () => {
    if (!executarValidacao()) {
      toast.error('Verifique os campos obrigatórios em vermelho.');
      console.log('Erros de validação:', errors.value);
      return;
    }

    const formValues = JSON.parse(JSON.stringify(values));
    try {
      const blocosPayload = formValues.blocos.map((bloco: any) => ({
        ordem: bloco.ordem,
        categoria: bloco.categoria,
        itens: bloco.itens.filter((item: any) => !item.suspenso).map((item: any) => {
          const dados = item.tipo === 'grupo_alternativas'
            ? item.itemSelecionado!
            : item;

          let diasProcessados = dados.diasDoCiclo;
          if (typeof diasProcessados === 'string') {
             diasProcessados = parseDiasCicloFromString(diasProcessados);
          }
          if (Array.isArray(diasProcessados)) {
            diasProcessados.sort((a: number, b: number) => a - b);
          }

          return {
            idItem: dados.idItem || `new-${Date.now()}-${Math.random()}`,
            medicamento: dados.medicamento,
            doseReferencia: dados.doseReferencia?.toString(),
            unidade: dados.unidade,
            doseMaxima: parseNumber(dados.doseMaxima),
            doseTeorica: dados.doseTeorica,
            percentualAjuste: parseNumber(dados.percentualAjuste),
            doseFinal: dados.doseFinal,
            via: dados.via,
            tempoMinutos: dados.tempoMinutos,
            diluicaoFinal: dados.diluicaoFinal,
            diasDoCiclo: diasProcessados,
            notasEspecificas: dados.notasEspecificas
          }
        })
      })).filter((bloco: any) => bloco.itens.length > 0);

      const payload: any = {
        pacienteId: formValues.pacienteId,
        medicoId: 'med.carlos',
        protocolo: {
          nome: formValues.protocoloNome,
          cicloAtual: formValues.numeroCiclo || 1
        },
        dadosPaciente: {
          ...dadosPacienteCalculo.value,
          nome: pacienteSelecionadoObj.value?.nome || '',
          prontuario: pacienteSelecionadoObj.value?.registro || '',
          nascimento: pacienteSelecionadoObj.value?.dataNascimento || ''
        },
        blocos: blocosPayload,
        diagnostico: formValues.diagnostico
      }

      if (route.query.prescricaoFisica === 'true' && formValues.medicoNome && formValues.medicoCrm) {
        payload.medicoNome = formValues.medicoNome
        payload.medicoCrm = formValues.medicoCrm
      }

      if (substituicaoOriginalId.value) {
        try {
          const resSub = await appStore.adicionarPrescricaoSubstituicao(
            payload as any,
            substituicaoOriginalId.value,
            'Substituída por nova prescrição'
          )
          prescricaoGeradaId.value = resSub.id
          prescricaoConcluida.value = true
          await appStore.fetchPrescricoes(formValues.pacienteId)

          if (route.query.retorno === 'agendamento' && prescricaoGeradaId.value) {
            await router.push({
              name: 'Agendamento',
              query: {
                pacienteId: formValues.pacienteId,
                prescricaoId: prescricaoGeradaId.value
              }
            })
          }
          return
        } catch (e) {
          console.error(e)
          const confirmar = window.confirm(
            'Falha ao substituir de forma atômica. Deseja criar a nova prescrição sem vincular à antiga?'
          )
          if (!confirmar) return
        }
      }

      const res = await appStore.adicionarPrescricao(payload as any)
      prescricaoGeradaId.value = res.id
      prescricaoConcluida.value = true
      await appStore.fetchPrescricoes(formValues.pacienteId)

      if (route.query.retorno === 'agendamento' && prescricaoGeradaId.value) {
        await router.push({
          name: 'Agendamento',
          query: {
            pacienteId: formValues.pacienteId,
            prescricaoId: prescricaoGeradaId.value
          }
        })
      }
    } catch (e) {
      console.error(e)
      toast.error('Erro ao salvar prescrição.')
    }
  }

  const init = async () => {
    await appStore.fetchProtocolos()
    const idUrl = route.query.pacienteId as string
    const substituirDe = route.query.substituirDe as string
    if (substituirDe) substituicaoOriginalId.value = substituirDe
    if (idUrl) {
      await appStore.carregarPaciente(idUrl)
      setFieldValue('pacienteId', idUrl)
      await appStore.fetchPrescricoes(idUrl)
      if (substituirDe) {
        const original = appStore.prescricoes.find(p => p.id === substituirDe)
        if (original) {
          await aplicarPrescricaoOriginal(original)
        }
      }
    } else {
      await appStore.fetchPacientes()
    }
  }

  watch([() => values.peso, () => values.altura], ([novoPeso, novaAltura]) => {
    const p = parseNumber(novoPeso)
    const a = parseNumber(novaAltura)
    const novaSc = calcularSC(p, a)
    if (Math.abs(novaSc - parseNumber(values.sc)) > 0.001) {
      setFieldValue('sc', novaSc)
    }
  })

  watch([() => values.sc, () => values.creatinina], () => {
    recalcularTodasDoses()
  }, {deep: true})

  watch(() => values.pacienteId, async (id) => {
    if (!id) return
    await appStore.fetchPrescricoes(id)
    const p = appStore.getPacienteById(id)
    if (p) {
      setFieldValue('peso', p.peso || 0)
      setFieldValue('altura', p.altura || 0)
      setFieldValue('idade', p.idade || 0)
      setFieldValue('sexo', p.sexo || '')
    }
  })

  watch(() => values.protocoloNome, async (novoNome) => {
    setFieldValue('blocos', [])
    templatesDisponiveis.value = []
    templateSelecionadoId.value = ''
    if (!novoNome) return
    const proto = appStore.protocolos.find(p => p.nome === novoNome)
    if (proto) {
      setFieldValue('duracaoCicloDias', proto.duracaoCicloDias || undefined)

      templatesDisponiveis.value = proto.templatesCiclo || []
      if (!bloqueandoTemplateInicial.value && proto.templatesCiclo?.length > 0) {
        await nextTick(() => {
          templateSelecionadoId.value = proto.templatesCiclo[0].idTemplate
        })
      }
    }
  })

  watch(templateSelecionadoId, async (novoId) => {
    if (!novoId) return
    if (bloqueandoWatcherTemplate.value) {
      bloqueandoWatcherTemplate.value = false
      return
    }
    const template = templatesDisponiveis.value.find(t => t.idTemplate === novoId)
    if (template) await aplicarTemplate(template)
  })

  watch(values, () => {
    executarValidacao();
  }, {deep: true});

  onBeforeRouteLeave((_to, _from, next) => {
    if (prescricaoConcluida.value) {
      next();
      return;
    }

    if (meta.value.dirty) {
      const answer = window.confirm('Você tem dados não salvos na prescrição. Deseja sair e perder o progresso?');
      if (answer) next();
      else next(false);
    } else {
      next();
    }
  });

  return {
    values,
    errors: errors,
    setFieldValue,
    setValues,
    validate,
    fields: {
      pacienteId,
      peso,
      altura,
      creatinina,
      sc,
      diagnostico,
      protocoloNome,
      numeroCiclo,
      medicoNome,
      medicoCrm
    },
    pacienteSelecionadoObj,
    ultimaPrescricao,
    templatesDisponiveis,
    templateSelecionadoId,
    prescricaoConcluida,
    prescricaoGeradaId,
    init,
    salvar,
    repetirUltimaPrescricao,
    recalcularTodasDoses
  }
}
