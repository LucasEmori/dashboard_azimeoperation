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
# Ordem cronologica (mais antigo -> mais recente): Marco, Abril, Maio
COMPARACAO_MESES = [sub_months(DESTAQUE, i) for i in range(3, 0, -1)]
DESTAQUE_ANO_PASSADO = date(DESTAQUE.year - 1, DESTAQUE.month, 1)
PROXIMO_MES = date(TODAY.year, TODAY.month, 1)

ALL_MONTHS = [DESTAQUE] + COMPARACAO_MESES

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
# Fonte de dados: "excel" (planilhas locais) ou "bq" (BigQuery / DW)
# ---------------------------------------------------------------------------
DATA_SOURCE = os.getenv("DATA_SOURCE", "bq").lower()
BQ_PROJECT = os.getenv("BQ_PROJECT", "operationsdw")

# Camada do DW e nomes das tabelas. Sobrescrever via env se necessario.
BQ_DATASET = os.getenv("BQ_DATASET", "ouro")
BQ_T3_DATASET = os.getenv("BQ_T3_DATASET", "bronze")  # Tela 3: so bronze tem MKT/EMBARQUE

# Tabela de Tela 2 (Produtos Lancados). Alterna via env para comparacao:
#   "lancamentos"        -> ouro.lancamentos_<emp>     (bate com P1, ~100%)
#   "itens_efetivo"      -> ouro.itens_lancados_efetivo_<emp>  (~3%, distorce)
BQ_T2_SOURCE = os.getenv("BQ_T2_SOURCE", "lancamentos").lower()

BQ_TABLES = {
    "p3": "{emp}",            # nf_alinare / nf_novitah  (Tela 1 notas)
    "geral": "{emp}",         # geral_estoque_alinare / geral_estoque_novitah
    "lancamentos_t3": "lancamentos",  # bronze.lancamentos (Tela 3)
    "fornecedor": "fornecedor",
}

def bq_t2_table(company: str) -> str:
    """Nome da tabela de Tela 2 conforme BQ_T2_SOURCE."""
    if BQ_T2_SOURCE == "itens_efetivo":
        return f"itens_lancados_efetivo_{company}"
    return f"lancamentos_{company}"

# Tela 1 (Geral): usar geral_<empresa> (bruto). NAO geral_estoque_* (agrupa
# lancamentos+estoque, recorte que perde NFs recentes).
BQ_GERAL_TABLES = {
    "alinare": os.getenv("BQ_GERAL_ALINARE", "geral_alinare"),
    "novitah": os.getenv("BQ_GERAL_NOVITAH", "geral_novitah"),
}

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
