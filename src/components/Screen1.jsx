import { useData, useMonth } from '../App.jsx'
import { resolveTela1Month } from '../utils/dataResolver.js'
import { fmtInt } from '../utils/format.js'
import { FolderKanban, Box, Users, Package } from 'lucide-react'
import KPIRow from './KPIRow.jsx'
import TrimesterCharts from './TrimesterCharts.jsx'

const ICONS = {
  notas: <FolderKanban size={20} />,
  skus: <Box size={20} />,
  fornecedor: <Users size={20} />,
  unidades: <Package size={20} />,
}

export default function Screen1({ company }) {
  const data = useData()
  const { month } = useMonth()
  const t1 = resolveTela1Month(data, company, month)
  if (!t1) {
    return (
      <div className={`co-${company}`}>
        <section className="flex items-center gap-2 mb-4">
          {ICONS.notas}
          <h2 className="text-2xl font-bold text-foreground">Notas de Entrada</h2>
          <span className="ml-auto px-3 py-1 rounded-full text-xs font-bold bg-co-accent/20 text-co-accent border border-co-accent/40">
            {month}
          </span>
        </section>
        <div className="text-center py-12 text-foreground/50 border border-dashed border-border rounded-xl">
          Nenhum dado disponível para este mês.
        </div>
      </div>
    )
  }
  const d = t1.destaque
  const displayMonth = d.mes

  const topForn = d.sku_por_fornecedor?.[0] || {}

  const kpis = [
    { label: 'Notas Emitidas', value: d.notas_emitidas, highlight: true, icon: ICONS.notas },
    { label: 'Total de SKUs únicos', value: fmtInt(d.sku_total), sub: `${d.sku_por_nota.toFixed(0)} SKU/nota em média`, icon: ICONS.skus },
    { label: 'Top Fornecedor', value: topForn.skus || '—', sub: topForn.fornecedor || '—', icon: ICONS.fornecedor },
    { label: 'Unidades Recebidas', value: fmtInt(d.unidades_recebidas), icon: ICONS.unidades },
  ]

  return (
    <div className={`co-${company}`}>
      <section className="flex items-center gap-2 mb-4">
        {ICONS.notas}
        <h2 className="text-2xl font-bold text-foreground">Notas de Entrada</h2>
        <span className="ml-auto px-3 py-1 rounded-full text-xs font-bold bg-co-accent/20 text-co-accent border border-co-accent/40">
          {displayMonth}
        </span>
      </section>

      <KPIRow kpis={kpis} />

      <TrimesterCharts company={company} />
    </div>
  )
}