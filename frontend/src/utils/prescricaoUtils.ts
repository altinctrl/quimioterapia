import {BlocoForm, ItemBlocoForm} from "@/types/prescricaoTypes.ts";
import {useAppStore} from "@/stores/app.ts";
import {CategoriaBlocoEnum, TemplateCiclo} from "@/types/protocoloTypes";

export const getUnidadeFinal = (unidadeRef: string) => {
  if (!unidadeRef) return ''
  const u = unidadeRef.toLowerCase()
  if (u === 'auc') return 'mg'
  if (u.includes('/')) return u.split('/')[0]
  return unidadeRef
}

export const formatDiasCiclo = (dias: number[]) => {
  if (!dias || !dias.length) return 'N/A'
  const lista = [...dias]
  if (lista.length === 1) return lista[0].toString()
  const ultimoDia = lista.pop()
  return `${lista.join(', ')} e ${ultimoDia}`
}

export const transformToNumber = (val: unknown): any => {
  if (val === '' || val === null || val === undefined) return null;
  if (typeof val === 'number') return val;
  if (typeof val === 'string') {
    const strOriginal = val.trim();
    const isNumericFormat = /^-?\d*[,.]?\d+$/.test(strOriginal);
    if (!isNumericFormat) return val;
    const cleanStr = strOriginal.replace(/,/g, '.');
    const parsed = parseFloat(cleanStr);
    return isNaN(parsed) ? val : parsed;
  }
  return val;
};

export const verificarPresencaUnidade = (blocos: BlocoForm[], unidade: string): boolean => {
  return blocos.some(bloco =>
    bloco.itens.some((item: ItemBlocoForm) => {
      if (item.tipo === 'medicamento_unico') return item.unidade === unidade;
      if (item.tipo === 'grupo_alternativas') return item.itemSelecionado?.unidade === unidade;
      return false;
    })
  );
};

export const temOrdensDuplicadas = (blocos: BlocoForm[]): boolean => {
  const ordens = blocos.map(b => b.ordem);
  return new Set(ordens).size !== ordens.length;
};

export const sequenciaEstaCorreta = (blocos: BlocoForm[]): boolean => {
  if (blocos.length === 0) return true;
  const ordens = blocos.map(b => b.ordem).sort((a, b) => a - b);
  return ordens.every((valor, index) => valor === index + 1);
};

export const getCategoriaLabel = (cat: string) => {
  const map: Record<string, string> = {
    [CategoriaBlocoEnum.PRE_MED]: 'Pré-Medicação',
    [CategoriaBlocoEnum.QT]: 'Terapia',
    [CategoriaBlocoEnum.POS_MED_HOSPITALAR]: 'Pós-Medicação (Hospitalar)',
    [CategoriaBlocoEnum.POS_MED_DOMICILIAR]: 'Pós-Medicação (Domiciliar)',
  }
  return map[cat] || cat
}

export const getCategoriaColor = (cat: string) => {
  if (cat === CategoriaBlocoEnum.QT) return 'border-blue-200 bg-blue-50/20'
  if (cat === CategoriaBlocoEnum.PRE_MED) return 'border-gray-200 bg-gray-50/20'
  return 'border-gray-200 bg-white'
}
export const isDiluenteDisponivel = (nome: string) => {
  const appStore = useAppStore()
  return !appStore.parametros?.diluentes?.includes(nome)
}

export const mesclarPrescricaoComTemplate = (template: TemplateCiclo, blocosAntigos: any[]) => {
  const mapaItensAntigos = new Map<string, { item: any, blocoIndex: number }>();
  const avisos: string[] = [];

  blocosAntigos.forEach((bloco, bIndex) => {
    bloco.itens.forEach((item: any) => {
      const nomeMed = item.medicamento || item.itemSelecionado?.medicamento;
      if (nomeMed) {
        mapaItensAntigos.set(nomeMed, {item, blocoIndex: bIndex});
      }
    });
  });

  const novosBlocos = template.blocos.map((bloco, novoBIndex) => ({
    ...bloco,
    itens: bloco.itens.map(item => {
      const uniqueId = `rep-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

      if (item.tipo === 'grupo_alternativas') {
        const match = item.opcoes.find(op => mapaItensAntigos.has(op.medicamento));
        let itemSelecionado = null;
        if (match) {
          const {item: dadosAntigos, blocoIndex: antigoBIndex} = mapaItensAntigos.get(match.medicamento)!;
          if (antigoBIndex !== novoBIndex) {
            avisos.push(`Ordem alterada: ${match.medicamento} passou do bloco ${antigoBIndex + 1} para o ${novoBIndex + 1}.`);
          }
          if (dadosAntigos.doseMaxima && match.doseMaxima && dadosAntigos.doseMaxima !== match.doseMaxima) {
            avisos.push(`Dose Máxima de ${match.medicamento} difere (Antigo: ${dadosAntigos.doseMaxima} | Novo Modelo: ${match.doseMaxima}). Mantido o valor antigo.`);
          }

          itemSelecionado = {
            ...match,
            idItem: `sel-${Date.now()}-${Math.random()}`,
            tipo: 'medicamento_unico',
            doseReferencia: dadosAntigos.doseReferencia,
            percentualAjuste: dadosAntigos.percentualAjuste ?? 100,
            doseMaxima: dadosAntigos.doseMaxima,
            doseTeorica: 0, doseFinal: 0,
            configuracaoDiluicao: match.configuracaoDiluicao,
            diluicaoFinal: dadosAntigos.diluicaoFinal || match.configuracaoDiluicao?.selecionada || ''
          };
          mapaItensAntigos.delete(match.medicamento);
        }

        return {
          ...item,
          idItem: uniqueId,
          tipo: 'grupo_alternativas',
          itemSelecionado: itemSelecionado,
          opcoes: item.opcoes.map(op => ({...op, tipo: 'medicamento_unico', percentualAjuste: 100}))
        };
      }
      else {
        const dadosTemplate = item.dados;
        const matchInfo = mapaItensAntigos.get(dadosTemplate.medicamento);

        if (matchInfo) {
          const {item: dadosAntigos, blocoIndex: antigoBIndex} = matchInfo;

          if (antigoBIndex !== novoBIndex) {
            avisos.push(`Ordem alterada: ${dadosTemplate.medicamento} passou do bloco ${antigoBIndex + 1} para o ${novoBIndex + 1}.`);
          }

          mapaItensAntigos.delete(dadosTemplate.medicamento);
          return {
            ...dadosTemplate,
            idItem: uniqueId,
            tipo: 'medicamento_unico',
            doseReferencia: dadosAntigos.doseReferencia,
            percentualAjuste: dadosAntigos.percentualAjuste ?? 100,
            doseMaxima: dadosAntigos.doseMaxima,
            diluicaoFinal: dadosAntigos.diluicaoFinal || dadosTemplate.configuracaoDiluicao?.selecionada || '',
            doseTeorica: 0, doseFinal: 0
          };
        }
        avisos.push(`Novo item adicionado pelo protocolo atual: ${dadosTemplate.medicamento}`);
        return {
          ...dadosTemplate,
          idItem: uniqueId,
          tipo: 'medicamento_unico',
          percentualAjuste: 100,
          doseTeorica: 0, doseFinal: 0,
          diluicaoFinal: dadosTemplate.configuracaoDiluicao?.selecionada || ''
        };
      }
    })
  }));

  if (mapaItensAntigos.size > 0) {
    const sobras = Array.from(mapaItensAntigos.keys()).join(', ');
    return {blocos: null, avisos: [`Itens da prescrição anterior não existem no novo modelo: ${sobras}`]};
  }
  return {blocos: novosBlocos, avisos};
};
