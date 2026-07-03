"""Componentes de UI reutilizaveis para o dashboard Streamlit (HTML/CSS com marca)."""
from __future__ import annotations

import streamlit as st

from . import config

_BRAND = config.BRAND


def inject_css():
    st.markdown("""
    <style>
    /* Reset & base */
    .stApp { background: #0a0e1a; }
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 0; max-width: 100%; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px; background: #121826; border-radius: 0;
        border-bottom: 1px solid #2a374a; justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 28px; font-size: 14px; font-weight: 500;
        color: #8b9cb5; background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important; border-bottom: 3px solid #ffffff;
    }

    /* Split container */
    .split-row { display: flex; gap: 2px; margin-top: 0; }
    .split-side {
        flex: 1; padding: 28px 32px; min-height: 80vh; border-radius: 0;
    }
    .split-side.alinare { background: #1a237e; }
    .split-side.novitah { background: #a07a7a; }

    /* Logo area */
    .logo-area { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
    .logo-box {
        width: 42px; height: 42px; border-radius: 6px; display: flex;
        align-items: center; justify-content: center; font-weight: 700; font-size: 20px;
        color: #fff;
    }
    .logo-box.alinare { background: #283593; }
    .logo-box.novitah { background: #8d6b6b; }
    .company-name { font-size: 22px; font-weight: 700; letter-spacing: 0.5px; color: #fff; }

    /* Section titles */
    .screen-title {
        font-size: 20px; font-weight: 600; color: #fff; margin-bottom: 16px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.12);
    }
    .month-header {
        font-size: 15px; font-weight: 500; color: rgba(255,255,255,0.9);
        margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
    }
    .pin { width: 14px; height: 14px; display: inline-block; opacity: 0.7; }

    /* Metric cards */
    .kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
    .kpi-card {
        background: rgba(255,255,255,0.06); border-radius: 8px; padding: 18px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .kpi-card.highlight {
        background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.18);
    }
    .kpi-label {
        font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;
        opacity: 0.7; margin-bottom: 6px; color: #fff;
    }
    .kpi-value {
        font-size: 34px; font-weight: 700; line-height: 1; color: #fff;
        font-variant-numeric: tabular-nums;
    }
    .kpi-value.green { color: #81c784; }
    .kpi-value.red { color: #ef9a9a; }
    .kpi-sub { font-size: 11px; opacity: 0.6; margin-top: 4px; color: #fff; }

    /* Comparison cards */
    .comp-title {
        font-size: 14px; font-weight: 500; margin: 8px 0 12px 0;
        color: rgba(255,255,255,0.9);
    }
    .comp-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .comp-card {
        background: rgba(255,255,255,0.04); border-radius: 6px; padding: 14px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .comp-month { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #fff; }
    .comp-label { font-size: 10px; opacity: 0.6; color: #fff; }
    .comp-value {
        font-size: 22px; font-weight: 700; color: #fff;
        font-variant-numeric: tabular-nums;
    }

    /* Planning items */
    .plan-list { display: flex; flex-direction: column; gap: 8px; }
    .plan-item {
        background: rgba(255,255,255,0.04); border-radius: 6px; padding: 14px;
        border: 1px solid rgba(255,255,255,0.08); display: flex;
        justify-content: space-between; align-items: center;
    }
    .plan-item.ready { background: rgba(76,175,80,0.12); border-color: rgba(76,175,80,0.25); }
    .plan-item.process { background: rgba(255,193,7,0.10); border-color: rgba(255,193,7,0.2); }
    .plan-name { font-size: 14px; font-weight: 500; color: #fff; }
    .plan-meta { font-size: 12px; opacity: 0.6; margin-top: 2px; color: #fff; }
    .plan-badges { display: flex; gap: 6px; align-items: center; }
    .badge {
        padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;
    }
    .badge.ready { background: rgba(76,175,80,0.2); color: #81c784; }
    .badge.process { background: rgba(255,193,7,0.2); color: #ffd54f; }
    .badge.mkt-sent { background: rgba(76,175,80,0.15); color: #81c784; }
    .badge.mkt-pending { background: rgba(255,193,7,0.15); color: #ffd54f; }

    /* Total box */
    .total-box {
        margin-top: 16px; padding: 16px; background: rgba(255,255,255,0.04);
        border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);
    }

    .data-note {
        font-size: 11px; opacity: 0.4; text-align: center; padding: 8px; color: #ccc;
    }
    </style>
    """, unsafe_allow_html=True)


def _logo(company: str) -> str:
    initial = company[0].upper()
    return f"""
    <div class="logo-area">
        <div class="logo-box {company}">{initial}</div>
        <span class="company-name">{config.COMPANY_LABELS[company]}</span>
    </div>"""


def _kpi(label: str, value, sub: str = "", highlight: bool = False,
         value_class: str = "") -> str:
    hl = " highlight" if highlight else ""
    vc = f" {value_class}" if value_class else ""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card{hl}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value{vc}">{value}</div>
        {sub_html}
    </div>"""


def _comparison_card(month: str, items: list[tuple[str, str]]) -> str:
    rows = ""
    for label, value in items:
        rows += f'<div class="comp-label">{label}</div><div class="comp-value">{value}</div>'
    return f"""<div class="comp-card"><div class="comp-month">{month}</div>{rows}</div>"""


def _planning_item(desc: str, meta: str, status: str, mkt: str) -> str:
    s_class = "ready" if status == "ready" else "process"
    s_label = "Pronto" if status == "ready" else "Em Processo"
    mkt_class = "mkt-sent" if mkt == "sent" else "mkt-pending"
    mkt_label = "MKT ✓" if mkt == "sent" else "MKT"
    return f"""
    <div class="plan-item {s_class}">
        <div>
            <div class="plan-name">{desc}</div>
            <div class="plan-meta">{meta}</div>
        </div>
        <div class="plan-badges">
            <span class="badge {s_class}">{s_label}</span>
            <span class="badge {mkt_class}">{mkt_label}</span>
        </div>
    </div>"""


def render_side(company: str, content_html: str):
    """Renderiza um lado (Alinare/Novitah) com fundo de marca."""
    st.markdown(
        f'<div class="split-side {company}">{_logo(company)}{content_html}</div>',
        unsafe_allow_html=True,
    )


def render_split(alinare_html: str, novitah_html: str):
    """Renderiza os dois lados lado a lado."""
    st.markdown(
        f'<div class="split-row">'
        f'<div class="split-side alinare">{_logo("alinare")}{alinare_html}</div>'
        f'<div class="split-side novitah">{_logo("novitah")}{novitah_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
