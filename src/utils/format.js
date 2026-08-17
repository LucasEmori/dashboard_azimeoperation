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

export function yearOf(mes) {
  const parts = String(mes || '').split(' ')
  return parts[parts.length - 1] || ''
}