"""Dashboard Alinare & Novitah - Streamlit + Plotly.

Le output/data.json (gerado pelo pipeline). Nao processa planilhas em runtime.
Estrutura: 2 abas de empresa (ALINARE | NOVITAH), cada uma com 3 sub-abas
(Notas de Entrada | Produtos Lancados | Proximos Lancamentos).
Run: streamlit run app.py
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Dashboard - Alinare & Novitah", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON = BASE_DIR / "output" / "data.json"

LABELS = {"alinare": "ALINARE", "novitah": "NOVITAH"}

# ---------------------------------------------------------------------------
# Logos (base64)
# ---------------------------------------------------------------------------
def _logo_b64(company: str) -> str:
    path = BASE_DIR / f"{company}_logo.jpg"
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return ""


_LOGOS = {c: _logo_b64(c) for c in ("alinare", "novitah")}

# ---------------------------------------------------------------------------
# SVG icons (stroke 2px, consistente)
# ---------------------------------------------------------------------------
_SVG = {
    "notas": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>',
    "produtos": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
    "calendario": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "relogio": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "grafico": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "troca": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
}

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
* { box-sizing: border-box; }
html, body, .stApp { font-variant-numeric: tabular-nums; }
.stApp { background: #0a0e1a; color: #e8edf5; }
section[data-testid="stSidebar"] { display: none; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 0 12px 24px !important; max-width: 1400px !important; margin: 0 auto; }

/* ---- Per-empresa: variaveis de cor ---- */
.co-alinare { --accent: #7986cb; --accent-rgb: 121,134,203; --band: linear-gradient(135deg,#1a237e 0%,#283593 100%); }
.co-novitah { --accent: #d7a9a9; --accent-rgb: 215,169,169; --band: linear-gradient(135deg,#a07a7a 0%,#8d6b6b 100%); }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: #121826; padding: 8px 10px; border-radius: 10px;
    border: 1px solid #2a374a; justify-content: center;
}
.stTabs [data-baseweb="tab"] {
    padding: 8px 22px; font-size: 13px; font-weight: 700; letter-spacing: .3px;
    color: #8b9cb5; background: transparent; border-radius: 8px;
}
.stTabs [data-baseweb="tab"]:hover { color: #fff; background: rgba(255,255,255,0.05); }
.stTabs [aria-selected="true"] { color: #fff !important; background: #2a3a52 !important; }
.stTabs [data-baseweb="tab-border"], .stTabs [data-baseweb="tab-highlight"] { display: none; }
/* Abas externas (empresa) maiores */
.outer-tabs .stTabs [data-baseweb="tab"] { font-size: 16px; padding: 12px 40px; }

/* ---- Brand band ---- */
.brand-band {
    background: var(--band); padding: 18px 26px; border-radius: 14px;
    display: flex; align-items: center; gap: 16px; margin: 14px 0 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.brand-band .logo-img {
    width: 52px; height: 52px; border-radius: 10px; object-fit: cover;
    border: 2px solid rgba(255,255,255,0.35); background: rgba(255,255,255,0.12);
}
.brand-band .company-name { font-size: 28px; font-weight: 800; letter-spacing: 1px; color: #fff; }
.brand-band .brand-sub { margin-left: auto; font-size: 12px; color: rgba(255,255,255,0.82); text-align: right; line-height: 1.5; }

/* ---- Section title ---- */
.section-title {
    font-size: 22px; font-weight: 700; margin: 4px 0 16px; color: #fff;
    display: flex; align-items: center; gap: 10px;
}
.section-title svg { width: 22px; height: 22px; color: var(--accent); }
.section-title .pill {
    margin-left: auto; font-size: 12px; font-weight: 700; letter-spacing: .4px;
    background: rgba(var(--accent-rgb),0.22); color: #fff;
    padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(var(--accent-rgb),0.4);
}

/* ---- KPI cards ---- */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }
.kpi {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--accent); border-radius: 12px; padding: 20px;
}
.kpi.hl {
    background: rgba(var(--accent-rgb),0.14); border: 1px solid rgba(var(--accent-rgb),0.45);
    box-shadow: 0 8px 22px rgba(0,0,0,0.28);
}
.kpi-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.72; margin-bottom: 8px; color: #cdd9ec; }
.kpi-value { font-size: 42px; font-weight: 800; line-height: 1; color: #fff; }
.kpi-value.green { color: #69f0ae; }
.kpi-value.red { color: #ff8a80; }
.kpi-sub { font-size: 12px; opacity: 0.65; margin-top: 6px; color: #cdd9ec; }

/* ---- Comparison ---- */
.comp-title { font-size: 16px; font-weight: 700; margin: 6px 0 12px; color: #cdd9ec; display: flex; align-items: center; gap: 8px; }
.comp-title svg { width: 17px; height: 17px; color: var(--accent); }
.comp-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 18px; }
.comp-grid.with-ano { grid-template-columns: repeat(4, 1fr); }
.comp-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-top: 3px solid rgba(var(--accent-rgb),0.5); border-radius: 10px; padding: 14px;
}
.comp-card.year-prev { border-top-color: rgba(255,235,150,0.6); background: rgba(255,235,150,0.06); border-style: dashed; }
.comp-month { font-size: 13px; font-weight: 700; margin-bottom: 10px; text-transform: capitalize; color: #fff; display:flex; align-items:center; gap:6px; }
.comp-month .ybadge { font-size: 10px; background: rgba(255,235,150,0.22); color: #fff59d; padding: 2px 7px; border-radius: 10px; font-weight: 700; }
.comp-label { font-size: 11px; opacity: 0.6; color: #cdd9ec; }
.comp-value { font-size: 24px; font-weight: 700; color: #fff; }
.comp-gap { height: 8px; }

/* ---- YoY block ---- */
.yoy {
    background: rgba(var(--accent-rgb),0.08); border: 1px solid rgba(var(--accent-rgb),0.3);
    border-radius: 14px; padding: 18px 20px; margin-bottom: 20px;
}
.yoy-title { font-size: 15px; font-weight: 700; margin-bottom: 14px; color: #fff; display:flex; align-items:center; gap:8px; }
.yoy-title svg { width: 18px; height: 18px; color: var(--accent); }
.yoy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.yoy-card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 14px; }
.yoy-card .yl { font-size: 12px; text-transform: uppercase; letter-spacing: .8px; opacity: 0.7; color: #cdd9ec; margin-bottom: 8px; }
.yoy-now { font-size: 30px; font-weight: 800; color: #fff; }
.yoy-prev { font-size: 13px; opacity: 0.6; color: #cdd9ec; margin-left: 8px; }
.yoy-delta { font-size: 13px; font-weight: 700; margin-top: 6px; }
.yoy-delta.up { color: #69f0ae; }
.yoy-delta.down { color: #ff8a80; }

/* ---- Planning ---- */
.plan-month { font-size: 18px; font-weight: 700; margin-bottom: 16px; color:#fff; display:flex; align-items:center; gap:8px; }
.plan-month svg { width: 19px; height: 19px; color: var(--accent); }
.plan-month .sub { font-size: 13px; font-weight: 500; opacity: 0.65; margin-left: 6px; color:#cdd9ec; }
.plan-list { display: flex; flex-direction: column; gap: 11px; }
.plan-item {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--accent); border-radius: 10px; padding: 13px 16px;
    display: flex; justify-content: space-between; align-items: center; gap: 12px;
}
.plan-item.ready { background: rgba(76,175,80,0.16); border-left-color: #66bb6a; }
.plan-item.process { background: rgba(255,193,7,0.12); border-left-color: #ffca28; }
.plan-name { font-size: 15px; font-weight: 600; color: #fff; }
.plan-meta { font-size: 12px; opacity: 0.7; margin-top: 3px; color: #cdd9ec; }
.plan-badges { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }
.pst { padding: 5px 11px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.pst.ready { background: rgba(76,175,80,0.3); color: #b9f6ca; }
.pst.process { background: rgba(255,193,7,0.3); color: #fff59d; }
.mktb { padding: 4px 9px; border-radius: 6px; font-size: 10px; font-weight: 700; }
.mktb.sent { background: rgba(76,175,80,0.3); color: #b9f6ca; }
.mktb.pending { background: rgba(255,193,7,0.3); color: #fff59d; }
.plan-total { margin-top: 18px; padding: 16px; background: rgba(var(--accent-rgb),0.1); border:1px solid rgba(var(--accent-rgb),0.3); border-radius: 10px; }
.plan-total-value { font-size: 28px; font-weight: 800; margin-top: 4px; color: #fff; }
.plan-total-bd { font-size: 13px; margin-top: 8px; display: flex; gap: 18px; color:#cdd9ec; }
.dot { display: inline-block; margin-right: 4px; }
.dot.ready { color: #b9f6ca; }
.dot.process { color: #fff59d; }

.data-note { font-size: 11px; opacity: 0.4; text-align: center; padding: 14px; color: #9fb0c8; }
.topbar { display:flex; align-items:center; gap:16px; padding: 10px 14px; background:#121826; border:1px solid #2a374a; border-radius:10px; margin: 6px 0 10px; }
.topbar-meta { font-size: 12px; color: #8b9cb5; line-height: 1.6; }
.topbar-meta b { color: #cdd9ec; }

/* ---- Selectbox dark theme + label ---- */
.stSelectbox label, [data-testid="stWidgetLabel"] p {
    color: #e8edf5 !important; font-weight: 700 !important; font-size: 14px !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #1a2335 !important; border-color: #2a374a !important;
    color: #e8edf5 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #e8edf5 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] svg { color: #8b9cb5 !important; }
/* Open dropdown: white bg -> dark text */
[data-baseweb="popover"] [role="option"] { color: #1a2335 !important; }
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"] {
    background: rgba(0,0,0,0.06) !important; color: #1a2335 !important;
}

/* ---- Tablet ---- */
@media (max-width: 900px) {
    .kpi-row { grid-template-columns: repeat(2, 1fr); }
    .comp-grid, .comp-grid.with-ano { grid-template-columns: repeat(2, 1fr); }
    .yoy-grid { grid-template-columns: repeat(2, 1fr); }
    .kpi-value { font-size: 36px; }
}

/* ---- Celular ---- */
@media (max-width: 640px) {
    .block-container { padding: 0 8px 20px !important; }

    /* Brand band compacta */
    .brand-band { padding: 14px 16px; flex-wrap: wrap; gap: 12px; }
    .brand-band .logo-img { width: 42px; height: 42px; }
    .brand-band .company-name { font-size: 22px; }
    .brand-band .brand-sub { display: none; } /* redundante c/ topbar */

    /* Tabs: scroll horizontal, labels longos nao quebram */
    .stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; justify-content: flex-start; padding: 6px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { flex-shrink: 0; padding: 8px 14px; font-size: 12px; white-space: nowrap; }

    /* Titulos de secao */
    .section-title { font-size: 17px; gap: 8px; flex-wrap: wrap; }
    .section-title svg { width: 18px; height: 18px; }
    .section-title .pill { font-size: 10px; padding: 3px 9px; }

    /* KPIs: 2 col, valores/padding menores */
    .kpi-row { grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px; }
    .kpi { padding: 14px; }
    .kpi-value { font-size: 28px; }
    .kpi-label { font-size: 10px; letter-spacing: .6px; }
    .kpi-sub { font-size: 11px; }

    /* Comparativo + YoY: 1 coluna */
    .comp-grid, .comp-grid.with-ano, .yoy-grid { grid-template-columns: 1fr; }
    .comp-card, .yoy-card { padding: 12px; }
    .comp-value { font-size: 22px; }
    .yoy-now { font-size: 26px; }

    /* Planning: empilha badges sob o nome */
    .plan-item { flex-direction: column; align-items: flex-start; gap: 10px; }
    .plan-badges { width: 100%; }
    .plan-name { font-size: 14px; }
    .plan-month { font-size: 16px; flex-wrap: wrap; }
    .plan-month .sub { display: block; width: 100%; margin: 2px 0 0; }
    .plan-total-value { font-size: 24px; }

    .topbar-meta { font-size: 11px; }
}
</style>
"""


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _fmt_media(v):
    if v is None:
        return "—"
    return f"+{v:.1f}" if v > 0 else f"{v:.1f}"


def _fmt_int(v):
    """Inteiro com separador de milhar brasileiro (ponto)."""
    return f"{int(v or 0):,}".replace(",", ".")


def _delta_pct(now, prev):
    if prev in (None, 0) or now is None:
        return None
    return (now - prev) / prev * 100.0


def _month_short(mes):
    return str(mes).split()[0] if mes else "—"


def _year_of(mes):
    parts = str(mes).split()
    return parts[-1] if parts else ""


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------
def _wrap_co(company, inner):
    return f'<div class="co-{company}">{inner}</div>'


def _brand_band(company, meta):
    b64 = _LOGOS.get(company, "")
    img = f'<img class="logo-img" src="data:image/jpeg;base64,{b64}" alt="{LABELS[company]}">' if b64 else ""
    sub = (f'Mês destaque: <b>{meta.get("destaque","")}</b><br>'
           f'Comparativo: <b>{", ".join(meta.get("comparacao",[]))}</b><br>'
           f'Ano anterior: <b>{meta.get("destaque_ano_passado","")}</b>')
    return f'<div class="brand-band">{img}<span class="company-name">{LABELS[company]}</span><span class="brand-sub">{sub}</span></div>'


def _section_title(icon, title, pill=""):
    pill_html = f'<span class="pill">{pill}</span>' if pill else ""
    return f'<div class="section-title">{_SVG[icon]} {title}{pill_html}</div>'


def _kpi(label, value, sub="", hl=False, value_class=""):
    cls = " hl" if hl else ""
    vc = f" {value_class}" if value_class else ""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi{cls}"><div class="kpi-label">{label}</div><div class="kpi-value{vc}">{value}</div>{sub_html}</div>'


def _comp_card(month, rows, year_prev=False):
    cls = " year-prev" if year_prev else ""
    ybadge = f'<span class="ybadge">{_year_of(month)}</span>' if year_prev else ""
    body = ""
    for i, (label, value) in enumerate(rows):
        if i > 0:
            body += '<div class="comp-gap"></div>'
        body += f'<div class="comp-label">{label}</div><div class="comp-value">{value}</div>'
    return f'<div class="comp-card{cls}"><div class="comp-month">{_month_short(month)}{ybadge}</div>{body}</div>'


def _yoy_block(company, destaque, ano):
    rows = ""
    specs = [
        ("SKU's Únicos", "skus", _fmt_int),
        ("Lançamentos Realizados", "lancamentos_realizados", _fmt_int),
        ("Média de Prazo", "media_prazo", _fmt_media),
    ]
    for label, key, fmt in specs:
        nv = destaque.get(key)
        pv = ano.get(key)
        now_str = fmt(nv) if nv is not None else "—"
        prev_str = fmt(pv) if pv is not None else "—"
        delta = _delta_pct(nv, pv)
        if delta is None:
            delta_html = '<div class="yoy-delta">—</div>'
        else:
            arrow = "▲" if delta >= 0 else "▼"
            dcls = "up" if delta >= 0 else "down"
            delta_html = f'<div class="yoy-delta {dcls}">{arrow} {delta:+.1f}%</div>'
        rows += (
            f'<div class="yoy-card"><div class="yl">{label}</div>'
            f'<span class="yoy-now">{now_str}</span>'
            f'<span class="yoy-prev">vs {prev_str} (ano anterior)</span>'
            f'{delta_html}</div>'
        )
    title = (f'{_SVG["troca"]} Comparativo Ano a Ano &bull; '
             f'{destaque.get("mes","")} × {ano.get("mes","")}')
    return f'<div class="yoy"><div class="yoy-title">{title}</div><div class="yoy-grid">{rows}</div></div>'


def _plan_item(it):
    status = it.get("status", "")
    s_ok = status == "OK"
    s_class = "ready" if s_ok else "process"
    s_label = "Pronto" if s_ok else "Em processo"
    mkt = it.get("mkt", "")
    m_ok = mkt == "OK"
    m_label = "MKT enviado" if m_ok else "MKT pendente"
    m_cls = "sent" if m_ok else "pending"
    meta = it.get("data", "")
    if it.get("embarque"):
        meta += f" &bull; Embarque {it['embarque']}"
    return f"""
    <div class="plan-item {s_class}">
      <div style="min-width:0;">
        <div class="plan-name">{it.get("descricao","—")}</div>
        <div class="plan-meta">{meta}</div>
      </div>
      <div class="plan-badges">
        <span class="pst {s_class}">{s_label}</span>
        <span class="mktb {m_cls}">{m_label}</span>
      </div>
    </div>"""


# ---------------------------------------------------------------------------
# Plotly - grafico de volume acumulado (running total) AA vs ano anterior
# ---------------------------------------------------------------------------
_ACCENT_RGB = {"alinare": "121,134,203", "novitah": "215,169,169"}


def _daily_volume_chart(company, destaque, ano):
    cur = destaque.get("volume_diario") or []
    prev = ano.get("volume_diario") or []
    cur_map = {d["dia"]: d["count"] for d in cur}
    prev_map = {d["dia"]: d["count"] for d in prev}
    all_days = set(cur_map) | set(prev_map)
    if not all_days:
        return None
    # Eixo X continuo dia 1 -> maior dia observado (alinhado AA vs ano anterior)
    max_day = max(all_days)
    days = list(range(1, max_day + 1))
    xs = [f"{d:02d}" for d in days]
    daily_cur = [cur_map.get(d, 0) for d in days]
    daily_prev = [prev_map.get(d, 0) for d in days]

    # Running total (soma cumulativa estilo window function SQL)
    cum_cur, cum_prev = [], []
    rc = rp = 0
    for dc, dp in zip(daily_cur, daily_prev):
        rc += dc
        rp += dp
        cum_cur.append(rc)
        cum_prev.append(rp)

    rgb = _ACCENT_RGB.get(company, "121,134,203")
    cur_year = _year_of(destaque.get("mes"))
    prev_year = _year_of(ano.get("mes"))
    # Marcadores apenas nos dias com lancamento real
    mk_cur = [6 if v else 0 for v in daily_cur]
    mk_prev = [5 if v else 0 for v in daily_prev]

    fig = go.Figure()
    # Ano anterior: linha tracejada
    fig.add_trace(go.Scatter(
        x=xs, y=cum_prev,
        name=f"{ano.get('mes', '')} · ano anterior",
        mode="lines+markers",
        line=dict(color=f"rgba({rgb},0.55)", width=2, dash="dash"),
        marker=dict(size=mk_prev, color=f"rgba({rgb},0.65)"),
        customdata=[[v] for v in daily_prev],
        hovertemplate=(f"<b>Dia %{{x}} ({prev_year})</b><br>"
                       f"Acumulado: %{{y}}<br>No dia: %{{customdata[0]}}<extra></extra>"),
    ))
    # Ano atual: linha solida + area preenchida entre as curvas
    fig.add_trace(go.Scatter(
        x=xs, y=cum_cur,
        name=f"{destaque.get('mes', '')} · ano atual",
        mode="lines+markers",
        line=dict(color=f"rgb({rgb})", width=3),
        marker=dict(size=mk_cur, color=f"rgb({rgb})"),
        fill="tonexty", fillcolor=f"rgba({rgb},0.08)",
        customdata=[[v] for v in daily_cur],
        hovertemplate=(f"<b>Dia %{{x}} ({cur_year})</b><br>"
                       f"Acumulado: %{{y}}<br>No dia: %{{customdata[0]}}<extra></extra>"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd9ec", size=11, family="system-ui, sans-serif"),
        margin=dict(l=8, r=8, t=95, b=8), height=420,
        title=dict(
            text=(f"<b>Volume Acumulado de Lançamentos</b><br>"
                  f"<span style='font-size:11px;color:#9fb0c8'>Running total · "
                  f"{destaque.get('mes', '')} × {ano.get('mes', '')}</span>"),
            font=dict(color="#fff", size=14), x=0.5, xanchor="center", y=0.97, yanchor="top"),
        legend=dict(orientation="h", y=1.0, x=0.5, xanchor="center", yanchor="bottom",
                     bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#e8edf5"),
                     itemsizing="constant", borderwidth=0),
        xaxis=dict(title=dict(text="Dia do mês", font=dict(size=11, color="#9fb0c8")),
                   tickangle=-45, showgrid=False, tickfont=dict(size=9, color="#9fb0c8"),
                   linecolor="rgba(255,255,255,0.12)"),
        yaxis=dict(title=dict(text="Lançamentos acumulados", font=dict(size=11, color="#9fb0c8")),
                   gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)",
                   rangemode="tozero", tickfont=dict(size=10, color="#9fb0c8")),
        hovermode="x", showlegend=True,
    )
    return fig


# ---------------------------------------------------------------------------
# Plotly - graficos trimestrais (Tela 1)
# ---------------------------------------------------------------------------
def _trim_keys(trimestres):
    """Apenas trimestres completos (3 meses) — exclui T3/T4 em andamento."""
    return [k for k in ("T1", "T2", "T3", "T4")
            if len(trimestres.get(k, {}).get("meses", [])) == 3]


def _trimester_month_chart(company, trimestres, sel):
    """Chart 1: barras por mes do trimestre selecionado."""
    rgb = _ACCENT_RGB.get(company, "121,134,203")
    if not sel:
        return

    t = trimestres[sel]
    meses = [m["mes"].split()[0] for m in t["meses"]]
    vals = [m["unidades_recebidas"] for m in t["meses"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=meses, y=vals, marker_color=f"rgb({rgb})",
        text=[_fmt_int(v) for v in vals], textposition="outside",
        textfont=dict(color="#e8edf5", size=10),
        hovertemplate="<b>%{x}</b><br>Unidades: %{y}<extra></extra>",
        width=0.5,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd9ec", size=11), margin=dict(l=8, r=8, t=48, b=8), height=360,
        title=dict(text=f"<b>{t['label']}</b>",
                   font=dict(color="#fff", size=13), x=0.5, xanchor="center"),
        xaxis=dict(tickfont=dict(size=10, color="#9fb0c8"), showgrid=False,
                   linecolor="rgba(255,255,255,0.12)"),
        yaxis=dict(title=dict(text="Unidades Recebidas", font=dict(size=10, color="#9fb0c8")),
                   gridcolor="rgba(255,255,255,0.06)", rangemode="tozero",
                   tickfont=dict(size=9, color="#9fb0c8")),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _trimester_compare_chart(company, trimestres):
    """Chart 2: comparativo entre trimestres (total de Unidades Recebidas)."""
    rgb = _ACCENT_RGB.get(company, "121,134,203")
    trim_keys = _trim_keys(trimestres)
    if not trim_keys:
        return

    labels = [trimestres[k]["label"] for k in trim_keys]
    totals = [trimestres[k]["total_unidades"] for k in trim_keys]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=totals, marker_color=f"rgb({rgb})",
        text=[_fmt_int(v) for v in totals], textposition="outside",
        textfont=dict(color="#e8edf5", size=10),
        hovertemplate="<b>%{x}</b><br>Total: %{y} unidades<extra></extra>",
        width=0.45,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd9ec", size=11), margin=dict(l=8, r=8, t=48, b=8), height=360,
        title=dict(text="<b>Comparativo Trimestral</b>",
                   font=dict(color="#fff", size=13), x=0.5, xanchor="center"),
        xaxis=dict(tickfont=dict(size=10, color="#9fb0c8"), showgrid=False,
                   linecolor="rgba(255,255,255,0.12)"),
        yaxis=dict(title=dict(text="Unidades Recebidas", font=dict(size=10, color="#9fb0c8")),
                   gridcolor="rgba(255,255,255,0.06)", rangemode="tozero",
                   tickfont=dict(size=9, color="#9fb0c8")),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
def render_screen1(company, data):
    t1 = data[company]["tela1"]
    d = t1.get("destaque", {})
    trimestres = t1.get("trimestres", {})
    forn = d.get("sku_por_fornecedor", []) or []
    top_forn = forn[0] if forn else {}

    kpis = (
        _kpi("Notas Emitidas", d.get("notas_emitidas", 0), hl=True)
        + _kpi("Total de SKUs únicos", _fmt_int(d.get("sku_total", 0)),
               sub=f'{d.get("sku_por_nota", 0):.0f} SKU/nota em média')
        + _kpi("Top Fornecedor", top_forn.get("skus", 0) if top_forn else "—",
               sub=top_forn.get("fornecedor", "—") if top_forn else "—")
        + _kpi("Unidades Recebidas", _fmt_int(d.get("unidades_recebidas", 0)))
    )
    html = _wrap_co(company,
        _section_title("notas", "Notas de Entrada", d.get("mes", ""))
        + f'<div class="kpi-row">{kpis}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

    # Filtro de trimestre (acima dos charts para alinhar X-axis)
    trim_keys = _trim_keys(trimestres)
    sel = None
    if trim_keys:
        col_f, _ = st.columns([1, 1])
        with col_f:
            sel = st.selectbox("Trimestre", trim_keys,
                               format_func=lambda k: trimestres[k]["label"],
                               key=f"trim1_{company}")

    # Graficos trimestrais lado a lado (X-axis alinhado)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        _trimester_month_chart(company, trimestres, sel)
    with col_c2:
        _trimester_compare_chart(company, trimestres)


def _comp_block(cards_html, with_ano=False):
    cls = "comp-grid with-ano" if with_ano else "comp-grid"
    return (f'<div class="comp-title">{_SVG["grafico"]} Comparativo — Meses Anteriores</div>'
            f'<div class="{cls}">{cards_html}</div>')


def render_screen2(company, data):
    t2 = data[company]["tela2"]
    d = t2.get("destaque", {})
    comps = t2.get("comparacao", [])
    ano = t2.get("ano_anterior", {})

    md = d.get("media_prazo")
    md_str = _fmt_media(md)
    md_cls = "green" if (md is not None and md >= 0) else "red"
    dia = d.get("dia_pico") or {}

    kpis = (
        _kpi("Média de Prazo", md_str, sub="Data → Lançamento", hl=True, value_class=md_cls)
        + _kpi("SKU's Únicos", d.get("skus", 0))
        + _kpi("Dia de Pico", dia.get("data", "—"), sub=dia.get("dia_semana", ""))
        + _kpi("Lançamentos Realizados", d.get("lancamentos_realizados", 0))
    )

    has_ano = ano and ano.get("lancamentos", 0) > 0
    comp_cards = "".join(
        _comp_card(c.get("mes"), [
            ("Lançamentos Realizados", c.get("lancamentos_realizados", 0)),
            ("Média Dias", _fmt_media(c.get("media_prazo"))),
        ]) for c in comps
    )
    if has_ano:
        comp_cards += _comp_card(ano.get("mes"), [
            ("Lançamentos Realizados", ano.get("lancamentos_realizados", 0)),
            ("SKUs", ano.get("skus", 0)),
            ("Média Dias", _fmt_media(ano.get("media_prazo"))),
        ], year_prev=True)

    html = _wrap_co(company,
        _section_title("produtos", "Produtos Lançados", d.get("mes", ""))
        + f'<div class="kpi-row">{kpis}</div>'
        + (_yoy_block(company, d, ano) if has_ano else "")
        + (_comp_block(comp_cards, with_ano=has_ano) if (comps or has_ano) else "")
    )
    st.markdown(html, unsafe_allow_html=True)

    # Grafico de volume acumulado (running total AA vs ano anterior)
    fig = _daily_volume_chart(company, d, ano)
    if fig is not None:
        st.markdown(_wrap_co(company, '<div class="comp-title" style="margin-top:8px;">'
                                      f'{_SVG["grafico"]} Volume Acumulado — {d.get("mes","")} × {ano.get("mes","")}'
                                      '</div>'), unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)


def render_screen3(company, data):
    t3 = data[company]["tela3"]
    items = t3.get("itens", [])
    ok = t3.get("status_ok", 0)
    proc = t3.get("status_processo", 0)
    list_html = "".join(_plan_item(it) for it in items) or '<div class="plan-meta">Nenhum lançamento programado.</div>'
    total_html = f"""
    <div class="plan-total">
      <div style="font-size:13px; opacity:0.7;">Total do Mês</div>
      <div class="plan-total-value">{t3.get("total_itens", 0)} itens</div>
      <div class="plan-total-bd">
        <span><span class="dot ready">&#9679;</span>{ok} Prontos</span>
        <span><span class="dot process">&#9679;</span>{proc} Em processo</span>
      </div>
    </div>"""
    kpis = (
        _kpi("Itens Programados", t3.get("total_itens", 0), hl=True)
        + _kpi("Status OK", ok, value_class="green")
        + _kpi("Em Processo", proc, value_class="red" if proc else "")
        + _kpi("MKT Enviado", t3.get("mkt_ok", 0), sub=f'Pendente: {t3.get("mkt_processo", 0)}')
    )
    html = _wrap_co(company,
        _section_title("calendario", "Próximos Lançamentos", t3.get("mes", ""))
        + f'<div class="kpi-row">{kpis}</div>'
        + f'<div class="plan-month">{_SVG["calendario"]} {t3.get("mes","")}<span class="sub">{t3.get("total_itens",0)} itens &bull; {ok} prontos &bull; {proc} em processo</span></div>'
        + f'<div class="plan-list">{list_html}</div>'
        + total_html
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Company page (band + 3 sub-abas)
# ---------------------------------------------------------------------------
def render_company(company, data):
    meta = data.get("meta", {})
    st.markdown(_wrap_co(company, _brand_band(company, meta)), unsafe_allow_html=True)
    t_notas, t_prod, t_prox = st.tabs(["Notas de Entrada", "Produtos Lançados", "Próximos Lançamentos"])
    with t_notas:
        render_screen1(company, data)
    with t_prod:
        render_screen2(company, data)
    with t_prox:
        render_screen3(company, data)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.markdown(_CSS, unsafe_allow_html=True)
    data = load_data()
    meta = data.get("meta", {})

    # Top bar: meta + botao atualizar
    meta_html = (f'<div class="topbar-meta">'
                 f'Destaque: <b>{meta.get("destaque","")}</b> &nbsp;|&nbsp; '
                 f'Comparativo: <b>{", ".join(meta.get("comparacao",[]))}</b>')
    if meta.get("destaque_ano_passado"):
        meta_html += f' &nbsp;|&nbsp; Ano anterior: <b>{meta.get("destaque_ano_passado","")}</b>'
    meta_html += f' &nbsp;|&nbsp; Planejamento: <b>{meta.get("proximo_mes","")}</b></div>'

    c_meta, c_btn = st.columns([7, 1])
    with c_meta:
        st.markdown(f'<div class="topbar">{meta_html}</div>', unsafe_allow_html=True)
    with c_btn:
        st.write("")
        if st.button("↻ Atualizar", help="Reprocessa as planilhas e atualiza os dados",
                     use_container_width=True):
            with st.spinner("Reprocessando planilhas..."):
                subprocess.run([sys.executable, "-m", "src.pipeline"],
                               cwd=str(BASE_DIR), capture_output=True, text=True)
            st.cache_data.clear()
            st.rerun()

    # Abas de empresa
    tab_a, tab_n = st.tabs(["ALINARE", "NOVITAH"])
    with tab_a:
        render_company("alinare", data)
    with tab_n:
        render_company("novitah", data)

    st.markdown(f'<div class="data-note">Dados processados em: {meta.get("hoje","")} &bull; '
                f'Fonte: output/data.json</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
