"""Pipeline: carrega dados, calcula metricas e exporta resultado consolidado."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from . import config
from . import io as iomod
from . import screen1_notas as s1
from . import screen2_lancamentos as s2
from . import screen3_programacao as s3

log = logging.getLogger("dashboard.pipeline")


def run() -> dict:
    """Executa o pipeline completo e retorna o dicionario de resultados."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    results = {"alinare": {}, "novitah": {}}

    # --- Telas 1 e 2: por empresa (arquivos proprios) ---
    for company in config.COMPANIES:
        log.info("=== Processando %s (Telas 1 e 2) ===", company.upper())
        p1 = iomod.load_planilha1(company)
        p3 = iomod.load_planilha3(company)
        geral = iomod.load_geral(company)

        results[company]["notas_entrada"] = s1.compute(company, p3, geral)
        results[company]["produtos_lancados"] = s2.compute(company, p1)

    # --- Tela 3: sempre do arquivo da Alinare (contem ambas) ---
    log.info("=== Processando Tela 3 (arquivo Alinare) ===")
    lanc = iomod.load_lancamentos("alinare")
    geral_alinare = iomod.load_geral("alinare")
    s3_results = s3.compute_all(lanc, geral_alinare)
    results["alinare"]["proximos_lancamentos"] = s3_results["alinare"]
    results["novitah"]["proximos_lancamentos"] = s3_results["novitah"]

    # --- Exportar ---
    _export(results)
    return results


def _export(results: dict) -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON principal (contrato para o dashboard)
    out = config.OUTPUT_DIR / "data.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    log.info("Exportado: %s", out)

    # Metadados
    meta = {
        "hoje": config.TODAY.isoformat(),
        "destaque": config.month_label(config.DESTAQUE) + f" {config.DESTAQUE.year}",
        "comparacao": [config.month_label(m) for m in config.COMPARACAO_MESES],
        "proximo_mes": config.month_label(config.PROXIMO_MES) + f" {config.PROXIMO_MES.year}",
    }
    with open(config.OUTPUT_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    data = run()
    print("\n=== RESUMO ===")
    for comp in config.COMPANIES:
        d = data[comp]
        s1d = d.get("notas_entrada", {}).get("destaque", {})
        s2d = d.get("produtos_lancados", {}).get("destaque", {})
        s3d = d.get("proximos_lancamentos", {})
        print(f"\n--- {comp.upper()} ---")
        print(f"  T1 Destaque: notas={s1d.get('notas_subiram')} sku_total={s1d.get('sku_total')} sku/nota={s1d.get('sku_por_nota')}")
        print(f"    match: {d.get('notas_entrada',{}).get('match_coverage')}")
        print(f"  T2 Destaque: media_dias={s2d.get('media_dias')} lancamentos={s2d.get('lancamentos')} skus={s2d.get('skus')}")
        print(f"    dia_mais: {s2d.get('dia_com_mais')}")
        print(f"  T3: total_skus={s3d.get('total_skus')} ready={s3d.get('ready')} process={s3d.get('process')} mkt_sent={s3d.get('mkt_sent')}")
