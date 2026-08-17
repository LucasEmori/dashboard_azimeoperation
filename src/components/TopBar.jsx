import { useTheme } from '../App.jsx'
import { Sun, Moon } from 'lucide-react'

export default function TopBar({ meta }) {
  const { dark, toggle } = useTheme()

  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3 mt-2 mb-3 bg-muted rounded-xl border border-border">
      <div className="text-sm text-foreground/70 leading-relaxed">
        Destaque: <b className="text-foreground">{meta.destaque}</b>
        <span className="mx-2 opacity-40">|</span>
        Comparativo: <b className="text-foreground">{meta.comparacao.join(', ')}</b>
        {meta.destaque_ano_passado && (
          <>
            <span className="mx-2 opacity-40">|</span>
            Ano anterior: <b className="text-foreground">{meta.destaque_ano_passado}</b>
          </>
        )}
        <span className="mx-2 opacity-40">|</span>
        Planejamento: <b className="text-foreground">{meta.proximo_mes}</b>
      </div>

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