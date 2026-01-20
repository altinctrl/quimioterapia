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
