"""Pipeline: carrega planilhas, calcula metricas e exporta JSON consolidado."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from . import config
from . import io as iomod
from . import screen1 as s1
from . import screen2 as s2
from . import screen3 as s3

log = logging.getLogger("dashboard.pipeline")


def run() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    src = config.DATA_SOURCE.upper()
    log.info("=== FONTE DE DADOS: %s ===", src)

    results = {"meta": _build_meta(), "alinare": {}, "novitah": {}}

    # Telas 1 e 2: por empresa
    for company in config.COMPANIES:
        log.info("=== Processando %s (Telas 1 e 2) ===", company.upper())
        p1 = iomod.load_p1(company)
        p3 = iomod.load_p3(company)
        geral = iomod.load_geral(company)

        results[company]["tela1"] = s1.compute(company, p3, geral)
        results[company]["tela2"] = s2.compute(company, p1)

    # Tela 3: sempre do arquivo da Alinare (Excel) ou bronze.lancamentos (BQ)
    log.info("=== Processando Tela 3 ===")
    if config.DATA_SOURCE == "bq":
        records = iomod.load_lancamentos_bq()
    else:
        ws = iomod.load_lancamentos()
        records = iomod.parse_lancamentos(ws)
    s3_results = s3.compute(records)
    results["alinare"]["tela3"] = s3_results["alinare"]
    results["novitah"]["tela3"] = s3_results["novitah"]

    _export(results)
    return results


def _build_meta() -> dict:
    return {
        "hoje": config.TODAY.isoformat(),
        "destaque": f"{config.month_label(config.DESTAQUE)} {config.DESTAQUE.year}",
        "destaque_iso": config.DESTAQUE.isoformat(),
        "comparacao": [f"{config.month_label(m)} {m.year}" for m in config.COMPARACAO_MESES],
        "comparacao_iso": [m.isoformat() for m in config.COMPARACAO_MESES],
        "destaque_ano_passado": f"{config.month_label(config.DESTAQUE_ANO_PASSADO)} {config.DESTAQUE_ANO_PASSADO.year}",
        "destaque_ano_passado_iso": config.DESTAQUE_ANO_PASSADO.isoformat(),
        "proximo_mes": f"{config.month_label(config.PROXIMO_MES)} {config.PROXIMO_MES.year}",
        "proximo_mes_iso": config.PROXIMO_MES.isoformat(),
    }


def _export(results: dict) -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = config.OUTPUT_DIR / "data.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    log.info("Exportado: %s", out)


if __name__ == "__main__":
    data = run()
    print("\n=== RESUMO ===")
    meta = data["meta"]
    print(f"Destaque: {meta['destaque']}")
    print(f"Comparacao: {meta['comparacao']}")
    print(f"Ano anterior: {meta['destaque_ano_passado']}")
    print(f"Proximo: {meta['proximo_mes']}")
    for comp in config.COMPANIES:
        d = data[comp]
        t1 = d.get("tela1", {}).get("destaque", {})
        t2 = d.get("tela2", {}).get("destaque", {})
        t3 = d.get("tela3", {})
        print(f"\n--- {comp.upper()} ---")
        print(f"  T1: notas={t1.get('notas_emitidas')} sku_total={t1.get('sku_total')} forn={t1.get('fornecedores')}")
        print(f"  T2: lanc={t2.get('lancamentos')} skus={t2.get('skus')} media={t2.get('media_prazo')} pico={t2.get('dia_pico')}")
        print(f"  T3: itens={t3.get('total_itens')} ok={t3.get('status_ok')} proc={t3.get('status_processo')} mkt={t3.get('mkt_ok')}")
