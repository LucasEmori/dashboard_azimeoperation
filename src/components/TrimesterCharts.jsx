import { useState } from 'react'
import { useData, useTheme, useMonth } from '../App.jsx'
import { resolveTela1Month } from '../utils/dataResolver.js'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { fmtInt } from '../utils/format.js'

export default function TrimesterCharts({ company }) {
  const data = useData()
  const { dark } = useTheme()
  const { month } = useMonth()
  const t1 = resolveTela1Month(data, company, month)
  const trimestres = t1?.trimestres || {}

  // Filter trimesters with actual data (notas > 0; meses zerados nao contam)
  const validTrims = ['T1', 'T2', 'T3', 'T4'].filter(
    k => (trimestres[k]?.meses || []).some(m => m.notas_emitidas > 0)
  )

  // Default to the last available trimester; fallback se troca de mes invalida selecao
  const [selectedTrim, setSelectedTrim] = useState(validTrims[validTrims.length - 1] || null)
  const activeTrim = validTrims.includes(selectedTrim) ? selectedTrim : (validTrims[validTrims.length - 1] || null)

  if (!activeTrim) return null

  const accentHex = company === 'alinare' ? (dark ? '#60A5FA' : '#1E40AF') : (dark ? '#D7A9A9' : '#A07A7A')
  const txtColor = dark ? '#E8EDF5' : '#1a2233'

  // Data for chart 1 (Months)
  const c1Data = trimestres[activeTrim].meses.map(m => ({
    name: m.mes.split(' ')[0],
    value: m.unidades_recebidas,
    notas: m.notas_emitidas
  }))

  // Data for chart 2 (Compare Trimesters)
  const c2Data = validTrims.map(k => ({
    name: trimestres[k].label,
    value: trimestres[k].total_unidades
  }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border p-3 rounded-lg shadow-lg">
          <p className="font-bold text-foreground mb-1">{label}</p>
          <p className="text-sm text-foreground/80">Unidades: <b className="text-foreground">{fmtInt(payload[0].value)}</b></p>
        </div>
      )
    }
    return null
  }

  const CustomLabel = ({ x, y, width, value }) => {
    return (
      <text x={x + width / 2} y={y - 8} fill={txtColor} fontSize={10} textAnchor="middle">
        {fmtInt(value)}
      </text>
    )
  }

  return (
    <div>
      <h3 className="text-base font-bold text-foreground mb-3">Unidades Recebidas por Trimestre</h3>
      <div className="mb-4 w-64">
        <label className="block text-sm font-bold text-foreground mb-2">Trimestre</label>
        <select
          value={activeTrim}
          onChange={e => setSelectedTrim(e.target.value)}
          className="w-full bg-background border border-border text-foreground rounded-lg p-2 font-medium focus:ring-2 focus:ring-ring outline-none"
        >
          {validTrims.map(k => (
            <option key={k} value={k}>{trimestres[k].label}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Chart 1 */}
        <div className="h-[360px] w-full">
          <h3 className="text-center font-bold text-foreground text-sm mb-4">{trimestres[activeTrim].label}</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={c1Data} margin={{ top: 20, right: 10, left: 50, bottom: 60 }}>
              <XAxis
                dataKey="name"
                axisLine={{ stroke: txtColor, strokeWidth: 1 }}
                tickLine={{ stroke: txtColor, strokeWidth: 1 }}
                tick={{ fill: txtColor, fontSize: 11 }}
                label={{ value: 'Mês', position: 'insideBottom', offset: -40, fill: txtColor, fontSize: 12 }}
              />
              <YAxis
                axisLine={{ stroke: txtColor, strokeWidth: 1 }}
                tickLine={{ stroke: txtColor, strokeWidth: 1 }}
                tick={{ fill: txtColor, fontSize: 10 }}
              />
              <CartesianGrid stroke={txtColor} strokeOpacity={0.1} vertical={false} />
              <Tooltip cursor={{ fill: 'transparent' }} content={<CustomTooltip />} />
              <Bar dataKey="value" fill={accentHex} radius={[4, 4, 0, 0]} barSize={56} maxBarSize={64} label={<CustomLabel />} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 2 */}
        <div className="h-[360px] w-full">
          <h3 className="text-center font-bold text-foreground text-sm mb-4">Comparativo Trimestral</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={c2Data} margin={{ top: 20, right: 10, left: 50, bottom: 60 }}>
              <XAxis
                dataKey="name"
                axisLine={{ stroke: txtColor, strokeWidth: 1 }}
                tickLine={{ stroke: txtColor, strokeWidth: 1 }}
                tick={{ fill: txtColor, fontSize: 11 }}
                label={{ value: 'Trimestre', position: 'insideBottom', offset: -40, fill: txtColor, fontSize: 12 }}
              />
              <YAxis
                axisLine={{ stroke: txtColor, strokeWidth: 1 }}
                tickLine={{ stroke: txtColor, strokeWidth: 1 }}
                tick={{ fill: txtColor, fontSize: 10 }}
              />
              <CartesianGrid stroke={txtColor} strokeOpacity={0.1} vertical={false} />
              <Tooltip cursor={{ fill: 'transparent' }} content={<CustomTooltip />} />
              <Bar dataKey="value" fill={accentHex} radius={[4, 4, 0, 0]} barSize={56} maxBarSize={64} label={<CustomLabel />}>
                {c2Data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.name === trimestres[activeTrim].label ? accentHex : `${accentHex}88`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}