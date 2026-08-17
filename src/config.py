"""Configuracao central: caminhos, meses dinamicos, constantes."""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

COMPANIES = ("alinare", "novitah")
COMPANY_LABELS = {"alinare": "ALINARE", "novitah": "NOVITAH"}
COMPANY_DIRS = {c: DATA_DIR / c for c in COMPANIES}

# ---------------------------------------------------------------------------
# Meses dinamicos a partir da data do sistema
# ---------------------------------------------------------------------------
TODAY = date.today()

def sub_months(d: date, n: int) -> date:
    m = d.month - n
    y = d.year
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1)

DESTAQUE = sub_months(TODAY, 0)  # mes atual (Julho/2026)
COMPARACAO_MESES = []
DESTAQUE_ANO_PASSADO = date(TODAY.year, TODAY.month, 1)
PROXIMO_MES = date(TODAY.year, TODAY.month, 1)
ALL_MONTHS = []

def set_destaque(d: date) -> None:
    global DESTAQUE, COMPARACAO_MESES, DESTAQUE_ANO_PASSADO, PROXIMO_MES, ALL_MONTHS, TODAY
    # Define o mes base
    DESTAQUE = date(d.year, d.month, 1)
    # 3 meses anteriores ao destaque
    COMPARACAO_MESES = [sub_months(DESTAQUE, i) for i in range(3, 0, -1)]
    # Mesmo mes, ano passado
    DESTAQUE_ANO_PASSADO = date(DESTAQUE.year - 1, DESTAQUE.month, 1)
    # Proximo mes baseia-se em TODAY ou no destaque escolhido?
    # Se user volta no tempo, Tela 3 (proximo mes) deve ser mes+1?
    # Originalmente baseia-se em TODAY (nao sub_months). Vou manter +1 do destaque.
    PROXIMO_MES = date(DESTAQUE.year + (DESTAQUE.month == 12), (DESTAQUE.month % 12) + 1, 1)

    ALL_MONTHS = [DESTAQUE] + COMPARACAO_MESES

# Inicializa state padrão
set_destaque(TODAY)

_MONTH_NAMES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
_WEEKDAYS = [
    "Segunda-feira", "Terça-feira", "Quarta-feira",
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo",
]


def month_label(d: date) -> str:
    return _MONTH_NAMES[d.month - 1]


def weekday_pt(d) -> str:
    return _WEEKDAYS[d.weekday()]


def ym(d: date) -> tuple[int, int]:
    return (d.year, d.month)

# ---------------------------------------------------------------------------
# Abas da Planilha Geral por empresa
# ---------------------------------------------------------------------------
SHEET_GERAL = {"alinare": "Geral", "novitah": "BASE GERAL"}

# ---------------------------------------------------------------------------
# Fonte de dados: "excel" (planilhas locais) ou "bq" (DW: antes BigQuery,
# agora Supabase/Postgres) ou "pg" (alias de bq p/ retrocompatibilidade).
# Valor "bq" mantido p/ nao quebrar env existente (DATA_SOURCE=bq no Railway).
# ---------------------------------------------------------------------------
_v = os.getenv("DATA_SOURCE", "bq").lower()
DATA_SOURCE = "bq" if _v in ("bq", "pg") else _v

# ---------------------------------------------------------------------------
# Supabase / Postgres (substitui BigQuery)
# String completa opcional; se ausente, monta das partes.
# Ex (Supabase pooler): postgresql://postgres.xzoohqiejbuaskpiktfj:pwd@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
# ---------------------------------------------------------------------------
PG_DSN = os.getenv(
    "PG_DSN",
    "postgresql://postgres.xzoohqiejbuaskpiktfj:azime202600@aws-0-sa-east-1.pooler.supabase.com:6543/postgres",
)

# Schemas do DW (mesma semantica das antigas camadas BQ ouro/bronze)
PG_SCHEMA = os.getenv("PG_SCHEMA", "ouro")        # telas 1 e 2
PG_T3_SCHEMA = os.getenv("PG_T3_SCHEMA", "bronze")  # tela 3: so bronze tem MKT/EMBARQUE

# Tabela de Tela 2 (Produtos Lancados). Alterna via env para comparacao:
#   "lancamentos"   -> ouro.lancamentos_<emp>     (bate com P1, ~100%)
#   "itens_efetivo" -> ouro.itens_lancados_efetivo_<emp>  (~3%, distorce)
PG_T2_SOURCE = os.getenv("PG_T2_SOURCE", "lancamentos").lower()

PG_TABLES = {
    "p3": "{emp}",              # nf_alinare / nf_novitah  (Tela 1 notas)
    "geral": "{emp}",           # geral_alinare / geral_novitah
    "lancamentos_t3": "lancamentos",  # bronze.lancamentos (Tela 3)
}

# Tela 1 (Geral): geral_<empresa> (bruto). NAO geral_estoque_*.
PG_GERAL_TABLES = {
    "alinare": os.getenv("PG_GERAL_ALINARE", "geral_alinare"),
    "novitah": os.getenv("PG_GERAL_NOVITAH", "geral_novitah"),
}

# Tela 1 (Notas): tabela de fornecedores por empresa (ouro.fornecedores_<emp>).
# Antes BQ usava tabela unica `fornecedor`; Postgres tem uma por empresa.
PG_FORN_TABLES = {
    "alinare": os.getenv("PG_FORN_ALINARE", "fornecedores_alinare"),
    "novitah": os.getenv("PG_FORN_NOVITAH", "fornecedores_novitah"),
}


def pg_t2_table(company: str) -> str:
    """Nome da tabela de Tela 2 conforme PG_T2_SOURCE."""
    if PG_T2_SOURCE == "itens_efetivo":
        return f"itens_lancados_efetivo_{company}"
    return f"lancamentos_{company}"


# ---------------------------------------------------------------------------
# Cores da marca
# ---------------------------------------------------------------------------
BRAND = {
    "alinare": {
        "bg": "#1a237e", "surface": "#283593", "accent": "#3949ab",
        "chart": "#7986cb",
    },
    "novitah": {
        "bg": "#a07a7a", "surface": "#8d6b6b", "accent": "#b88e8e",
        "chart": "#d7a9a9",
    },
}
