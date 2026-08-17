import { useState, useEffect, createContext, useContext } from 'react'
import Dashboard from './Dashboard.jsx'

export const ThemeContext = createContext()
export const DataContext = createContext()

export function useTheme() { return useContext(ThemeContext) }
export function useData() { return useContext(DataContext) }

export default function App() {
  const [dark, setDark] = useState(true)
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/data.json')
      .then(r => r.json())
      .then(setData)
      .catch(console.error)
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="animate-pulse text-lg opacity-60">Carregando dados...</div>
      </div>
    )
  }

  return (
    <ThemeContext.Provider value={{ dark, setDark, toggle: () => setDark(d => !d) }}>
      <DataContext.Provider value={data}>
        <Dashboard />
      </DataContext.Provider>
    </ThemeContext.Provider>
  )
}