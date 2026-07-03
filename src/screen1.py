"""Tela 1 - Notas de Entrada.

- Notas Emitidas: contar linhas P3 com Data Entrada no mes
- SKU/nota: join P3._nf <-> Geral._nf, contar COD PROD
- SKU/Fornecedor: usar Razao Social (coluna G) do P3, somar SKUs das notas
"""
from __future__ import annotations

import logging

import pandas as pd

from . import config
from . import io as iomod

log = logging.getLogger("dashboard.screen1")


def compute(company: str, p3: pd.DataFrame, geral: pd.DataFrame) -> dict:
    months = [config.DESTAQUE_ANO_PASSADO] if False else []  # Tela 1 sem 2025
    months = config.ALL_MONTHS
    result = {"company": company, "destaque": None, "comparacao": []}

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
    numero_col = cm3.get("Numero")

    # NF -> SKU count a partir do Geral
    codprod_col = cmg.get("COD PROD")
    if not geral.empty and "_nf" in geral.columns and codprod_col:
        nf_skus = geral.dropna(subset=["_nf"]).groupby("_nf")[codprod_col].nunique()
    else:
        nf_skus = pd.Series(dtype=int)

    for i, md in enumerate(months):
        mask = (p3[data_entrada_col].dt.year == md.year) & (p3[data_entrada_col].dt.month == md.month)
        mdf = p3[mask]

        notas_emitidas = len(mdf)
        if notas_emitidas == 0:
            entry = _empty_entry(md, i == 0)
        else:
            # SKU por nota via join com Geral
            nfs = set(mdf["_nf"].dropna().astype(int).unique()) if "_nf" in mdf.columns else set()
            sku_total = int(nf_skus.reindex(list(nfs)).sum()) if nfs else 0
            sku_por_nota = round(sku_total / notas_emitidas, 1) if notas_emitidas else 0.0

            # Detalhe por nota
            notas_detalhe = []
            for _, row in mdf.iterrows():
                nf = row.get("_nf")
                skus = int(nf_skus.get(nf, 0)) if nf else 0
                nf_display = int(nf) if nf else None
                notas_detalhe.append({"nf": nf_display, "skus": skus})

            # SKU por fornecedor (Razao Social do P3)
            forn_data = {}
            for _, row in mdf.iterrows():
                nf = row.get("_nf")
                razao = row[razao_col] if razao_col and razao_col in mdf.columns else None
                if pd.isna(razao):
                    continue
                razao_str = str(razao).strip()
                skus = int(nf_skus.get(nf, 0)) if nf else 0
                forn_data[razao_str] = forn_data.get(razao_str, 0) + skus

            forn_sorted = sorted(forn_data.items(), key=lambda x: -x[1])
            sku_fornecedor = [{"fornecedor": f, "skus": s} for f, s in forn_sorted]

            entry = {
                "mes": f"{config.month_label(md)} {md.year}",
                "is_destaque": i == 0,
                "notas_emitidas": notas_emitidas,
                "sku_total": sku_total,
                "sku_por_nota": sku_por_nota,
                "fornecedores": len(forn_sorted),
                "sku_por_fornecedor": sku_fornecedor,
                "notas_detalhe": notas_detalhe,
            }

        if i == 0:
            result["destaque"] = entry
        else:
            result["comparacao"].append(entry)

    return result


def _empty_entry(md, is_destaque):
    return {
        "mes": f"{config.month_label(md)} {md.year}",
        "is_destaque": is_destaque,
        "notas_emitidas": 0,
        "sku_total": 0,
        "sku_por_nota": 0.0,
        "fornecedores": 0,
        "sku_por_fornecedor": [],
        "notas_detalhe": [],
    }
