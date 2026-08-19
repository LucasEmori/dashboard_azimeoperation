export default function KPIRow({ kpis }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-3.5 mb-4 sm:mb-6">
      {kpis.map((kpi, i) => (
        <div
          key={i}
          className={`relative p-3.5 sm:p-5 rounded-xl border flex flex-col justify-center min-h-[76px] sm:min-h-0 ${
            kpi.highlight
              ? 'bg-co-accent/10 border-co-accent/40 shadow-xl shadow-black/5 border-l-4 border-l-co-accent'
              : 'bg-background border-border border-l-4 border-l-co-accent'
          }`}
        >
          <div className="text-[10px] sm:text-xs uppercase tracking-wider text-muted-foreground opacity-70 mb-1.5 sm:mb-2 flex items-center gap-1.5 sm:gap-2">
            {kpi.icon && <span className="text-co-accent [&>svg]:w-4 [&>svg]:h-4 sm:[&>svg]:w-5 sm:[&>svg]:h-5">{kpi.icon}</span>}
            <span className="truncate">{kpi.label}</span>
          </div>
          <div className={`text-2xl sm:text-[42px] leading-none font-extrabold tabular-nums ${kpi.valueClass || 'text-foreground'}`}>
            {kpi.value}
          </div>
          {kpi.sub && (
            <div className="text-[10px] sm:text-xs opacity-65 mt-1 sm:mt-1.5 text-muted-foreground">
              {kpi.sub}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}