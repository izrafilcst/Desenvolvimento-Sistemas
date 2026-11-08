"""Fixtures comuns: banco temporário por teste, relógio injetável e clientes logados.

    relogio      RelogioFalso: relogio() devolve o "agora"; relogio.avancar(s) anda s segundos
    conn, repo   SQLite temporário com o schema, para testar servicos.py direto
    app          create_app com banco temporário, CSRF desligado, TOKEN e relógio injetados
    client       cliente sem sessão
    org_client   cliente logado como organizador (login "org")
    obs_client   cliente logado como observador (login "obs")
    TOKEN        token do gateway configurado no app de teste
    cabecalho_token  {"Authorization": "Bearer <TOKEN>"}
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import db  # noqa: E402
import servicos  # noqa: E402
from app import create_app  # noqa: E402
from repositorio import Repositorio  # noqa: E402

TOKEN = "token-de-teste-0123456789"
SENHA_TESTE = "senha-de-teste-123"
INICIO = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)


class RelogioFalso:
    def __init__(self, inicio: datetime = INICIO):
        self.agora = inicio

    def __call__(self) -> datetime:
        return self.agora

    def avancar(self, segundos: float) -> datetime:
        self.agora += timedelta(seconds=segundos)
        return self.agora


@pytest.fixture
def relogio():
    return RelogioFalso()


@pytest.fixture
def conn(tmp_path):
    c = db.conectar(tmp_path / "servicos.db")
    db.criar_banco(c)
    yield c
    c.close()


@pytest.fixture
def repo(conn):
    return Repositorio(conn)


@pytest.fixture
def app(tmp_path, relogio):
    return create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "app.db"),
        "SECRET_KEY": "chave-de-teste",
        "WTF_CSRF_ENABLED": False,
        "MESHTRACKER_TOKEN": TOKEN,
        "RELOGIO": relogio,
        "ATRASADO_S": 60,
        "PERDIDO_S": 120,
    })


@pytest.fixture
def client(app):
    return app.test_client()


def _cliente_logado(app, login: str, papel: str):
    with app.app_context():
        usuario_id = servicos.criar_usuario(db.get_repo(), login, SENHA_TESTE, papel)
    cliente = app.test_client()
    with cliente.session_transaction() as sessao:
        sessao["_user_id"] = str(usuario_id)
        sessao["_fresh"] = True
    return cliente


@pytest.fixture
def org_client(app):
    return _cliente_logado(app, "org", "organizador")


@pytest.fixture
def obs_client(app):
    return _cliente_logado(app, "obs", "observador")


@pytest.fixture
def cabecalho_token():
    return {"Authorization": f"Bearer {TOKEN}"}
