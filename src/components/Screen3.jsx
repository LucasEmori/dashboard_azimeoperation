import { useData, useMonth } from '../App.jsx'
import { resolveTela3Month } from '../utils/dataResolver.js'
import { Calendar, CheckCircle, Clock, Send } from 'lucide-react'
import KPIRow from './KPIRow.jsx'

export default function Screen3({ company }) {
  const data = useData()
  const t3 = resolveTela3Month(data, company)

  if (!t3) {
    return (
      <div className={`co-${company}`}>
        <section className="flex items-center gap-2 mb-4">
          <Calendar size={22} className="text-co-accent" />
          <h2 className="text-2xl font-bold text-foreground">Próximos Lançamentos</h2>
        </section>
        <div className="text-center py-12 text-foreground/50 border border-dashed border-border rounded-xl">
          Nenhum dado de planejamento disponível.
        </div>
      </div>
    )
  }

  const items = t3.itens || []
  const ok = t3.status_ok || 0
  const proc = t3.status_processo || 0

  const kpis = [
    { label: 'Itens Programados', value: t3.total_itens || 0, highlight: true, icon: <Calendar size={20} /> },
    { label: 'Status OK', value: ok, valueClass: 'text-green-500', icon: <CheckCircle size={20} /> },
    { label: 'Em Processo', value: proc, valueClass: proc ? 'text-red-500' : '', icon: <Clock size={20} /> },
    { label: 'MKT Enviado', value: t3.mkt_ok || 0, sub: `Pendente: ${t3.mkt_processo || 0}`, icon: <Send size={20} /> },
  ]

  return (
    <div className={`co-${company}`}>
      <section className="flex items-center gap-2 mb-4">
        <Calendar size={22} className="text-co-accent" />
        <h2 className="text-2xl font-bold text-foreground">Próximos Lançamentos</h2>
        <span className="ml-auto px-3 py-1 rounded-full text-xs font-bold bg-co-accent/20 text-co-accent border border-co-accent/40">
          {t3.mes}
        </span>
      </section>

      <KPIRow kpis={kpis} />

      {/* Month header */}
      <div className="flex items-center gap-2 text-lg font-bold text-foreground mb-4">
        <Calendar size={19} className="text-co-accent" />
        {t3.mes}
        <span className="text-sm font-medium opacity-65 ml-1.5">
          {t3.total_itens} itens • {ok} prontos • {proc} em processo
        </span>
      </div>

      {/* Items list */}
      <div className="flex flex-col gap-2.5 mb-5">
        {items.length === 0 && (
          <div className="text-sm text-foreground/60 py-6 text-center">Nenhum lançamento programado.</div>
        )}
        {items.map((it, i) => (
          <PlanItem key={i} item={it} />
        ))}
      </div>

      {/* Total card */}
      <div className="p-4 bg-co-accent/10 border border-co-accent/30 rounded-xl">
        <div className="text-sm opacity-70 text-foreground">Total do Mês</div>
        <div className="text-[28px] font-extrabold text-foreground mt-1">{t3.total_itens} itens</div>
        <div className="flex gap-5 mt-2 text-sm text-foreground/80">
          <span>
            <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1.5 align-middle" />
            {ok} Prontos
          </span>
          <span>
            <span className="inline-block w-2 h-2 rounded-full bg-yellow-400 mr-1.5 align-middle" />
            {proc} Em processo
          </span>
        </div>
      </div>
    </div>
  )
}

function PlanItem({ item }) {
  const statusOK = item.status === 'OK'
  const statusClass = statusOK ? 'border-green-500/40 bg-green-500/8' : 'border-yellow-400/40 bg-yellow-400/8'
  const mktOK = item.mkt === 'OK'

  return (
    <div className={`flex items-center gap-3 px-4 py-3.5 rounded-xl border ${statusClass} bg-background/50`}>
      <div className="min-w-0 flex-1">
        <div className="text-[15px] font-semibold text-foreground">{item.descricao}</div>
        <div className="text-xs opacity-70 text-foreground/70 mt-0.5">
          {item.data}{item.embarque && <> • Embarque {item.embarque}</>}
        </div>
      </div>
      <div className="flex items-center gap-1.5 flex-shrink-0">
        <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
          statusOK ? 'bg-green-500/30 text-green-200' : 'bg-yellow-400/30 text-yellow-200'
        }`}>
          {statusOK ? 'Pronto' : 'Em processo'}
        </span>
        <span className={`px-2 py-1 rounded-md text-[10px] font-bold ${
          mktOK ? 'bg-green-500/30 text-green-200' : 'bg-yellow-400/30 text-yellow-200'
        }`}>
          {mktOK ? 'MKT enviado' : 'MKT pendente'}
        </span>
      </div>
    </div>
  )
}