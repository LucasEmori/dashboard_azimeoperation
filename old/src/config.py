"""Configuracao central: caminhos, meses de referencia e codigos de MARCA."""
from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "cache"

COMPANIES = ("alinare", "novitah")
COMPANY_LABELS = {"alinare": "ALINARE", "novitah": "NOVITAH"}
COMPANY_DIRS = {c: DATA_DIR / c for c in COMPANIES}

# Codigos usados na coluna MARCA da aba Geral.
# AL = Alinare; NV = Novitah (descoberto dinamicamente, fallback aqui).
MARCA_CODES = {"alinare": {"AL"}, "novitah": {"NV", "NO", "NT"}}

# ---------------------------------------------------------------------------
# Meses de referencia (dinamico a partir de "hoje")
# ---------------------------------------------------------------------------
TODAY = date.today()


def _month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def _sub_months(d: date, n: int) -> date:
    """Subtrai n meses preservando o dia 1."""
    m = d.month - n
    y = d.year
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1)


# Mes destaque = mes anterior ao atual
DESTAQUE = _sub_months(TODAY, 1)
# Proximo mes (planejamento da Tela 3) = mes atual
PROXIMO_MES = _month_start(TODAY.year, TODAY.month)
# Comparacao: 3 meses consecutivos antes do destaque (mais recente primeiro)
COMPARACAO_MESES = [_sub_months(DESTAQUE, i) for i in range(1, 4)]

# Todos os meses relevantes para Telas 1 e 2 (destaque primeiro)
ALL_MONTHS = [DESTAQUE] + COMPARACAO_MESES


def month_label(d: date) -> str:
    """Retorna nome do mes em portugues com inicial maiuscula."""
    nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]
    return nomes[d.month - 1]


def month_short(d: date) -> str:
    return month_label(d)[:3]


def ym_key(d: date) -> tuple[int, int]:
    return (d.year, d.month)


# Dias da semana em portugues
WEEKDAYS_PT = [
    "Segunda-feira", "Terça-feira", "Quarta-feira",
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo",
]


def weekday_pt(d: date) -> str:
    # date.weekday(): seg=0 .. dom=6
    return WEEKDAYS_PT[d.weekday()]


# ---------------------------------------------------------------------------
# Localizacao dos arquivos por empresa (glob, pois nomes tem acentos/versao)
# ---------------------------------------------------------------------------
def find_file(company: str, prefix: str) -> Path | None:
    """Encontra o unico arquivo .xlsx na pasta da empresa com o prefixo."""
    pasta = COMPANY_DIRS[company]
    if not pasta.exists():
        return None
    matches = sorted(pasta.glob(f"{prefix}*.xlsx"))
    return matches[0] if matches else None


# Padroes de nome de arquivo
FILE_P1 = "1"   # Produtos lancados
FILE_P2 = "2"   # Planilha Geral
FILE_P3 = "3"   # Notas de entrada

# Abas da Planilha Geral
SHEET_GERAL = "Geral"
SHEET_LANCAMENTOS = "Lançamentos"

# Nome da aba Geral por empresa (Novitah usa "BASE GERAL")
SHEET_GERAL_BY_COMPANY = {
    "alinare": "Geral",
    "novitah": "BASE GERAL",
}

# Mapeamento de colunas canonicas: nome esperado -> lista de alias possiveis
COL_ALIASES = {
    "COD PROD": ["COD BARRAS", "CODIGO BARRAS"],
    "FORNECEDOR": ["FORNECEDOR "],
}

# Layout da aba Lancamentos (colunas 1-indexed)
# B=BU(empresa), C=Data, D=Embarque/Pedra, E=Embarque, F=MKT, G=Status, H=Transferencia
LANC_COL = {
    "bu": 2,            # empresa: 'Novitah' / 'Alinare'
    "data": 3,          # data do lancamento (join com Geral.LANÇAMENTO)
    "embarque_pedra": 4,
    "embarque": 5,
    "mkt": 6,           # texto MKT + preenchimento verde = enviado
    "status": 7,        # Programado/Finalizado/Lancado/Fila Etiquetagem/Em etiquetagem
    "transferencia": 8, # Finalizado - 100% fotos / datas
}
# Linhas de cabecalho da aba Lancamentos (a ignorar ao ler dados)
LANC_HEADER_ROWS = {4, 15}

# ---------------------------------------------------------------------------
# Cores da marca (espelham dashboard/brand-spec.md)
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
