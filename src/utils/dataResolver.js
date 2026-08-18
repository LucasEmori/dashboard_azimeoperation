/** Obtem empresa data para um dado month string "YYYY-MM". */
export function getCompanyMonth(data, company, month) {
  const m = data.by_month?.[month]
  if (!m) return null
  return m[company] || null
}

// tela2 destrincha o entry por mes (destaque e comparações) duma empresa.
export function resolveTela2Month(data, company, month) {
  const companyData = getCompanyMonth(data, company, month)
  if (!companyData) return null
  return companyData.tela2
}

// tela3: sempre o mes mais recente COM registros (walk-back).
// by_month[M].tela3 = lancamentos de M+1; mes atual pode apontar p/ futuro vazio.
export function resolveTela3Month(data, company) {
  const months = data.meta?.months || []
  for (const m of months) {
    const cd = getCompanyMonth(data, company, m)
    if (cd?.tela3 && (cd.tela3.total_itens || 0) > 0) return cd.tela3
  }
  return null
}

export function resolveTela1Month(data, company, month) {
  const companyData = getCompanyMonth(data, company, month)
  if (!companyData) return null
  return companyData.tela1
}