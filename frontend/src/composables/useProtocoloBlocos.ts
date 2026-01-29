import {ref} from 'vue';
import {createEmptyBloco, createEmptyItemBloco, createEmptyMedicamento} from '@/utils/factoriesProtocolo.ts';
import type {Bloco, ItemBloco, TemplateCiclo} from "@/types/typesProtocolo.ts";

export function useProtocoloBlocos() {
  const selectedIndexes = ref<number[]>([]);

  const addItemToBloco = (bloco: Bloco) => {
    bloco.itens.push(createEmptyItemBloco());
  };

  const removeItemFromBloco = (bloco: Bloco, idx: number) => {
    bloco.itens.splice(idx, 1);
  };

  const addOptionToGroup = (item: ItemBloco) => {
    if (item.tipo !== 'grupo_alternativas') return;
    item.opcoes.push(createEmptyMedicamento());
  };

  const removeOptionFromGroup = (item: ItemBloco, idx: number) => {
    if (item.tipo !== 'grupo_alternativas') return;
    item.opcoes.splice(idx, 1);
  };

  const toggleItemType = (bloco: Bloco, item: ItemBloco, index: number) => {
    const novosItensNoBloco = [...bloco.itens];
    if (item.tipo === 'medicamento_unico') {
      const novoGrupo: ItemBloco = {
        tipo: 'grupo_alternativas',
        labelGrupo: item.dados.medicamento || 'Nova Escolha',
        opcoes: [JSON.parse(JSON.stringify(item.dados))]
      };
      novosItensNoBloco.splice(index, 1, novoGrupo);
    } else {
      const opcoes = item.opcoes || [];
      if (opcoes.length === 0) opcoes.push(createEmptyMedicamento());
      const itensSeparados: ItemBloco[] = opcoes.map((op: any) => ({
        tipo: 'medicamento_unico',
        dados: JSON.parse(JSON.stringify(op))
      }));
      novosItensNoBloco.splice(index, 1, ...itensSeparados);
    }
    bloco.itens = novosItensNoBloco;
    selectedIndexes.value = [];
  };

  const toggleSelection = (idx: number, checked: boolean) => {
    if (checked) selectedIndexes.value.push(idx);
    else selectedIndexes.value = selectedIndexes.value.filter(i => i !== idx);
  };

  const mergeSelected = (bloco: Bloco) => {
    if (selectedIndexes.value.length < 2) return;
    const targetIndex = Math.min(...selectedIndexes.value);
    const indexesAsc = [...selectedIndexes.value].sort((a, b) => a - b);
    const novasOpcoes: any[] = [];

    indexesAsc.forEach(idx => {
      const item = bloco.itens[idx];
      if (item.tipo === 'medicamento_unico') {
        novasOpcoes.push(JSON.parse(JSON.stringify(item.dados)));
      } else {
        novasOpcoes.push(...JSON.parse(JSON.stringify(item.opcoes)));
      }
    });

    const copiaItens = [...bloco.itens];
    const indexesDesc = [...selectedIndexes.value].sort((a, b) => b - a);
    indexesDesc.forEach(idx => {
      copiaItens.splice(idx, 1);
    });

    const novoGrupo: ItemBloco = {
      tipo: 'grupo_alternativas',
      labelGrupo: 'Grupo Mesclado',
      opcoes: novasOpcoes,
    };

    copiaItens.splice(targetIndex, 0, novoGrupo);
    bloco.itens = copiaItens;
    selectedIndexes.value = [];
  };

  const addBlocoToTemplate = (template: TemplateCiclo) => {
    const novaOrdem = (template.blocos.length || 0) + 1;
    template.blocos.push(createEmptyBloco(novaOrdem));
  };

  const reorderBlocos = (template: TemplateCiclo) => {
    template.blocos.forEach((b, idx) => {
      b.ordem = idx + 1;
    });
  };

  const removeBlocoFromTemplate = (template: TemplateCiclo, index: number) => {
    template.blocos.splice(index, 1);
    reorderBlocos(template);
  };

  const moveBlocoInTemplate = (template: TemplateCiclo, index: number, direction: 'up' | 'down') => {
    const blocos = template.blocos;
    if (direction === 'up' && index > 0) {
      [blocos[index], blocos[index - 1]] = [blocos[index - 1], blocos[index]];
    } else if (direction === 'down' && index < blocos.length - 1) {
      [blocos[index], blocos[index + 1]] = [blocos[index + 1], blocos[index]];
    }
    reorderBlocos(template);
  };

  return {
    selectedIndexes,
    addItemToBloco,
    removeItemFromBloco,
    addOptionToGroup,
    removeOptionFromGroup,
    toggleItemType,
    toggleSelection,
    mergeSelected,
    addBlocoToTemplate,
    removeBlocoFromTemplate,
    moveBlocoInTemplate,
  };
}
