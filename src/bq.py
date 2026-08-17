"""Adapter Postgres/Supabase: le o DW (camadas ouro/bronze) e devolve
DataFrames/records com a mesma forma que src/io.py devolve a partir do Excel.

Substitui o antigo adapter BigQuery (GBQ descontinuado). O esquema mudou:
  - Projeto.dataset.tabela  (BQ)  ->  schema.tabela  (PG: ouro.lancamentos_alinare)
  - Colunas UPPER_CASE com _      ->  lowercase snake_case
  - ouro.fornecedor (unico)       ->  ouro.fornecedores_alinare / _novitah
  - AS TIMESTAMP / INT64          ->  TIMESTAMP / BIGINT nativos
Os aliases no SELECT preservam os nomes ASCII que screen1/screen2/pipeline esperam.
"""
from __future__ import annotations

import logging
from functools import lru_cache

import pandas as pd
import psycopg2

from . import config
from .io import asciize

log = logging.getLogger("dashboard.bq")

PRONTO_KW = ("programado", "finalizado", "lancado")


@lru_cache(maxsize=1)
def _conn():
    return psycopg2.connect(config.PG_DSN, connect_timeout=15)


def query_df(sql: str) -> pd.DataFrame:
    """Roda query no Postgres e devolve DataFrame pandas."""
    log.info("PG query: %s", " ".join(sql.split())[:160])
    conn = _conn()
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        df = pd.DataFrame(cur.fetchall(), columns=cols)
    log.info("PG retornou %d linhas, %d colunas", len(df), len(df.columns))
    return df


def _full(table: str, schema: str | None = None) -> str:
    sc = schema or config.PG_SCHEMA
    return f'"{sc}"."{table}"'


# ---------------------------------------------------------------------------
# Tela 2 - Produtos Lancados (P1)
#   ouro.lancamentos_<emp> -> FINALIZADO/DATA_LANCAMENTO/DATA_VIRADA (timestamptz)
#   ouro.itens_lancados_efetivo_<emp> -> DATA_LANCAMENTO e STRING (cast necessario)
# ---------------------------------------------------------------------------
def load_p1_bq(company: str) -> pd.DataFrame:
    table = config.pg_t2_table(company)
    is_efetivo = config.PG_T2_SOURCE == "itens_efetivo"
    if is_efetivo:
        prod_col = "cod_barras" if company == "novitah" else "cod_prod"
    else:
        prod_col = "produto"
    # data_virada so existe em lancamentos_* (nao em itens_lancados_efetivo_*)
    virada = "" if is_efetivo else ",\n      data_virada AS \"Data Virada\""
    sql = f"""
    SELECT
      finalizado                AS "Data",
      data_lancamento           AS "Data Lancamento",
      {prod_col}                AS "Produto"{virada}
    FROM {_full(table)}
    WHERE finalizado IS NOT NULL
    """
    df = query_df(sql)
    # Garantir tipos datetime (screen2 usa .dt)
    for c in ("Data", "Data Lancamento", "Data Virada"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Tela 1 - Notas de Entrada (P3) + join fornecedor (Razao Social)
# ---------------------------------------------------------------------------
def load_p3_bq(company: str) -> pd.DataFrame:
    sql = f"""
    SELECT
      nf.numero          AS "Numero",
      nf.data_entrada    AS "Data Entrada",
      fo.fornecedor      AS "Razao Social"
    FROM {_full(f"nf_{company}")} nf
    LEFT JOIN {_full(config.PG_FORN_TABLES[company])} fo
      ON nf.id_fornecedor = fo.id
    """
    df = query_df(sql)
    # BQ ja devolve NF como numerico; mantem compatibilidade com norm_nf
    df["_nf"] = pd.to_numeric(df["Numero"], errors="coerce")
    df["Data Entrada"] = pd.to_datetime(df["Data Entrada"], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Tela 1 - Geral / Estoque (P2)
#   Alinare: cod_prod ; Novitah: cod_barras -> alias "COD PROD" (igual ao Excel)
# ---------------------------------------------------------------------------
def load_geral_bq(company: str) -> pd.DataFrame:
    cod_col = "cod_barras" if company == "novitah" else "cod_prod"
    sql = f"""
    SELECT
      {cod_col}   AS "COD PROD",
      quantidade,
      nf,
      fornecedor,
      marca,
      lancamento  AS "LANCAMENTO"
    FROM {_full(config.PG_GERAL_TABLES[company])}
    """
    df = query_df(sql)
    df["_nf"] = pd.to_numeric(df["nf"], errors="coerce")
    df["LANCAMENTO"] = pd.to_datetime(df["LANCAMENTO"], errors="coerce")
    # O DW carrega linhas duplicadas. Dedup por (NF, COD PROD, QUANTIDADE):
    # remove duplicacao exata mas preserva entradas legitimas com qtd diferente
    # (mesmo NF+produto recebido em 2 lotes distintos).
    antes = len(df)
    df = df.drop_duplicates(subset=["_nf", "COD PROD", "quantidade"], keep="first")
    if len(df) != antes:
        log.info("Geral %s: dedup %d -> %d linhas", company, antes, len(df))
    return df


# ---------------------------------------------------------------------------
# Tela 3 - Proximos Lancamentos (bronze.lancamentos)
#   bronze e a unica camada com MKT e EMBARQUE (ouro/prata perderam no ETL).
#   DATA/MKT/STATUS sao STRING; parse igual ao parse_lancamentos do Excel.
# ---------------------------------------------------------------------------
def load_lancamentos_bq() -> list[dict]:
    sql = f"""
    SELECT bu, data, embarque_pedra, embarque, mkt, status
    FROM {_full("lancamentos", schema=config.PG_T3_SCHEMA)}
    """
    df = query_df(sql)
    return parse_lancamentos_df(df)


def parse_lancamentos_df(df: pd.DataFrame) -> list[dict]:
    """Equivalente a io.parse_lancamentos(ws), mas sobre DataFrame bronze."""
    import pandas as _pd
    records = []

    for _, row in df.iterrows():
        bu_raw = row.get("bu")
        bu_str = str(bu_raw).strip().lower() if bu_raw is not None and not _pd.isna(bu_raw) else ""
        if bu_str not in ("alinare", "novitah"):
            continue

        data_raw = row.get("data")
        status = row.get("status")
        mkt_val = row.get("mkt")
        desc = row.get("embarque_pedra")
        embarque = row.get("embarque")

        # Classificar status (normalizando acentos)
        s_norm = asciize(str(status)).lower() if status is not None and not _pd.isna(status) else ""
        is_ready = any(kw in s_norm for kw in PRONTO_KW)

        mkt_ok = (
            isinstance(mkt_val, str) and "entregue" in mkt_val.lower()
        ) or (mkt_val is not None and not _pd.isna(mkt_val) and "entregue" in str(mkt_val).lower())

        # Data: datetime, "Pendente", ou outro (string no bronze)
        data_val = None
        in_scope = False
        if data_raw is None or (isinstance(data_raw, float) and _pd.isna(data_raw)):
            continue
        if isinstance(data_raw, str) and data_raw.strip().lower() == "pendente":
            data_val = "Sem data"
            in_scope = True
        else:
            dt = _pd.to_datetime(data_raw, errors="coerce")
            if _pd.notna(dt) and dt.year == config.PROXIMO_MES.year and dt.month == config.PROXIMO_MES.month:
                data_val = dt.strftime("%d/%m")
                in_scope = True

        if not in_scope:
            continue

        records.append({
            "empresa": bu_str,
            "data": data_val,
            "descricao": str(desc).strip() if desc is not None and not _pd.isna(desc) else "",
            "embarque": str(embarque).strip() if embarque is not None and not _pd.isna(embarque) else "",
            "status_raw": str(status).strip() if status is not None and not _pd.isna(status) else "",
            "status": "OK" if is_ready else "EM PROCESSO",
            "mkt": "OK" if mkt_ok else "EM PROCESSO",
        })

    return records
