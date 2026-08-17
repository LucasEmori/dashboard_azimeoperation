// Ponytail: mirrors Python helpers in old app.py (_fmt_media, _fmt_int, _delta_pct, _month_short, _year_of)

export function fmtMedia(v) {
  if (v === null || v === undefined) return '—'
  return v > 0 ? `+${v.toFixed(1)}` : v.toFixed(1)
}

export function fmtInt(v) {
  return Math.trunc(v || 0).toLocaleString('pt-BR')
}

export function deltaPct(now, prev) {
  if (prev === null || prev === undefined || prev === 0 || now === null || now === undefined) return null
  return ((now - prev) / prev) * 100
}

export function monthShort(mes) {
  return mes ? String(mes).split(' ')[0] : '—'
}

// Converte 'Janeiro 2026' -> '2026-01', 'Agosto 2025' -> '2025-08', etc.
export function monthToYYYYMM(display) {
  if (!display || display.includes('-')) return display
  const ptMeses = {
    Janeiro: '01', Fevereiro: '02', Março: '03', Abril: '04',
    Maio: '05', Junho: '06', Julho: '07', Agosto: '08',
    Setembro: '09', Outubro: '10', Novembro: '11', Dezembro: '12',
  }
  const parts = display.split(' ')
  const mes = parts[0]
  const ano = parts[1]
  return `${ano}-${ptMeses[mes] || '01'}`
}

// Converte '2026-08' -> 'Agosto 2026'
export function yyyymmToLabel(ym) {
  if (!ym || !ym.includes('-')) return ym
  const ptMeses = [
    'Janeiro','Fevereiro','Março','Abril','Maio','Junho',
    'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro',
  ]
  const [ano, mes] = ym.split('-')
  return `${ptMeses[parseInt(mes, 10) - 1]} ${ano}`
}

export function yearOf(mes) {
  const parts = String(mes || '').split(' ')
  return parts[parts.length - 1] || ''
}