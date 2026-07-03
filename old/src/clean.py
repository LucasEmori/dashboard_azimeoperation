"""Normalizacao de chaves, status e classificacao por empresa."""
from __future__ import annotations

import re

import pandas as pd


def normalize_nf(val) -> int | None:
    """Extrai o numero inteiro de uma chave de NF (ex.: 'NF922'->922, '000000949'->949)."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        try:
            return int(val)
        except (ValueError, OverflowError):
            return None
    digits = re.sub(r"\D", "", str(val))
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def company_from_marca(marca: str, marca_map: dict) -> str | None:
    """Classifica uma linha da aba Geral em 'alinare'/'novitah' pelo codigo MARCA."""
    if not isinstance(marca, str):
        return None
    code = marca.strip().upper()
    if code in marca_map.get("alinare", set()):
        return "alinare"
    if code in marca_map.get("novitah", set()):
        return "novitah"
    return None


# Palavras que indicam "Pronto" no status (Tela 3)
STATUS_PRONTO_KEYWORDS = (
    "programado", "finalizado", "lançado", "lancado", "finalizad",
)
# Palavras que indicam processo/pendente (explicitamente)
STATUS_PROCESSO_KEYWORDS = (
    "pendente", "processo", "conferên", "conferen", "etiquetagem",
    "fila", "plantão", "plantao",
)


def classify_status(*values) -> str:
    """Classifica o status de um item de programacao em 'ready' ou 'process'.

    Procura em todos os valores passados (colunas de status da aba Lancamentos).
    Se algum contem palavra de "pronto" -> 'ready'; caso contrario 'process'.
    """
    combined = " ".join(str(v).lower() for v in values if v is not None and str(v).strip())
    if not combined.strip():
        return "process"
    for kw in STATUS_PRONTO_KEYWORDS:
        if kw in combined:
            return "ready"
    return "process"


def mkt_status(mkt_verde: bool, mkt_valor) -> str:
    """Retorna 'sent' se verde/enviado ao MKT, senao 'pending'."""
    if mkt_verde:
        return "sent"
    if mkt_valor is not None and str(mkt_valor).strip() != "":
        # valor preenchido mas nao verde -> ainda assim considerar?
        # Por definicao do usuario, so conta como enviado se VERDE.
        return "pending"
    return "pending"


def fmt_signed_days(days: float) -> str:
    """Formata media de dias com indicador de adiantado/atrasado."""
    if days is None or pd.isna(days):
        return "—"
    if days < 0:
        return f"{abs(days):.1f} dias (adiantado)"
    if days > 0:
        return f"{days:.1f} dias (atrasado)"
    return "0 dias (no prazo)"
