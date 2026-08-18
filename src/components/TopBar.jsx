import { useTheme, useMonth, useData } from '../App.jsx'
import { monthToYYYYMM } from '../utils/format.js'
import { Sun, Moon, CalendarDays, RefreshCw, Check } from 'lucide-react'

export default function TopBar({ meta, company }) {
  const { dark, toggle } = useTheme()
  const { month, setMonth, syncing, triggerSync } = useMonth()
  const data = useData()

  // Meses disponíveis vêm do data.json: destaque + comparacao + ano anterior
  const meses = [
    ...new Set([
      meta?.destaque,
      ...(meta?.comparacao || []),
      meta?.destaque_ano_passado,
    ].filter(Boolean)),
  ]
  const monthLabel = data && month === null ? meta?.destaque : null
  const isDestaqueAtual = month === monthToYYYYMM(meta?.destaque)

  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3 mt-2 mb-3 bg-muted rounded-xl border border-border flex-wrap">
      <div className="flex items-center gap-2">
        <CalendarDays size={18} className="text-co-accent flex-shrink-0" />
        <label htmlFor="mes-destaque" className="text-sm font-bold text-foreground">Mês destaque:</label>
        <select
          id="mes-destaque"
          value={month || ''}
          onChange={e => setMonth(e.target.value)}
          disabled={syncing}
          className="bg-background border border-border text-foreground rounded-lg px-3 py-1.5 text-sm font-bold focus:ring-2 focus:ring-ring outline-none cursor-pointer disabled:opacity-50"
        >
          {meses.map(m => (
            <option key={m} value={monthToYYYYMM(m)}>{m}</option>
          ))}
        </select>
        {isDestaqueAtual && !syncing && (
          <span className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-co-accent/20 text-co-accent border border-co-accent/40">
            <Check size={11} /> atual
          </span>
        )}
      </div>

      <button
        onClick={triggerSync}
        disabled={syncing}
        aria-label="Atualizar dados do Data Warehouse"
        className="flex items-center gap-2 px-3 h-9 rounded-lg bg-background border border-border text-foreground text-xs font-bold hover:ring-2 hover:ring-ring/50 transition-all cursor-pointer disabled:opacity-50"
      >
        <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
        <span className="hidden sm:inline">{syncing ? 'Sincronizando DW...' : 'Atualizar do DW'}</span>
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