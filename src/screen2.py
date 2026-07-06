"""Tela 2 - Produtos Lancados.

- Lancamentos: contar linhas P1 com Data no mes
- SKUs: contar Produto unico
- Media de prazo: (Data Lancamento - Data) para o ano atual, remover negativos
- Dia com mais lancamentos: agrupar por dia, achar maximo
- Comparacao inclui o mes destaque do ano anterior
"""
from __future__ import annotations

import logging

import pandas as pd

from . import config
from . import io as iomod

log = logging.getLogger("dashboard.screen2")


def compute(company: str, p1: pd.DataFrame) -> dict:
    result = {"company": company, "destaque": None, "comparacao": [], "ano_anterior": None}

    if p1.empty:
        log.warning("[%s] P1 vazia", company)
        return result

    cm = iomod.col_map(p1)
    data_col = cm.get("Data")
    dlanc_col = cm.get("Data Lancamento")
    prod_col = cm.get("Produto")

    if not data_col or not dlanc_col:
        log.warning("[%s] P1 sem colunas Data/Data Lancamento", company)
        return result

    # Filtrar apenas ano atual
    yr_filter = p1[p1[data_col].dt.year == config.TODAY.year].copy()

    weekdays = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]

    for i, md in enumerate(config.ALL_MONTHS):
        entry = _calc_month(yr_filter, data_col, dlanc_col, prod_col, md, i == 0, weekdays,
                            with_volume=(i == 0))
        if i == 0:
            result["destaque"] = entry
        else:
            result["comparacao"].append(entry)

    # Ano anterior (mes destaque do ano passado)
    yr_prev = p1[p1[data_col].dt.year == config.DESTAQUE_ANO_PASSADO.year].copy()
    result["ano_anterior"] = _calc_month(
        yr_prev, data_col, dlanc_col, prod_col, config.DESTAQUE_ANO_PASSADO,
        False, weekdays, with_volume=True
    )

    return result


def _calc_month(df, data_col, dlanc_col, prod_col, md, is_destaque, weekdays, with_volume=False) -> dict:
    mask = (df[data_col].dt.year == md.year) & (df[data_col].dt.month == md.month)
    mdf = df[mask]

    if mdf.empty:
        return _empty_entry(md, is_destaque)

    total_linhas = len(mdf)
    skus = int(mdf[prod_col].nunique()) if prod_col else 0
    # Lançamentos Realizados: dias com >=300 linhas (coluna H = Data Lancamento)
    if dlanc_col in mdf.columns and not mdf[dlanc_col].dropna().empty:
        by_date = mdf.groupby(mdf[dlanc_col].dt.date).size()
        lancamentos_realizados = int((by_date >= 300).sum())
    else:
        lancamentos_realizados = 0

    # Media de prazo: H - G, remover negativos
    both = mdf.dropna(subset=[data_col, dlanc_col]).copy()
    both = both[both[dlanc_col].dt.year == md.year]
    if not both.empty:
        both["_dias"] = (both[dlanc_col] - both[data_col]).dt.days
        clean = both[both["_dias"] >= 0]
        media = round(float(clean["_dias"].mean()), 1) if not clean.empty else None
        mediana = round(float(clean["_dias"].median()), 1) if not clean.empty else None
        removidos = len(both) - len(clean)
    else:
        media = None
        mediana = None
        removidos = 0

    # Dia de pico (apenas destaque)
    dia_pico = None
    if is_destaque:
        by_day = mdf.groupby(mdf[data_col].dt.date).size().sort_values(ascending=False)
        if not by_day.empty:
            pk = by_day.index[0]
            dia_pico = {
                "data": pk.strftime("%d/%m"),
                "dia_semana": config.weekday_pt(pk),
                "quantidade": int(by_day.iloc[0]),
            }

    # Volume diario (destaque e ano anterior): lancamentos por dia do mes
    volume_diario = None
    if with_volume:
        by_daynum = mdf.groupby(mdf[data_col].dt.day).size()
        volume_diario = [
            {"dia": int(d), "data": f"{int(d):02d}/{md.month:02d}", "count": int(c)}
            for d, c in by_daynum.items()
        ]
        volume_diario.sort(key=lambda x: x["dia"])

    return {
        "mes": f"{config.month_label(md)} {md.year}",
        "is_destaque": is_destaque,
        "lancamentos": total_linhas,
        "lancamentos_realizados": lancamentos_realizados,
        "skus": skus,
        "media_prazo": media,
        "mediana_prazo": mediana,
        "removidos_negativos": removidos,
        "dia_pico": dia_pico,
        "volume_diario": volume_diario,
    }


def _empty_entry(md, is_destaque) -> dict:
    return {
        "mes": f"{config.month_label(md)} {md.year}",
        "is_destaque": is_destaque,
        "lancamentos": 0,
        "lancamentos_realizados": 0,
        "skus": 0,
        "media_prazo": None,
        "mediana_prazo": None,
        "removidos_negativos": 0,
        "dia_pico": None,
        "volume_diario": None,
    }
