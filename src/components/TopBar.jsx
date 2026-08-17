import { useState, useEffect } from 'react'
import { useTheme, useMonth } from '../App.jsx'
import { yyyymmToLabel } from '../utils/format.js'
import { Sun, Moon, CalendarDays, RefreshCw, Check } from 'lucide-react'

export default function TopBar({ meta, company }) {
  const { dark, toggle } = useTheme()
  const { month, setMonth, loading, refresh } = useMonth()
  const [months, setMonths] = useState([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    fetch('/api/months')
      .then(r => r.json())
      .then(d => setMonths(Array.isArray(d.months) ? d.months : []))
      .catch(() => {
        // fallback: meses do próprio meta
        const fb = [
          meta?.destaque_iso, ...(meta?.comparacao_iso || []), meta?.destaque_ano_passado_iso,
        ].filter(Boolean).map(iso => iso.substring(0, 7))
        setMonths([...new Set(fb)])
      })
  }, [])

  const isDestaqueAtual = month === meta?.destaque_iso?.substring(0, 7)

  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3 mt-2 mb-3 bg-muted rounded-xl border border-border flex-wrap">
      <div className="flex items-center gap-2">
        <CalendarDays size={18} className="text-co-accent flex-shrink-0" />
        <label htmlFor="mes-destaque" className="text-sm font-bold text-foreground">Mês destaque:</label>
        <select
          id="mes-destaque"
          value={month || ''}
          onChange={e => setMonth(e.target.value)}
          disabled={loading}
          className="bg-background border border-border text-foreground rounded-lg px-3 py-1.5 text-sm font-bold focus:ring-2 focus:ring-ring outline-none cursor-pointer disabled:opacity-50"
        >
          {months.map(m => (
            <option key={m} value={m}>{yyyymmToLabel(m)}</option>
          ))}
        </select>
        {isDestaqueAtual && !loading && (
          <span className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-co-accent/20 text-co-accent border border-co-accent/40">
            <Check size={11} /> atual
          </span>
        )}
      </div>

      <button
        onClick={refresh}
        disabled={loading}
        aria-label="Atualizar dados do Data Warehouse"
        className="flex items-center gap-2 px-3 h-9 rounded-lg bg-background border border-border text-foreground text-xs font-bold hover:ring-2 hover:ring-ring/50 transition-all cursor-pointer disabled:opacity-50"
      >
        <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        <span className="hidden sm:inline">{loading ? 'Consultando DW...' : 'Atualizar do DW'}</span>
      </button>

      <button
        onClick={toggle}
        aria-label={dark ? 'Ativar tema claro' : 'Ativar tema escuro'}
        className="flex items-center justify-center w-11 h-11 rounded-full bg-background border border-border text-foreground hover:ring-2 hover:ring-ring/50 transition-all duration-200 cursor-pointer flex-shrink-0"
      >
        {dark ? <Sun size={20} /> : <Moon size={20} />}
      </button>
    </div>
  )
}