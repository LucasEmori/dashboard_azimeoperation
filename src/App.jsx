import { useState, useEffect, createContext, useContext } from 'react'
import Dashboard from './Dashboard.jsx'

export const ThemeContext = createContext()
export const DataContext = createContext()
export const MonthContext = createContext()

export function useTheme() { return useContext(ThemeContext) }
export function useData() { return useContext(DataContext) }
export function useMonth() { return useContext(MonthContext) }

export default function App() {
  const [dark, setDark] = useState(true)
  const [data, setData] = useState(null)
  const [month, setMonth] = useState(null) // 'YYYY-MM'
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  function loadMonth(m) {
    setLoading(true)
    setError(null)
    const url = m ? `/api/data?month=${m}` : '/api/data?month=' + new Date().toISOString().slice(0, 7)
    fetch(url)
      .then(r => r.json())
      .then(d => {
        if (d.error) throw new Error(d.error)
        setData(d)
        if (!m && d.meta?.destaque_iso) {
          setMonth(d.meta.destaque_iso.substring(0, 7))
        }
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadMonth(month) }, [month])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground gap-3 px-4 text-center">
        <div className="text-lg font-bold text-destructive">Erro ao consultar o Data Warehouse</div>
        <div className="text-sm opacity-70 max-w-md">{error}</div>
        <button
          onClick={() => loadMonth(month)}
          className="mt-2 px-4 py-2 rounded-lg bg-co-accent text-white font-bold"
        >
          Tentar novamente
        </button>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="animate-pulse text-lg font-bold opacity-60">Carregando dados vivos do DW...</div>
      </div>
    )
  }

  return (
    <ThemeContext.Provider value={{ dark, setDark, toggle: () => setDark(d => !d) }}>
      <DataContext.Provider value={data}>
        <MonthContext.Provider value={{ month, setMonth, loading, refresh: () => loadMonth(month) }}>
          <Dashboard />
        </MonthContext.Provider>
      </DataContext.Provider>
    </ThemeContext.Provider>
  )
}