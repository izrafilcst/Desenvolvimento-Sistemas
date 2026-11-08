"""Configuração lida das variáveis de ambiente.

Nenhuma senha, token ou chave fica no código. Sem MESHTRACKER_TOKEN,
POST /api/v1/sinais sempre responde 401 (R11).
"""

import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA_INSTANCE = RAIZ / "instance"


def agora_utc() -> datetime:
    """Relógio padrão: agora em UTC, com fuso. Os testes injetam outro (R9)."""
    return datetime.now(timezone.utc)


def _inteiro_positivo(ambiente, nome: str, padrao: int) -> int:
    bruto = ambiente.get(nome)
    if bruto is None or bruto == "":
        return padrao
    try:
        valor = int(bruto)
    except ValueError:
        raise ValueError(f"{nome} precisa ser um número inteiro de segundos, recebi {bruto!r}") from None
    if valor <= 0:
        raise ValueError(f"{nome} precisa ser maior que zero, recebi {valor}")
    return valor


def carregar(ambiente=None) -> dict:
    """Monta o dicionário de configuração do Flask a partir do ambiente.

    SECRET_KEY fica None quando MESHTRACKER_SECRET_KEY não está definida;
    create_app() então lê ou cria instance/.secret_key.
    """
    ambiente = os.environ if ambiente is None else ambiente
    atrasado = _inteiro_positivo(ambiente, "MESHTRACKER_ATRASADO_S", 60)
    perdido = _inteiro_positivo(ambiente, "MESHTRACKER_PERDIDO_S", 120)
    if perdido <= atrasado:
        raise ValueError("MESHTRACKER_PERDIDO_S precisa ser maior que MESHTRACKER_ATRASADO_S")
    return {
        "DATABASE": ambiente.get("MESHTRACKER_DB") or str(PASTA_INSTANCE / "meshtracker.db"),
        "SECRET_KEY": ambiente.get("MESHTRACKER_SECRET_KEY") or None,
        "MESHTRACKER_TOKEN": ambiente.get("MESHTRACKER_TOKEN") or None,
        "ATRASADO_S": atrasado,
        "PERDIDO_S": perdido,
        "RELOGIO": agora_utc,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
    }


def ler_ou_criar_chave(caminho: Path = PASTA_INSTANCE / ".secret_key") -> str:
    """Lê a chave de sessão de instance/.secret_key ou cria uma na primeira execução."""
    caminho = Path(caminho)
    if caminho.exists():
        chave = caminho.read_text(encoding="utf-8").strip()
        if chave:
            return chave
    caminho.parent.mkdir(parents=True, exist_ok=True)
    chave = secrets.token_hex(32)
    caminho.write_text(chave, encoding="utf-8")
    return chave
