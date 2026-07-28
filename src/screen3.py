"""Tela 3 - Lancamentos Programados.

Dados da aba Lancamentos do arquivo P2 da Alinare.
Filtra itens do proximo mes (mes atual do sistema) + pendentes.
Split por empresa (Alinare / Novitah).
Status: Programado/Finalizado/Lancado -> OK; resto -> EM PROCESSO.
MKT: se contem "entregue" no texto -> OK.
"""
from __future__ import annotations

import logging

from . import config

log = logging.getLogger("dashboard.screen3")


def compute(records) -> dict[str, dict]:
    """Processa registros de lancamentos (Excel parse ou BQ) e retorna dados
    para ambas as empresas."""
    if records is None:
        records = []

    results = {}
    for company in config.COMPANIES:
        items = [r for r in records if r["empresa"] == company]
        ok_count = sum(1 for i in items if i["status"] == "OK")
        proc_count = sum(1 for i in items if i["status"] == "EM PROCESSO")
        mkt_ok = sum(1 for i in items if i["mkt"] == "OK")

        results[company] = {
            "company": company,
            "mes": f"{config.month_label(config.PROXIMO_MES)} {config.PROXIMO_MES.year}",
            "total_itens": len(items),
            "status_ok": ok_count,
            "status_processo": proc_count,
            "mkt_ok": mkt_ok,
            "mkt_processo": len(items) - mkt_ok,
            "itens": items,
        }

    return results
