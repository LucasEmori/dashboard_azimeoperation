"""Pipeline: carrega planilhas, calcula metricas e exporta JSON consolidado."""
from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

from . import config
from . import io as iomod
from . import screen1 as s1
from . import screen2 as s2
from . import screen3 as s3

log = logging.getLogger("dashboard.pipeline")


def _month_range(start_ym: tuple[int, int], end_ym: tuple[int, int]) -> list[date]:
    """Retorna lista de datas (dia 1) entre start e end, decrescente."""
    y, m = end_ym
    sy, sm = start_ym
    res = []
    while (y, m) >= (sy, sm):
        res.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return res


def run(progress_cb=None) -> dict:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    src = config.DATA_SOURCE.upper()
    log.info("=== FONTE DE DADOS: %s ===", src)

    if progress_cb:
        progress_cb("Iniciando pulls do BD", 0)

    # 1. Pulls seriais
    # Extrair todos dataframes do Supabase sequencialmente p/ nao bater connection limit (pgbouncer).
    # Como e thread background, demorar 2 min nao trava API nem da timeout 150s.
    dfs = {}
    def do_load(k, fn, *args):
        if progress_cb:
            progress_cb(f"Extraindo {k}...", 10)
        dfs[k] = fn(*args)

    for c in config.COMPANIES:
        do_load(f"p1_{c}", iomod.load_p1, c)
        do_load(f"p3_{c}", iomod.load_p3, c)
        do_load(f"geral_{c}", iomod.load_geral, c)

    if config.DATA_SOURCE == "bq":
        from .bq import query_df, _full
        def get_bronze():
            sql = f"SELECT bu, data, embarque_pedra, embarque, mkt, status FROM {_full('lancamentos', schema=config.PG_T3_SCHEMA)}"
            return query_df(sql)
        do_load("bronze", get_bronze)
    else:
        def get_bronze_excel():
            return iomod.load_lancamentos()
        do_load("bronze_ws", get_bronze_excel)

    # 2. Gerar lista de meses p/ processar: Jan/2024 ate mes_atual
    meses_alvo = _month_range((2024, 1), (config.TODAY.year, config.TODAY.month))

    # Montar estrutura JSON
    results = {
        "meta": {
            "hoje": config.TODAY.isoformat(),
            "months": [m.strftime("%Y-%m") for m in meses_alvo],
            "month_labels": {m.strftime("%Y-%m"): f"{config.month_label(m)} {m.year}" for m in meses_alvo},
            "destaque_iso": config.TODAY.isoformat(), # default UI
        },
        "by_month": {}
    }

    if progress_cb:
        progress_cb("Processando metricas", 50)

    for idx, M in enumerate(meses_alvo):
        # State config dita comportamento de S1/S2/S3
        config.set_destaque(M)

        m_key = M.strftime("%Y-%m")
        results["by_month"][m_key] = {"alinare": {}, "novitah": {}}

        # Meta legado/padrao no top level usa o destaque configurado p/ compatibilidade basica.
        if idx == 0:
            results["meta"].update(_build_meta())

        for company in config.COMPANIES:
            p1 = dfs[f"p1_{company}"]
            p3 = dfs[f"p3_{company}"]
            geral = dfs[f"geral_{company}"]

            results["by_month"][m_key][company]["tela1"] = s1.compute(company, p3, geral)
            results["by_month"][m_key][company]["tela2"] = s2.compute(company, p1)

        # Tela 3
        if config.DATA_SOURCE == "bq":
            from .bq import parse_lancamentos_df
            records = parse_lancamentos_df(dfs["bronze"], config.PROXIMO_MES)
        else:
            records = iomod.parse_lancamentos(dfs["bronze_ws"])

        s3_results = s3.compute(records)
        results["by_month"][m_key]["alinare"]["tela3"] = s3_results["alinare"]
        results["by_month"][m_key]["novitah"]["tela3"] = s3_results["novitah"]

    if progress_cb:
        progress_cb("Exportando", 90)

    _export(results)

    if progress_cb:
        progress_cb("Concluido", 100)

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
