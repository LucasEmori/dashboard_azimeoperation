const LABELS = { alinare: 'ALINARE', novitah: 'NOVITAH' }

export default function BrandBand({ company, meta }) {
  return (
    <div className={`co-${company} band-${company} flex items-center gap-4 px-6 py-4 rounded-2xl mb-5 shadow-xl shadow-black/20`}>
      <img
        src={`/${company}_logo.jpg`}
        alt={LABELS[company]}
        className="w-[52px] h-[52px] rounded-xl object-cover border-2 border-white/35 bg-white/10"
      />
      <span className="text-[28px] font-extrabold tracking-wide text-white">{LABELS[company]}</span>
      <div className="ml-auto text-right text-xs text-white/80 leading-relaxed hidden sm:block">
        Mês destaque: <b>{meta.destaque}</b><br />
        Comparativo: <b>{meta.comparacao.join(', ')}</b><br />
        Ano anterior: <b>{meta.destaque_ano_passado}</b>
      </div>
    </div>
  )
}