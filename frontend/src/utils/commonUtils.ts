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
