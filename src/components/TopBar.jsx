import { useTheme, useMonth, useData } from '../App.jsx'
import { monthToYYYYMM } from '../utils/format.js'
import { Sun, Moon, CalendarDays, RefreshCw, Check } from 'lucide-react'

export default function TopBar({ meta, company }) {
  const { dark, toggle } = useTheme()
  const { month, setMonth, syncing, triggerSync } = useMonth()
  const data = useData()

  // Meses disponíveis vêm da lista calculada no backend
  const meses = meta?.months || []
  const isDestaqueAtual = month === meta?.destaque_iso?.substring(0, 7)

  return (
    <div className="flex items-center justify-between gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 sm:py-3 mt-2 mb-3 bg-muted rounded-xl border border-border flex-wrap">
      <div className="flex items-center gap-1.5 sm:gap-2 min-w-0 flex-1">
        <CalendarDays size={16} className="text-co-accent flex-shrink-0" />
        <label htmlFor="mes-destaque" className="text-xs sm:text-sm font-bold text-foreground whitespace-nowrap">Mês:</label>
        <select
          id="mes-destaque"
          value={month || ''}
          onChange={e => setMonth(e.target.value)}
          disabled={syncing}
          className="min-w-0 flex-1 sm:flex-none bg-background border border-border text-foreground rounded-lg px-2 sm:px-3 py-1.5 text-xs sm:text-sm font-bold focus:ring-2 focus:ring-ring outline-none cursor-pointer disabled:opacity-50"
        >
          {meses.map(m => (
            <option key={m} value={m}>{meta?.month_labels?.[m] || m}</option>
          ))}
        </select>
        {isDestaqueAtual && !syncing && (
          <span className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-co-accent/20 text-co-accent border border-co-accent/40">
            <Check size={11} /> atual
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        <button
          onClick={triggerSync}
          disabled={syncing}
          aria-label="Atualizar dados do Data Warehouse"
          className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 h-8 sm:h-9 rounded-lg bg-background border border-border text-foreground text-xs font-bold hover:ring-2 hover:ring-ring/50 transition-all cursor-pointer disabled:opacity-50"
        >
          <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
          <span className="hidden md:inline">{syncing ? 'Sincronizando...' : 'Atualizar DW'}</span>
        </button>

        <button
          onClick={toggle}
          aria-label={dark ? 'Ativar tema claro' : 'Ativar tema escuro'}
          className="flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-background border border-border text-foreground hover:ring-2 hover:ring-ring/50 transition-all duration-200 cursor-pointer flex-shrink-0"
        >
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </div>
  )
}