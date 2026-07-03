"""Tela 3 - Programacao dos proximos lancamentos.

Usa a aba Lancamentos do arquivo da Alinare (contem ambas as empresas, coluna BU).
Sem comparacao com meses anteriores - apenas o proximo mes.

Metricas:
  - Previa dos lancamentos do proximo mes com status (Pronto / Em Processo)
  - Status MKT (verde = enviado)
  - SKU programados para subir no mes (join Lancamentos.Data <-> Geral.LANCAMENTO)
"""
from __future__ import annotations

import logging

import pandas as pd

from . import config
from .clean import classify_status, mkt_status

log = logging.getLogger("dashboard.screen3")


def compute_all(lanc: pd.DataFrame, geral: pd.DataFrame) -> dict[str, dict]:
    """Calcula metricas da Tela 3 para ambas as empresas a partir dos dados da Alinare."""
    results = {}
    for company in config.COMPANIES:
        results[company] = _compute_company(company, lanc, geral)
    return results


def _compute_company(company: str, lanc: pd.DataFrame, geral: pd.DataFrame) -> dict:
    result = {
        "company": company,
        "month": f"{config.month_label(config.PROXIMO_MES)} {config.PROXIMO_MES.year}",
        "items": [],
        "total_skus": 0,
        "ready": 0,
        "process": 0,
        "mkt_sent": 0,
        "mkt_pending": 0,
    }

    if lanc.empty:
        log.warning("[%s] Lancamentos vazio", company)
        return result

    # Filtrar Lancamentos para a empresa e proximo mes
    emp_lanc = lanc[lanc["empresa"] == company].copy()
    prox_ym = config.ym_key(config.PROXIMO_MES)
    emp_lanc = emp_lanc.dropna(subset=["data"])
    july_mask = emp_lanc["data"].apply(
        lambda d: isinstance(d, pd.Timestamp) and (d.year, d.month) == prox_ym
    )
    emp_july = emp_lanc[july_mask]

    # SKU count via join Lancamentos.data <-> Geral.LANCAMENTO
    sku_count = 0
    if not geral.empty and "LANÇAMENTO" in geral.columns and not emp_july.empty:
        marca_map = {"alinare": {"AL"}, "novitah": {"NV", "NO", "NT"}}
        # Detectar codigos reais
        from .io import detect_marca_codes
        mc = detect_marca_codes(geral)
        emp_codes = mc.get(company, marca_map.get(company, set()))
        g = geral[geral["MARCA"].astype(str).str.upper().isin(emp_codes)] if emp_codes else geral
        g = g.dropna(subset=["LANÇAMENTO"])
        july_dates = set(emp_july["data"].dt.normalize().unique())
        matched = g[g["LANÇAMENTO"].dt.normalize().isin(july_dates)]
        sku_count = int(matched["COD PROD"].nunique()) if "COD PROD" in matched.columns else 0
        log.info("[%s] SKU programados Julho: %d (datas Lancamentos: %d, Geral matched: %d linhas)",
                 company, sku_count, len(july_dates), len(matched))

    result["total_skus"] = sku_count

    # Processar itens da previa
    ready = process = mkt_sent = mkt_pending = 0
    items = []
    for _, row in emp_july.iterrows():
        status_text = classify_status(row.get("status"), row.get("transferencia"))
        mkt = mkt_status(row.get("mkt_verde", False), row.get("mkt_valor"))

        if status_text == "ready":
            ready += 1
        else:
            process += 1
        if mkt == "sent":
            mkt_sent += 1
        else:
            mkt_pending += 1

        embarque_pedra = str(row.get("embarque_pedra") or "")[:60]
        items.append({
            "data": row["data"].strftime("%d/%m") if isinstance(row["data"], pd.Timestamp) else "—",
            "descricao": embarque_pedra,
            "embarque": str(row.get("embarque") or ""),
            "status": status_text,
            "status_raw": str(row.get("status") or ""),
            "mkt": mkt,
        })

    # Ordenar por data
    items.sort(key=lambda x: x["data"])
    result["items"] = items
    result["ready"] = ready
    result["process"] = process
    result["mkt_sent"] = mkt_sent
    result["mkt_pending"] = mkt_pending

    return result
