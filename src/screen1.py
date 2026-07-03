"""Tela 1 - Notas de Entrada.

- Notas Emitidas: contar linhas P3 com Data Entrada no mes
- SKU/nota: join P3._nf <-> Geral._nf, contar COD PROD unico
- SKU/Fornecedor: usar Razao Social (coluna G) do P3, somar SKUs das notas
- Unidades Recebidas: join P3._nf <-> Geral._nf, somar coluna QUANTIDADE
- Trimestres: agrupar meses por trimestre (T1-T4) para graficos comparativos
"""
from __future__ import annotations

import logging
from datetime import date

import pandas as pd

from . import config
from . import io as iomod

log = logging.getLogger("dashboard.screen1")

_TRIM_MAP = {1: "T1", 2: "T1", 3: "T1", 4: "T2", 5: "T2", 6: "T2",
             7: "T3", 8: "T3", 9: "T3", 10: "T4", 11: "T4", 12: "T4"}
_TRIM_LABELS = {"T1": "1º Trimestre", "T2": "2º Trimestre",
                "T3": "3º Trimestre", "T4": "4º Trimestre"}


def compute(company: str, p3: pd.DataFrame, geral: pd.DataFrame) -> dict:
    result = {"company": company, "destaque": None, "trimestres": {}}

    if p3.empty:
        log.warning("[%s] P3 vazia", company)
        return result

    cm3 = iomod.col_map(p3)
    cmg = iomod.col_map(geral)
    data_entrada_col = cm3.get("Data Entrada")
    if not data_entrada_col:
        log.warning("[%s] P3 sem coluna Data Entrada", company)
        return result

    # Colunas do P3
    p3_cols = list(p3.columns)
    razao_col = p3_cols[6] if len(p3_cols) > 6 else cm3.get("Razao Social")

    # NF -> SKU count (unique COD PROD per NF) a partir do Geral
    codprod_col = cmg.get("COD PROD")
    if not geral.empty and "_nf" in geral.columns and codprod_col:
        nf_skus = geral.dropna(subset=["_nf"]).groupby("_nf")[codprod_col].nunique()
    else:
        nf_skus = pd.Series(dtype=int)

    # NF -> QUANTIDADE sum (Unidades Recebidas por NF)
    qtd_col = _find_qtd_col(cmg)
    if not geral.empty and "_nf" in geral.columns and qtd_col:
        nf_qtd = geral.dropna(subset=["_nf", qtd_col]).groupby("_nf")[qtd_col].sum()
    else:
        nf_qtd = pd.Series(dtype=float)
        log.warning("[%s] QUANTIDADE nao encontrada no Geral", company)

    # Processar TODOS os meses do ano atual em P3
    yr = config.DESTAQUE.year
    p3_yr = p3[p3[data_entrada_col].dt.year == yr].copy()
    if p3_yr.empty:
        log.warning("[%s] P3 sem dados para ano %d", company, yr)
        return result

    all_months = {}  # month_num -> entry

    for month_num in range(1, 13):
        mask = p3_yr[data_entrada_col].dt.month == month_num
        mdf = p3_yr[mask]
        if mdf.empty:
            continue

        notas_emitidas = len(mdf)
        nfs = set(mdf["_nf"].dropna().astype(int).unique()) if "_nf" in mdf.columns else set()
        nfs_list = list(nfs)
        sku_total = int(nf_skus.reindex(nfs_list).fillna(0).sum()) if nfs else 0
        unidades = int(nf_qtd.reindex(nfs_list).fillna(0).sum()) if nfs else 0
        sku_por_nota = round(sku_total / notas_emitidas, 1) if notas_emitidas else 0.0

        md = date(yr, month_num, 1)
        entry = {
            "mes": config.month_label(md),
            "mes_num": month_num,
            "notas_emitidas": notas_emitidas,
            "sku_total": sku_total,
            "sku_por_nota": sku_por_nota,
            "unidades_recebidas": unidades,
        }
        all_months[month_num] = entry

        # Destaque (mes corrente - 1): adicionar detalhes de fornecedor
        if month_num == config.DESTAQUE.month:
            entry["mes"] = f"{config.month_label(md)} {yr}"
            entry["is_destaque"] = True

            notas_detalhe = []
            forn_data = {}
            for _, row in mdf.iterrows():
                nf = row.get("_nf")
                skus = int(nf_skus.get(nf, 0)) if nf else 0
                nf_display = int(nf) if nf else None
                notas_detalhe.append({"nf": nf_display, "skus": skus})

                razao = row[razao_col] if razao_col and razao_col in mdf.columns else None
                if not pd.isna(razao):
                    razao_str = str(razao).strip()
                    forn_data[razao_str] = forn_data.get(razao_str, 0) + skus

            forn_sorted = sorted(forn_data.items(), key=lambda x: -x[1])
            entry["sku_por_fornecedor"] = [{"fornecedor": f, "skus": s} for f, s in forn_sorted]
            entry["notas_detalhe"] = notas_detalhe
            entry["fornecedores"] = len(forn_sorted)
            result["destaque"] = entry

    # Agrupar em trimestres
    trimestres = {}
    for t_key in ("T1", "T2", "T3", "T4"):
        meses_t = []
        for m_num in range(1, 13):
            if _TRIM_MAP[m_num] == t_key and m_num in all_months:
                meses_t.append({
                    "mes": all_months[m_num]["mes"],
                    "unidades_recebidas": all_months[m_num]["unidades_recebidas"],
                    "notas_emitidas": all_months[m_num]["notas_emitidas"],
                })
        total = sum(e["unidades_recebidas"] for e in meses_t)
        trimestres[t_key] = {
            "label": _TRIM_LABELS[t_key],
            "meses": meses_t,
            "total_unidades": total,
        }

    # Unidades recebidas do ano anterior (mes destaque) para comparativo YoY.
    # Geral/P2 e o arquivo do ano atual — NFs do ano anterior podem nao existir.
    ano_prev = config.DESTAQUE_ANO_PASSADO
    mask_prev = ((p3[data_entrada_col].dt.year == ano_prev.year) &
                 (p3[data_entrada_col].dt.month == ano_prev.month))
    p3_prev = p3[mask_prev]
    if not p3_prev.empty and "_nf" in p3_prev.columns:
        nfs_prev = list(set(p3_prev["_nf"].dropna().astype(int).unique()))
        matched = nf_qtd.reindex(nfs_prev).dropna()
        result["unidades_ano_anterior"] = int(matched.sum()) if not matched.empty else None
    else:
        result["unidades_ano_anterior"] = None

    result["trimestres"] = trimestres
    return result


def _find_qtd_col(cmg: dict) -> str | None:
    """Busca coluna QUANTIDADE case-insensitive (Alinare=UPPER, Novitah=Title)."""
    for k, v in cmg.items():
        if k.upper() == "QUANTIDADE":
            return v
    return None
