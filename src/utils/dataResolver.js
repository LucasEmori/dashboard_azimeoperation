// Resolve data for a given month from tela2 structure
export function resolveTela2Month(data, company, month) {
  const t2 = data[company].tela2
  const all = [t2.destaque, ...(t2.comparacao || []), t2.ano_anterior].filter(Boolean)
  // Match by mes string
  return all.find(m => m.mes === month) || t2.destaque
}

// tela3 only has data for its own month (destaque or proximo_mes)
export function resolveTela3Month(data, company, month) {
  const t3 = data[company].tela3
  if (t3.mes === month) return t3
  // If month doesn't match, return null (no data available for that month)
  return null
}