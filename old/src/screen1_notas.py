"""Tela 1 - Notas de Entrada.

Metricas por mes:
  - Notas que subiram (count distinct Numero com Data Entrada no mes)
  - SKU total e SKU/nota medio (join P3 <-> Geral.NF)
  - SKU por fornecedor (ranking)
"""
from __future__ import annotations

import logging

import pandas as pd

from . import config
from . import io as iomod
from .clean import normalize_nf, company_from_marca

log = logging.getLogger("dashboard.screen1")


def compute(company: str, p3: pd.DataFrame, geral: pd.DataFrame) -> dict:
    """Calcula todas as metricas da Tela 1 para uma empresa."""
    months = config.ALL_MONTHS
    result = {
        "company": company,
        "destaque": None,
        "comparison": [],
        "sku_por_fornecedor_destaque": [],
        "match_coverage": None,
    }

    if p3.empty:
        log.warning("[%s] Planilha 3 vazia", company)
        return result
    if geral.empty:
        log.warning("[%s] Geral vazia", company)

    # --- Filtrar Geral por MARCA da empresa ---
    marca_map = iomod.detect_marca_codes(geral)
    empresa_marca = marca_map.get(company, set())
    if empresa_marca:
        g = geral[geral["MARCA"].astype(str).str.upper().isin(empresa_marca)].copy()
    else:
        g = geral.copy()
    log.info("[%s] Geral filtrado por MARCA %s: %d linhas", company, empresa_marca, len(g))

    # --- NF -> SKU map a partir do Geral ---
    if not g.empty and "NF" in g.columns:
        g["_nf_key"] = g["NF"].apply(normalize_nf)
        g_valid = g.dropna(subset=["_nf_key"])
        nf_to_skus = g_valid.groupby("_nf_key")["COD PROD"].nunique()
        # NF -> fornecedor (primeiro nao-nulo)
        nf_to_forn = (
            g_valid.dropna(subset=["FORNECEDOR"])
            .groupby("_nf_key")["FORNECEDOR"]
            .first()
        )
        empresa_nfs = set(g_valid["_nf_key"].dropna().unique())
    else:
        nf_to_skus = pd.Series(dtype=int)
        nf_to_forn = pd.Series(dtype=object)
        empresa_nfs = set()

    # --- Processar P3 ---
    p3 = p3.copy()
    if "Data Entrada" not in p3.columns:
        log.warning("[%s] P3 sem coluna Data Entrada", company)
        return result
    p3["_nf_key"] = p3["Número"].apply(normalize_nf)
    p3 = p3.dropna(subset=["Data Entrada"])

    # Filtrar notas pertencentes a esta empresa (via NF match com Geral)
    p3_emp = p3[p3["_nf_key"].isin(empresa_nfs)].copy() if empresa_nfs else p3.copy()
    matched = len(p3_emp["_nf_key"].dropna().unique()) if empresa_nfs else 0
    total_nfs_p3 = len(p3["_nf_key"].dropna().unique())
    result["match_coverage"] = {
        "empresa_nfs_in_geral": len(empresa_nfs),
        "p3_nfs_total": total_nfs_p3,
        "p3_nfs_matched": matched,
    }

    # --- Calcular por mes ---
    for i, month_date in enumerate(months):
        ym = config.ym_key(month_date)
        mask = p3_emp["Data Entrada"].apply(
            lambda d: d is not pd.NaT and (d.year, d.month) == ym
        )
        month_notas = p3_emp[mask]
        nf_keys = set(month_notas["_nf_key"].dropna().unique())
        notas_count = len(nf_keys) if nf_keys else len(month_notas["Número"].dropna().unique())

        # SKU total: somar SKUs das notas do mes
        sku_total = int(nf_to_skus.reindex(list(nf_keys)).sum()) if nf_keys else 0
        sku_por_nota = round(sku_total / notas_count, 1) if notas_count else 0.0

        # SKU por fornecedor (no mes destaque)
        forn_data = []
        if nf_keys:
            forn_skus = (
                g_valid[g_valid["_nf_key"].isin(nf_keys)]
                .dropna(subset=["FORNECEDOR"])
                .groupby("FORNECEDOR")["COD PROD"]
                .nunique()
                .sort_values(ascending=False)
            )
            forn_data = [
                {"fornecedor": str(f), "skus": int(s)}
                for f, s in forn_skus.head(15).items()
            ]
        fornecedores_ativos = len(forn_data)

        entry = {
            "month": config.month_label(month_date),
            "month_date": month_date.isoformat(),
            "is_destaque": i == 0,
            "notas_subiram": int(notas_count),
            "sku_total": sku_total,
            "sku_por_nota": sku_por_nota,
            "fornecedores_ativos": fornecedores_ativos,
        }
        if i == 0:
            result["destaque"] = entry
            result["sku_por_fornecedor_destaque"] = forn_data
        else:
            result["comparison"].append(entry)

    return result
