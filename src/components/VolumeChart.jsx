import { useTheme } from '../App.jsx'
import { AreaChart, Area, Line, ComposedChart, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import { yearOf } from '../utils/format.js'
import { BarChart3 } from 'lucide-react'

const ACCENT_RGB = { alinare: '121,134,203', novitah: '215,169,169' }

export default function VolumeChart({ company, destaque, ano }) {
  const { dark } = useTheme()
  const cur = destaque.volume_diario || []
  const prev = ano.volume_diario || []

  // Se ambos vazios, mostra mensagem em vez de gráfico vazio
  const bothEmpty = cur.length === 0 && prev.length === 0
  if (bothEmpty) {
    return (
      <div className="mt-6">
        <div className="flex items-center gap-2 text-base font-bold text-foreground/80 mb-3">
          <BarChart3 size={18} className="text-co-accent" />
          Volume Acumulado — {destaque.mes} × {ano.mes}
        </div>
        <div className="h-[220px] w-full bg-background/30 rounded-xl border border-dashed border-border flex flex-col items-center justify-center text-foreground/50">
          <BarChart3 size={28} className="mb-2 opacity-40" />
          <p className="text-sm font-medium">Volume diário indisponível para este mês.</p>
          <p className="text-xs mt-1 opacity-60">Dados disponíveis apenas no mês destaque.</p>
        </div>
      </div>
    )
  }

  // Constrói chartData com o que disponível
  const curMap = Object.fromEntries(cur.map(d => [d.dia, d.count]))
  const prevMap = Object.fromEntries(prev.map(d => [d.dia, d.count]))
  const allDays = new Set([...Object.keys(curMap).map(Number), ...Object.keys(prevMap).map(Number)])
  const maxDay = Math.max(...allDays, 0)

  let rc = 0, rp = 0
  const chartData = []
  for (let d = 1; d <= maxDay; d++) {
    const dc = curMap[d] || 0
    const dp = prevMap[d] || 0
    rc += dc
    rp += dp
    chartData.push({
      dia: String(d).padStart(2, '0'),
      atual: cur.length > 0 ? rc : null,
      anterior: prev.length > 0 ? rp : null,
      atualDia: dc,
      anteriorDia: dp,
    })
  }

  const rgb = ACCENT_RGB[company] || ACCENT_RGB.alinare
  const txtColor = dark ? '#E8EDF5' : '#1a2233'
  const gridColor = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)'

  const hasCur = cur.length > 0
  const hasPrev = prev.length > 0
  const hasBoth = hasCur && hasPrev

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border p-3 rounded-lg shadow-lg text-sm">
          <p className="font-bold text-foreground mb-2">Dia {label}</p>
          {payload.map((p, i) => {
            if (p.value === null) return null
            return (
              <p key={i} style={{ color: p.color }}>
                {p.name}: <b>{p.value}</b> acum. ({p.payload[p.dataKey === 'atual' ? 'atualDia' : 'anteriorDia']} no dia)
              </p>
            )
          })}
        </div>
      )
    }
    return null
  }

  return (
    <div className="mt-6">
      <div className="flex items-center gap-2 text-base font-bold text-foreground/80 mb-3">
        <BarChart3 size={18} className="text-co-accent" />
        Volume Acumulado — {hasCur ? `${destaque.mes}` : ''} {hasBoth ? '×' : ''} {hasPrev ? `${ano.mes}` : ''}
      </div>
      <div className="h-[420px] w-full bg-background/30 rounded-xl border border-border p-4">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
            <CartesianGrid stroke={gridColor} vertical={false} />
            <XAxis dataKey="dia" tick={{ fill: txtColor, fontSize: 9 }} angle={-45} textAnchor="end" height={40}
                   label={{ value: 'Dia do mês', position: 'insideBottom', offset: -5, fill: txtColor, fontSize: 11 }} />
            <YAxis tick={{ fill: txtColor, fontSize: 10 }}
                   label={{ value: 'Lançamentos acumulados', angle: -90, position: 'insideLeft', fill: txtColor, fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: txtColor, fontSize: 12 }} />
            {hasCur && (
              <Area
                type="monotone" dataKey="atual" name={`${destaque.mes}`}
                stroke={`rgb(${rgb})`} strokeWidth={3}
                fill={`rgba(${rgb},0.08)`}
                dot={{ r: 2, fill: `rgb(${rgb})` }}
              />
            )}
            {hasPrev && (
              <Line
                type="monotone" dataKey="anterior" name={`${ano.mes}`}
                stroke={`rgba(${rgb},0.55)`} strokeWidth={2} strokeDasharray="6 4"
                dot={{ r: 2, fill: `rgba(${rgb},0.65)` }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}