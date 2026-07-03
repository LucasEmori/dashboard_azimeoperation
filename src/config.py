"""Configuracao central: caminhos, meses dinamicos, constantes."""
from __future__ import annotations

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


DESTAQUE = sub_months(TODAY, 1)
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
