"""Tela 2 - Produtos Lancados.

Metricas por mes:
  - Media de dias (Data - Data Lancamento), com sinal (negativo = adiantado)
  - Quantidade de lancamentos (distinct Lancamento)
  - SKUs lancados (distinct Produto)
  - Dia com mais lancamentos (apenas mes destaque)
"""
from __future__ import annotations

import logging

import pandas as pd

from . import config

log = logging.getLogger("dashboard.screen2")


def compute(company: str, p1: pd.DataFrame) -> dict:
    months = config.ALL_MONTHS
    result = {
        "company": company,
        "destaque": None,
        "comparison": [],
    }

    if p1.empty:
        log.warning("[%s] Planilha 1 vazia", company)
        return result

    if "Data" not in p1.columns or "Data Lançamento" not in p1.columns:
        log.warning("[%s] P1 sem colunas Data/Data Lancamento", company)
        return result

    df = p1.copy()
    df = df.dropna(subset=["Data"])

    for i, month_date in enumerate(months):
        ym = config.ym_key(month_date)
        mask = df["Data"].apply(lambda d: d is not pd.NaT and (d.year, d.month) == ym)
        mdf = df[mask]
        if mdf.empty:
            entry = _empty_entry(month_date, i == 0)
        else:
            # Media de dias: Data (estimativa) - Data Lancamento (realidade)
            both = mdf.dropna(subset=["Data", "Data Lançamento"]).copy()
            if not both.empty:
                both["_dias"] = (both["Data"] - both["Data Lançamento"]).dt.days
                media_dias = round(float(both["_dias"].mean()), 1)
            else:
                media_dias = None

            # Lancamentos e SKUs
            lanc_col = "Lançamento" if "Lançamento" in mdf.columns else None
            lancamentos = int(mdf[lanc_col].nunique()) if lanc_col else int(len(mdf))
            skus = int(mdf["Produto"].nunique()) if "Produto" in mdf.columns else int(len(mdf))

            # Dia com mais lancamentos (so destaque)
            dia_mais = None
            if i == 0:
                by_day = mdf.groupby(mdf["Data"].dt.date).size()
                if not by_day.empty:
                    peak_day = by_day.idxmax()
                    peak_count = int(by_day.max())
                    dia_mais = {
                        "date": peak_day.isoformat(),
                        "day": peak_day.day,
                        "weekday": config.weekday_pt(peak_day),
                        "count": peak_count,
                    }

            entry = {
                "month": config.month_label(month_date),
                "month_date": month_date.isoformat(),
                "is_destaque": i == 0,
                "media_dias": media_dias,
                "lancamentos": lancamentos,
                "skus": skus,
                "dia_com_mais": dia_mais,
            }

        if i == 0:
            result["destaque"] = entry
        else:
            result["comparison"].append(entry)

    return result


def _empty_entry(month_date, is_destaque):
    return {
        "month": config.month_label(month_date),
        "month_date": month_date.isoformat(),
        "is_destaque": is_destaque,
        "media_dias": None,
        "lancamentos": 0,
        "skus": 0,
        "dia_com_mais": None,
    }
