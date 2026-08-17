export default function KPIRow({ kpis }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 mb-6">
      {kpis.map((kpi, i) => (
        <div
          key={i}
          className={`relative p-5 rounded-xl border flex flex-col justify-center ${
            kpi.highlight
              ? 'bg-co-accent/10 border-co-accent/40 shadow-xl shadow-black/5 border-l-4 border-l-co-accent'
              : 'bg-background border-border border-l-4 border-l-co-accent'
          }`}
        >
          <div className="text-xs uppercase tracking-wider text-muted-foreground opacity-70 mb-2 flex items-center gap-2">
            {kpi.icon && <span className="text-co-accent">{kpi.icon}</span>}
            {kpi.label}
          </div>
          <div className={`text-[42px] leading-none font-extrabold ${kpi.valueClass || 'text-foreground'}`}>
            {kpi.value}
          </div>
          {kpi.sub && (
            <div className="text-xs opacity-65 mt-1.5 text-muted-foreground">
              {kpi.sub}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}