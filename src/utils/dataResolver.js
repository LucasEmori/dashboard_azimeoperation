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

// tela3 always shows the latest available data (current system month)
export function resolveTela3Month(data, company) {
  // Pega o primeiro mês disponível no array de meses (o mais recente)
  const latestMonth = data.meta?.months?.[0]
  if (!latestMonth) return null
  const companyData = getCompanyMonth(data, company, latestMonth)
  if (!companyData) return null
  return companyData.tela3
}

export function resolveTela1Month(data, company, month) {
  const companyData = getCompanyMonth(data, company, month)
  if (!companyData) return null
  return companyData.tela1
}