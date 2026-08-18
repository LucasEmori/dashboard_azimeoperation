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

// tela3 only has data for its own month (destaque or proximo_mes)
export function resolveTela3Month(data, company, month) {
  const companyData = getCompanyMonth(data, company, month)
  if (!companyData) return null
  return companyData.tela3
}

export function resolveTela1Month(data, company, month) {
  const companyData = getCompanyMonth(data, company, month)
  if (!companyData) return null
  return companyData.tela1
}