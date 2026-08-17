import { useData, useMonth } from '../App.jsx'
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
  const t1 = data[company].tela1
  const d = t1.destaque

  // Mês na tela1 é sempre o destaque fixo (pq não há base por mês de comparativo nela)
  // Se o mês selecionado não for o destaque, mostramos aviso, mas preservamos a base dos trimestres e KPI destaque.
  const isSelectedDestaque = month === d.mes
  const displayMonth = isSelectedDestaque ? d.mes : `${month} (Visualizando base ${d.mes})`

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