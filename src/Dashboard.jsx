import { useState } from 'react'
import { useData, useTheme } from './App.jsx'
import TopBar from './components/TopBar.jsx'
import BrandBand from './components/BrandBand.jsx'
import Screen1 from './components/Screen1.jsx'
import Screen2 from './components/Screen2.jsx'
import Screen3 from './components/Screen3.jsx'

const TABS = ['Notas de Entrada', 'Produtos Lançados', 'Próximos Lançamentos']
const COMPANIES = ['alinare', 'novitah']
const LABELS = { alinare: 'ALINARE', novitah: 'NOVITAH' }

export default function Dashboard() {
  const data = useData()
  const { dark } = useTheme()
  const [activeCompany, setActiveCompany] = useState('alinare')
  const [activeScreen, setActiveScreen] = useState(0)

  const meta = data.meta

  return (
    <div className="max-w-[1400px] mx-auto px-3 pb-8 font-sans">
      <TopBar meta={meta} company={activeCompany} />

      {/* Company tabs — centered */}
      <div className="flex justify-center items-center gap-2 mb-4">
        {COMPANIES.map(c => (
          <button
            key={c}
            onClick={() => { setActiveCompany(c); setActiveScreen(0) }}
            className={`px-8 py-3 rounded-xl text-base font-bold transition-all duration-200 border
              ${activeCompany === c
                ? 'bg-muted text-foreground shadow-lg shadow-co-accent/10 border-co-accent/40'
                : 'bg-muted/60 text-foreground/80 border-border hover:bg-muted hover:text-foreground'
              }`}
          >
            {LABELS[c]}
          </button>
        ))}
      </div>

      {/* Brand band */}
      <BrandBand company={activeCompany} meta={meta} />

      {/* Sub-tabs */}
      <div className="flex gap-1.5 bg-muted rounded-xl p-2 mb-5 border border-border">
        {TABS.map((t, i) => (
          <button
            key={i}
            onClick={() => setActiveScreen(i)}
            className={`flex-1 py-2 px-5 rounded-lg text-sm font-bold transition-all duration-200 border border-transparent
              ${activeScreen === i
                ? 'bg-background text-foreground shadow-sm border-border'
                : 'bg-background/40 text-foreground/75 hover:text-foreground hover:bg-background/80'
              }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeScreen === 0 && <Screen1 company={activeCompany} />}
      {activeScreen === 1 && <Screen2 company={activeCompany} />}
      {activeScreen === 2 && <Screen3 company={activeCompany} />}

      <div className="text-center text-xs text-muted mt-8 opacity-50">
        Dados processados em: {meta.hoje} • Fonte: output/data.json
      </div>
    </div>
  )
}