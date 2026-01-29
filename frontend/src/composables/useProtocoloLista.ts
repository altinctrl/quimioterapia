import {computed, ref, type Ref} from 'vue';
import {diasSemanaOptions} from '@/constants/constProtocolos.ts';
import type {Protocolo, ProtocoloFiltros} from "@/types/typesProtocolo.ts";
import {useLocalStorage} from "@vueuse/core";

export function useProtocoloLista(
  protocolos: Ref<Protocolo[]>,
  diasFuncionamento: Ref<number[]>
) {
  const searchTerm = ref('');

  const filtros = useLocalStorage<ProtocoloFiltros>('app_protocolos_filtros', {
    sortOrder: 'nome',
    status: 'todos',
    restricao: 'todos',
    grupoInfusao: ['rapido', 'medio', 'longo', 'extra_longo']
  });

  const filteredProtocolos = computed(() => {
    let result = protocolos.value.filter(p => {
      const matchesSearch = p.nome.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
        (p.indicacao && p.indicacao.toLowerCase().includes(searchTerm.value.toLowerCase()));
      if (!matchesSearch) return false;

      if (filtros.value.status === 'ativos' && !p.ativo) return false;
      if (filtros.value.status === 'inativos' && p.ativo) return false;

      const {isRestricted} = checkRestricao(p);
      if (filtros.value.restricao === 'com' && !isRestricted) return false;
      if (filtros.value.restricao === 'sem' && isRestricted) return false;

      const grupo = inferirGrupoInfusao(p.tempoTotalMinutos || 0);
      return filtros.value.grupoInfusao.includes(grupo);
    });

    return result.sort((a: any, b: any) => {
      if (filtros.value.sortOrder === 'duracao') {
        return (a.tempoTotalMinutos || 0) - (b.tempoTotalMinutos || 0);
      }
      return a.nome.localeCompare(b.nome);
    });
  });

  const inferirGrupoInfusao = (duracao: number): 'rapido' | 'medio' | 'longo' | 'extra_longo' => {
    if (duracao <= 30) return 'rapido';
    if (duracao <= 120) return 'medio';
    if (duracao <= 240) return 'longo';
    return 'extra_longo';
  };

  const checkRestricao = (protocolo: Protocolo) => {
    const diasPermitidos = protocolo.diasSemanaPermitidos || [];
    const diasClinica = diasFuncionamento.value || [];

    if (!diasPermitidos.length || !diasClinica.length) {
      return {isRestricted: false, text: 'Permitido todos os dias.'};
    }

    const diasFaltantes = diasClinica.filter((d: number) => !diasPermitidos.includes(d));
    if (diasFaltantes.length === 0) {
      return {isRestricted: false, text: 'Permitido todos os dias.'};
    }

    const labels = diasPermitidos
      .sort((a: number, b: number) => a - b)
      .map((d: number) => diasSemanaOptions.find(opt => opt.value === d)?.label)
      .filter(Boolean)
      .join(', ');

    return {isRestricted: true, text: `Permitido nos dias: ${labels}.`};
  };

  return {
    searchTerm,
    filtros,
    filteredProtocolos,
    checkRestricao
  };
}
