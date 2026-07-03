"""Dashboard Alinare & Novitah — Streamlit + Plotly.

Run:  streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import plotly.graph_objects as go
import streamlit as st

from src import config
from src import ui_components as ui
from src.clean import fmt_signed_days

st.set_page_config(page_title="Dashboard — Alinare & Novitah", layout="wide", page_icon="💎")


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner="Processando planilhas...")
def load_data():
    from src.pipeline import run
    return run()


# ---------------------------------------------------------------------------
# Plotly helpers
# ---------------------------------------------------------------------------
_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white", size=12, family="system-ui, sans-serif"),
    margin=dict(l=10, r=10, t=30, b=10),
)


def _bar_chart(labels, values, color, title="", highlight_last=False):
    colors = [color] * len(labels)
    if highlight_last and labels:
        colors[-1] = "#ffffff"
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=colors,
                                 text=values, textposition="outside",
                                 textfont=dict(size=13, color="white"))])
    fig.update_layout(**_PLOTLY_LAYOUT, title=title,
                      yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                      showlegend=False)
    return fig


def _hbar_chart(labels, values, color, title=""):
    fig = go.Figure(data=[go.Bar(y=labels, x=values, orientation="h",
                                 marker_color=color,
                                 text=values, textposition="outside",
                                 textfont=dict(size=11, color="white"))])
    fig.update_layout(**_PLOTLY_LAYOUT, title=title,
                      xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                      showlegend=False, height=320,
                      margin=dict(l=10, r=40, t=30, b=10))
    return fig


def _donut(labels, values, colors, title=""):
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.6,
        marker=dict(colors=colors),
        textinfo="label+value", textfont=dict(color="white", size=12),
    )])
    fig.update_layout(**_PLOTLY_LAYOUT, title=title, showlegend=False)
    return fig


# ---------------------------------------------------------------------------
# Screen renderers
# ---------------------------------------------------------------------------
def _screen1_side(company, data):
    s1 = data[company]["notas_entrada"]
    d = s1.get("destaque", {})
    comps = s1.get("comparison", [])

    html = f'<div class="screen-title">Notas de Entrada</div>'
    html += '<div class="month-header">📍 ' + config.month_label(config.DESTAQUE) + f' {config.DESTAQUE.year} — Mês Destaque</div>'
    html += '<div class="kpi-grid">'
    html += ui._kpi("Notas que Subiram", d.get("notas_subiram", 0), highlight=True)
    html += ui._kpi("SKU por Nota (média)", d.get("sku_por_nota", 0), sub=f'Total: {d.get("sku_total", 0)} SKUs')
    html += ui._kpi("Fornecedores Ativos", d.get("fornecedores_ativos", 0))
    top_forn = s1.get("sku_por_fornecedor_destaque", [])
    top_val = top_forn[0]["skus"] if top_forn else 0
    top_name = top_forn[0]["fornecedor"] if top_forn else "—"
    html += ui._kpi("Top Fornecedor", top_val, sub=top_name)
    html += '</div>'

    # Comparison
    if comps:
        html += '<div class="comp-title">Comparativo — Meses Anteriores</div>'
        html += '<div class="comp-grid">'
        for c in comps:
            html += ui._comparison_card(c["month"], [
                ("Notas", c.get("notas_subiram", 0)),
                ("SKU/nota", c.get("sku_por_nota", 0)),
            ])
        html += '</div>'

    return html


def _screen2_side(company, data):
    s2 = data[company]["produtos_lancados"]
    d = s2.get("destaque", {})
    comps = s2.get("comparison", [])

    md = d.get("media_dias")
    md_str = f"{md:+.1f}" if md is not None else "—"
    md_class = "green" if (md is not None and md < 0) else ("red" if (md is not None and md > 0) else "")
    md_sub = "Adiantado (negativo)" if (md is not None and md < 0) else "Data − Lançamento"

    html = f'<div class="screen-title">Produtos Lançados</div>'
    html += '<div class="month-header">📍 ' + config.month_label(config.DESTAQUE) + f' {config.DESTAQUE.year} — Mês Destaque</div>'
    html += '<div class="kpi-grid">'
    html += ui._kpi("Média de Dias", md_str, sub=md_sub, highlight=True, value_class=md_class)
    html += ui._kpi("Lançamentos", d.get("lancamentos", 0))
    dia = d.get("dia_com_mais")
    html += ui._kpi("Dia com Mais", dia["day"] if dia else "—",
                    sub=dia["weekday"] if dia else "")
    html += ui._kpi("SKUs Lançados", d.get("skus", 0))
    html += '</div>'

    if comps:
        html += '<div class="comp-title">Comparativo — Meses Anteriores</div>'
        html += '<div class="comp-grid">'
        for c in comps:
            cmd = c.get("media_dias")
            cmd_str = f"{cmd:+.1f}" if cmd is not None else "—"
            html += ui._comparison_card(c["month"], [
                ("Lançamentos", c.get("lancamentos", 0)),
                ("Média Dias", cmd_str),
            ])
        html += '</div>'

    return html


def _screen3_side(company, data):
    s3 = data[company]["proximos_lancamentos"]
    html = f'<div class="screen-title">Próximos Lançamentos</div>'
    html += f'<div class="month-header">📅 {s3.get("month", "")}</div>'

    # KPIs
    html += '<div class="kpi-grid">'
    html += ui._kpi("SKUs Programados", s3.get("total_skus", 0), highlight=True)
    html += ui._kpi("Prontos", s3.get("ready", 0), value_class="green")
    html += ui._kpi("Em Processo", s3.get("process", 0), value_class="red" if s3.get("process", 0) else "")
    html += ui._kpi("MKT Enviado", s3.get("mkt_sent", 0),
                    sub=f'Pendente: {s3.get("mkt_pending", 0)}')
    html += '</div>'

    # Planning list
    items = s3.get("items", [])
    if items:
        html += '<div class="plan-list">'
        for it in items:
            meta = f'{it["data"]} — {it["embarque"]}' if it.get("embarque") else it["data"]
            html += ui._planning_item(it["descricao"], meta, it["status"], it["mkt"])
        html += '</div>'
    else:
        html += '<div class="plan-meta">Nenhum lançamento programado para este mês.</div>'

    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ui.inject_css()

    st.markdown('<div style="text-align:center; padding: 4px 0;">'
                '<span style="font-size:11px; color:#8b9cb5;">'
                f'Destaque: {config.month_label(config.DESTAQUE)} {config.DESTAQUE.year} · '
                f'Comparação: {", ".join(config.month_label(m) for m in config.COMPARACAO_MESES)} · '
                f'Planejamento: {config.month_label(config.PROXIMO_MES)} {config.PROXIMO_MES.year}'
                '</span></div>', unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 6, 1])
    with col_btn1:
        if st.button("🔄 Atualizar", help="Recarrega dados das planilhas"):
            st.cache_data.clear()
            st.rerun()

    data = load_data()

    tab1, tab2, tab3 = st.tabs(["📋 Notas de Entrada", "📦 Produtos Lançados", "🚀 Próximos Lançamentos"])

    with tab1:
        ui.render_split(_screen1_side("alinare", data), _screen1_side("novitah", data))
        # Charts
        _screen1_charts(data)

    with tab2:
        ui.render_split(_screen2_side("alinare", data), _screen2_side("novitah", data))
        _screen2_charts(data)

    with tab3:
        ui.render_split(_screen3_side("alinare", data), _screen3_side("novitah", data))

    st.markdown('<div class="data-note">Dados processados das planilhas em /data · '
                'Para recarregar, aguarde o cache expirar</div>',
                unsafe_allow_html=True)


def _screen1_charts(data):
    st.markdown("---")
    col_a, col_n = st.columns(2)
    for col, company in [(col_a, "alinare"), (col_n, "novitah")]:
        s1 = data[company]["notas_entrada"]
        d = s1.get("destaque", {})
        comps = s1.get("comparison", [])
        # Ordem cronologica (mais antigo -> mais recente)
        months = [c["month"] for c in comps] + [d["month"]]
        notas = [c.get("notas_subiram", 0) for c in comps] + [d.get("notas_subiram", 0)]
        color = config.BRAND[company]["chart"]

        with col:
            st.plotly_chart(_bar_chart(months, notas, color,
                                       f"{config.COMPANY_LABELS[company]} — Notas que Subiram"),
                            use_container_width=True)

            forn = s1.get("sku_por_fornecedor_destaque", [])[:8]
            if forn:
                labels = [f["fornecedor"] for f in forn][::-1]
                values = [f["skus"] for f in forn][::-1]
                st.plotly_chart(_hbar_chart(labels, values, color,
                                            f"SKU por Fornecedor — {config.month_label(config.DESTAQUE)}"),
                                use_container_width=True)


def _screen2_charts(data):
    st.markdown("---")
    col_a, col_n = st.columns(2)
    for col, company in [(col_a, "alinare"), (col_n, "novitah")]:
        s2 = data[company]["produtos_lancados"]
        d = s2.get("destaque", {})
        comps = s2.get("comparison", [])
        months = [c["month"] for c in comps] + [d["month"]]
        lanc = [c.get("lancamentos", 0) for c in comps] + [d.get("lancamentos", 0)]
        medias = [c.get("media_dias") or 0 for c in comps] + [d.get("media_dias") or 0]
        color = config.BRAND[company]["chart"]

        with col:
            st.plotly_chart(_bar_chart(months, lanc, color,
                                       f"{config.COMPANY_LABELS[company]} — Lançamentos"),
                            use_container_width=True)
            # Media dias com cor por sinal
            bar_colors = ["#81c784" if v < 0 else "#ef9a9a" if v > 0 else "#90a4ae" for v in medias]
            fig = go.Figure(data=[go.Bar(x=months, y=medias, marker_color=bar_colors,
                                         text=[f"{v:+.1f}" for v in medias],
                                         textposition="outside",
                                         textfont=dict(color="white", size=12))])
            fig.update_layout(**_PLOTLY_LAYOUT,
                              title=f"{config.COMPANY_LABELS[company]} — Média de Dias (verde=adiantado)",
                              yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
