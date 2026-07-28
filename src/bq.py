"""Adapter BigQuery: le o DW (camada ouro/bronze) e devolve DataFrames/records
com a mesma forma que src/io.py devolve a partir do Excel.

Convencao de nomes: as colunas sao renomeadas via alias no SELECT para casar com
os nomes ASCII que o resto do pipeline espera (Data, Data Lancamento, COD PROD,
Data Entrada, Razao Social, _nf, ...). Assim screen1/screen2/pipeline nao mudam.
"""
from __future__ import annotations

import logging
from functools import lru_cache

import pandas as pd

from . import config
from .io import asciize, norm_nf

log = logging.getLogger("dashboard.bq")

PRONTO_KW = ("programado", "finalizado", "lancado")


@lru_cache(maxsize=1)
def _client():
    from google.cloud import bigquery  # import tardo: so quando BQ e usado
    return bigquery.Client(project=config.BQ_PROJECT)


def query_df(sql: str) -> pd.DataFrame:
    """Roda query no BigQuery e devolve DataFrame pandas."""
    log.info("BQ query: %s", " ".join(sql.split())[:160])
    df = _client().query(sql).to_dataframe(create_bqstorage_client=True)
    log.info("BQ retornou %d linhas, %d colunas", len(df), len(df.columns))
    return df


def _full(table: str, dataset: str | None = None) -> str:
    ds = dataset or config.BQ_DATASET
    return f"`{config.BQ_PROJECT}.{ds}.{table}`"


# ---------------------------------------------------------------------------
# Tela 2 - Produtos Lancados (P1)
#   ouro.lancamentos_<emp>   -> FINALIZADO/PRODUTO/DATA_LANCAMENTO/DATA_VIRADA (TIMESTAMP)
#   ouro.itens_lancados_efetivo_<emp> -> DATA_LANCAMENTO e STRING (cast necessario)
# ---------------------------------------------------------------------------
def load_p1_bq(company: str) -> pd.DataFrame:
    table = config.bq_t2_table(company)
    is_efetivo = config.BQ_T2_SOURCE == "itens_efetivo"
    if is_efetivo:
        prod_col = "COD_BARRAS" if company == "novitah" else "COD_PROD"
    else:
        prod_col = "PRODUTO"
    # DATA_VIRADA so existe em lancamentos_* (nao em itens_lancados_efetivo_*)
    virada = "" if is_efetivo else ",\n      SAFE_CAST(DATA_VIRADA AS TIMESTAMP) AS `Data Virada`"
    sql = f"""
    SELECT
      SAFE_CAST(FINALIZADO AS TIMESTAMP)      AS `Data`,
      SAFE_CAST(DATA_LANCAMENTO AS TIMESTAMP) AS `Data Lancamento`,
      SAFE_CAST(`{prod_col}` AS INT64)        AS `Produto`{virada}
    FROM {_full(table)}
    WHERE FINALIZADO IS NOT NULL
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
      nf.Numero,
      SAFE_CAST(nf.Data_Entrada AS DATE) AS `Data Entrada`,
      fo.Fornecedor                      AS `Razao Social`
    FROM {_full(f"nf_{company}")} nf
    LEFT JOIN {_full("fornecedor")} fo
      ON nf.id_fornecedor = fo.id
    """
    df = query_df(sql)
    # screen1: hack posicional razao_col = p3_cols[6] if len>6 else col_map("Razao Social").
    # Devolvendo <=6 colunas nomeadas, cai no fallback e acha "Razao Social".
    # BQ ja devolve NF como numerico (Int64 nullable); norm_nf quebra com
    # nullable Int64 (408.0 -> str -> "4080"), logo converter direto.
    df["_nf"] = pd.to_numeric(df["Numero"], errors="coerce")
    df["Data Entrada"] = pd.to_datetime(df["Data Entrada"], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Tela 1 - Geral / Estoque (P2)
#   Alinare: COD_PROD ; Novitah: COD_BARRAS -> alias "COD PROD" (igual ao Excel)
# ---------------------------------------------------------------------------
def load_geral_bq(company: str) -> pd.DataFrame:
    cod_col = "COD_BARRAS" if company == "novitah" else "COD_PROD"
    sql = f"""
    SELECT
      `{cod_col}`   AS `COD PROD`,
      QUANTIDADE,
      NF,
      FORNECEDOR,
      MARCA,
      LANcAMENTO    AS `LANCAMENTO`
    FROM {_full(config.BQ_GERAL_TABLES[company])}
    """
    df = query_df(sql)
    df["_nf"] = pd.to_numeric(df["NF"], errors="coerce")
    df["LANCAMENTO"] = pd.to_datetime(df["LANCAMENTO"], errors="coerce")
    # O DW carrega linhas duplicadas. Dedup por (NF, COD PROD, QUANTIDADE):
    # remove duplicacao exata mas preserva entradas legitimas com qtd diferente
    # (mesmo NF+produto recebido em 2 lotes distintos).
    antes = len(df)
    df = df.drop_duplicates(subset=["_nf", "COD PROD", "QUANTIDADE"], keep="first")
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
    SELECT BU, DATA, EMBARQUE_PEDRA, EMBARQUE, MKT, STATUS
    FROM {_full("lancamentos", dataset=config.BQ_T3_DATASET)}
    """
    df = query_df(sql)
    return parse_lancamentos_df(df)


def parse_lancamentos_df(df: pd.DataFrame) -> list[dict]:
    """Equivalente a io.parse_lancamentos(ws), mas sobre DataFrame bronze."""
    import pandas as _pd
    records = []

    for _, row in df.iterrows():
        bu_raw = row.get("BU")
        bu_str = str(bu_raw).strip().lower() if bu_raw is not None and not _pd.isna(bu_raw) else ""
        if bu_str not in ("alinare", "novitah"):
            continue

        data_raw = row.get("DATA")
        status = row.get("STATUS")
        mkt_val = row.get("MKT")
        desc = row.get("EMBARQUE_PEDRA")
        embarque = row.get("EMBARQUE")

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
