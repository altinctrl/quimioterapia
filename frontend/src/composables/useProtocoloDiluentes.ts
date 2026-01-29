import {computed, type Ref} from 'vue';
import type {ConfiguracaoDiluicao} from "@/types/typesProtocolo.ts";
import {useConfiguracaoStore} from "@/stores/storeAjustes.ts";

export function useProtocoloDiluentes(modelValue: Ref<ConfiguracaoDiluicao | undefined>, emit: any) {
  const configStore = useConfiguracaoStore();

  const listaGlobalDiluentes = computed(() => {
    return configStore.parametros?.diluentes || [];
  });

  const safeModelValue = computed((): ConfiguracaoDiluicao => {
    return modelValue.value || {selecionada: '', opcoesPermitidas: []};
  });

  const diluentesUnificados = computed(() => {
    const globais = listaGlobalDiluentes.value;
    const locais = safeModelValue.value.opcoesPermitidas || [];
    const unicos = new Set([...globais, ...locais]);
    return Array.from(unicos).sort((a, b) => a.localeCompare(b));
  });

  const isIndisponivel = (diluente: string) => {
    if (listaGlobalDiluentes.value.length === 0) return false;
    return !listaGlobalDiluentes.value.includes(diluente);
  };

  const labelResumido = computed(() => {
    if (diluentesUnificados.value.length === 0) return 'Sem opções';
    const permitidos = safeModelValue.value.opcoesPermitidas || [];
    if (permitidos.length === 0) return 'Selecione...';
    if (permitidos.length === 1) return permitidos[0];
    return `${permitidos.length} selecionados`;
  });

  const toggleDiluente = (diluente: string, checked: boolean) => {
    const novoConfig: ConfiguracaoDiluicao = modelValue.value
      ? {...modelValue.value}
      : {selecionada: '', opcoesPermitidas: []};

    if (!novoConfig.opcoesPermitidas) novoConfig.opcoesPermitidas = [];

    if (checked) {
      if (!novoConfig.opcoesPermitidas.includes(diluente)) {
        novoConfig.opcoesPermitidas.push(diluente);
      }
      if (novoConfig.opcoesPermitidas.length === 1) {
        novoConfig.selecionada = diluente;
      }
    } else {
      novoConfig.opcoesPermitidas = novoConfig.opcoesPermitidas.filter(d => d !== diluente);
      if (novoConfig.selecionada === diluente) {
        novoConfig.selecionada = novoConfig.opcoesPermitidas[0] || '';
      }
    }
    emit('update:modelValue', novoConfig);
  };

  const updateSelecionada = (val: string) => {
    const novoConfig: ConfiguracaoDiluicao = modelValue.value
      ? {...modelValue.value, selecionada: val}
      : {selecionada: val, opcoesPermitidas: [val]};
    emit('update:modelValue', novoConfig);
  };

  return {
    safeModelValue,
    diluentesUnificados,
    isIndisponivel,
    labelResumido,
    toggleDiluente,
    updateSelecionada
  };
}
