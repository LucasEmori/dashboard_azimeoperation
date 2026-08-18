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
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)

  // Carrega data.json local (rapido — sem DW)
  function loadData() {
    setLoading(true)
    setError(null)
    fetch('/api/data')
      .then(r => r.json())
      .then(d => {
        if (d.error) throw new Error(d.error)
        setData(d)
        if (!month && d.meta?.destaque_iso) {
          setMonth(d.meta.destaque_iso.substring(0, 7))
        }
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  // Dispara sync DW em background; polling status
  function triggerSync() {
    setSyncing(true)
    fetch('/api/sync', { method: 'POST' })
      .then(() => pollStatus())
      .catch(e => { setSyncing(false); setError(e.message) })
  }

  function pollStatus() {
    const interval = setInterval(() => {
      fetch('/api/status')
        .then(r => r.json())
        .then(s => {
          if (s.state === 'idle') {
            clearInterval(interval)
            setSyncing(false)
            if (s.error) setError(s.error)
            else loadData() // recarrega data.json recém-atualizado
          }
        })
        .catch(() => {})
    }, 2000)
  }

  useEffect(() => { loadData() }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  if (error && !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground gap-3 px-4 text-center">
        <div className="text-lg font-bold text-destructive">Erro ao carregar dados</div>
        <div className="text-sm opacity-70 max-w-md">{error}</div>
        <button onClick={loadData} className="mt-2 px-4 py-2 rounded-lg bg-co-accent text-white font-bold">
          Tentar novamente
        </button>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="animate-pulse text-lg font-bold opacity-60">Carregando...</div>
      </div>
    )
  }

  return (
    <ThemeContext.Provider value={{ dark, setDark, toggle: () => setDark(d => !d) }}>
      <DataContext.Provider value={data}>
        <MonthContext.Provider value={{ month, setMonth, loading, syncing, triggerSync }}>
          {error && (
            <div className="fixed top-4 right-4 z-50 px-4 py-2 rounded-lg bg-destructive/10 border border-destructive/40 text-destructive text-sm font-bold">
              Última sync falhou: {error}
            </div>
          )}
          <Dashboard />
        </MonthContext.Provider>
      </DataContext.Provider>
    </ThemeContext.Provider>
  )
}