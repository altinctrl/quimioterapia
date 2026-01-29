import {diasSemanaOptions} from "@/constants/constProtocolos.ts";

export const parseNumber = (val: any): number => {
  if (typeof val === 'number') return val
  if (!val) return 0
  return parseFloat(val.toString().replace(',', '.')) || 0
}

export const formatNumber = (val: number) => {
  if (isNaN(val) || val === null || val === undefined) return '0,00';
  const casasDecimais = val < 1 ? 3 : 2;
  return val.toLocaleString('pt-BR', {
    minimumFractionDigits: casasDecimais,
    maximumFractionDigits: casasDecimais
  });
}

export const formatDiasSemana = (dias: number[] | undefined): string => {
  if (!dias || !dias.length) return '';
  const nomes = dias.map(dia => diasSemanaOptions.find(o => o.value === dia)?.label || '');
  if (nomes.length === 1) return nomes[0];
  const ultimoNome = nomes.pop();
  return `${nomes.join(', ')} e ${ultimoNome}`;
};

export const formatDiasCicloToString = (arr: number[] | undefined): string => {
  return arr?.join(', ') || '';
};

export const parseDiasCicloFromString = (val: string | number): number[] => {
  const strVal = String(val);
  return strVal.split(',')
    .map(s => parseInt(s.trim()))
    .filter(n => !isNaN(n));
};
