import { useData, useMonth } from '../App.jsx'
import { resolveTela2Month } from '../utils/dataResolver.js'
import { fmtInt, fmtMedia, deltaPct, monthShort, yearOf } from '../utils/format.js'
import { CheckCircle, BarChart3, TrendingUp, Calendar, Hash } from 'lucide-react'
import KPIRow from './KPIRow.jsx'
import VolumeChart from './VolumeChart.jsx'

const ICONS = {
  prazo: <Calendar size={20} />,
  skus: <Hash size={20} />,
  pico: <TrendingUp size={20} />,
  lancamentos: <CheckCircle size={20} />,
}

export default function Screen2({ company }) {
  const data = useData()
  const { month } = useMonth()
  const t2 = resolveTela2Month(data, company, month)
  if (!t2) {
    return (
      <div className={`co-${company}`}>
        <section className="flex items-center gap-2 mb-4">
          <CheckCircle size={22} className="text-co-accent" />
          <h2 className="text-2xl font-bold text-foreground">Produtos Lançados</h2>
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

  const d = t2.destaque
  const comps = t2.comparacao || []
  // ano_anterior no formato atual é mês anterior (ou nulo)
  const ano = t2.ano_anterior || {}


  const md = d.media_prazo
  const mdStr = fmtMedia(md)
  const mdCls = md !== null && md >= 0 ? 'text-green-500' : 'text-red-500'
  const dia = d.dia_pico || {}

  const kpis = [
    { label: 'Média de Prazo', value: mdStr, sub: 'Data → Lançamento', highlight: true, valueClass: mdCls, icon: ICONS.prazo },
    { label: "SKU's Únicos", value: d.skus || 0, icon: ICONS.skus },
    { label: 'Dia de Pico', value: dia.data || '—', sub: dia.dia_semana || '', icon: ICONS.pico },
    { label: 'Lançamentos Realizados', value: d.lancamentos_realizados || 0, icon: ICONS.lancamentos },
  ]

  const hasAno = ano && ano.lancamentos > 0

  return (
    <div className={`co-${company}`}>
      <section className="flex items-center gap-2 mb-4">
        <CheckCircle size={20} className="text-co-accent flex-shrink-0 sm:hidden" />
        <CheckCircle size={22} className="text-co-accent flex-shrink-0 hidden sm:block" />
        <h2 className="text-lg sm:text-2xl font-bold text-foreground truncate">Produtos Lançados</h2>
        <span className="ml-auto px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-xs font-bold bg-co-accent/20 text-co-accent border border-co-accent/40 flex-shrink-0">
          {d.mes}
        </span>
      </section>

      <KPIRow kpis={kpis} />

      {hasAno && (
        <div className="bg-co-accent/5 border border-co-accent/20 rounded-2xl p-3 sm:p-5 mb-4 sm:mb-6">
          <div className="flex items-center gap-2 text-xs sm:text-sm font-bold text-foreground mb-3 sm:mb-4">
            <BarChart3 size={18} className="text-co-accent flex-shrink-0" />
            <span className="truncate">Ano a Ano • {d.mes} × {ano.mes}</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-4">
            <YoyCard label="SKU's Únicos" now={d.skus} prev={ano.skus} fmt={fmtInt} />
            <YoyCard label="Lançamentos" now={d.lancamentos_realizados} prev={ano.lancamentos_realizados} fmt={fmtInt} />
            <YoyCard label="Média Prazo" now={d.media_prazo} prev={ano.media_prazo} fmt={fmtMedia} />
          </div>
        </div>
      )}

      {(comps.length > 0 || hasAno) && (
        <>
          <div className="flex items-center gap-2 text-sm sm:text-base font-bold text-foreground/80 mb-3 mt-2">
            <BarChart3 size={18} className="text-co-accent" /> Comparativo — Meses Anteriores
          </div>
          <div className={`grid grid-cols-2 sm:grid-cols-3 md:grid-cols-${hasAno ? '4' : '3'} gap-2 sm:gap-3 mb-6`}>
            {comps.map((c, i) => (
              <CompCard
                key={i}
                month={c.mes}
                rows={[
                  { label: 'Lançamentos Realizados', value: c.lancamentos_realizados || 0 },
                  { label: 'Média Dias', value: fmtMedia(c.media_prazo) }
                ]}
              />
            ))}
            {hasAno && (
              <CompCard
                month={ano.mes}
                yearPrev
                rows={[
                  { label: 'Lançamentos Realizados', value: ano.lancamentos_realizados || 0 },
                  { label: 'SKUs', value: ano.skus || 0 },
                  { label: 'Média Dias', value: fmtMedia(ano.media_prazo) }
                ]}
              />
            )}
          </div>
        </>
      )}

      <VolumeChart company={company} destaque={d} ano={ano} />
    </div>
  )
}

function YoyCard({ label, now, prev, fmt }) {
  const nowStr = now !== null ? fmt(now) : '—'
  const prevStr = prev !== null ? fmt(prev) : '—'
  const delta = deltaPct(now, prev)

  return (
    <div className="bg-background rounded-xl p-3 sm:p-4 shadow-sm border border-border">
      <div className="text-[10px] sm:text-xs uppercase tracking-wide text-foreground/60 mb-1.5 sm:mb-2">{label}</div>
      <div className="flex items-baseline flex-wrap gap-1.5 sm:gap-2">
        <span className="text-2xl sm:text-3xl font-extrabold text-foreground">{nowStr}</span>
        <span className="text-[10px] sm:text-xs text-foreground/50">vs {prevStr} (ano ant.)</span>
      </div>
      <div className="mt-1.5 sm:mt-2">
        {delta === null ? (
          <span className="text-xs sm:text-sm font-bold text-foreground/50">—</span>
        ) : (
          <span className={`text-xs sm:text-sm font-bold ${delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {delta >= 0 ? '▲' : '▼'} {delta > 0 ? '+' : ''}{delta.toFixed(1)}%
          </span>
        )}
      </div>
    </div>
  )
}

function CompCard({ month, rows, yearPrev }) {
  return (
    <div className={`rounded-xl p-2.5 sm:p-4 border bg-background/50 ${
      yearPrev
        ? 'border-t-[3px] border-t-yellow-400/60 border-dashed bg-yellow-400/5'
        : 'border-t-[3px] border-t-co-accent/50'
    }`}>
      <div className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm font-bold text-foreground mb-2 sm:mb-3 capitalize">
        {monthShort(month)}
        {yearPrev && <span className="text-[9px] sm:text-[10px] bg-yellow-400/20 text-yellow-600 dark:text-yellow-200 px-1.5 sm:px-2 py-0.5 rounded-full">{yearOf(month)}</span>}
      </div>
      {rows.map((r, i) => (
        <div key={i} className={i > 0 ? 'mt-1.5 sm:mt-2' : ''}>
          <div className="text-[9px] sm:text-[11px] text-foreground/60">{r.label}</div>
          <div className="text-lg sm:text-xl font-bold text-foreground">{r.value}</div>
        </div>
      ))}
    </div>
  )
}