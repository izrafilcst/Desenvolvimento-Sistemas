"""Conexão com o SQLite e criação do banco a partir de schema.sql."""

import sqlite3
from pathlib import Path

from flask import Flask, current_app, g

from repositorio import Repositorio

ESQUEMA = Path(__file__).resolve().parent / "schema.sql"


def conectar(caminho) -> sqlite3.Connection:
    """Abre o banco com chaves estrangeiras ligadas e linhas acessíveis por nome."""
    caminho = str(caminho)
    if caminho != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(caminho, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_banco(conn: sqlite3.Connection) -> None:
    """Cria as tabelas que ainda não existem. Pode ser chamada a cada inicialização."""
    conn.executescript(ESQUEMA.read_text(encoding="utf-8"))
    conn.commit()


def get_db() -> sqlite3.Connection:
    """Conexão da requisição atual, aberta na primeira chamada e fechada no teardown."""
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE"])
    return g.db


def get_repo() -> Repositorio:
    """Repositório sobre a conexão da requisição atual."""
    return Repositorio(get_db())


def _fechar(_erro=None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app: Flask) -> None:
    """Liga o fechamento da conexão ao fim da requisição e cria o esquema."""
    app.teardown_appcontext(_fechar)
    conn = conectar(app.config["DATABASE"])
    try:
        criar_banco(conn)
    finally:
        conn.close()
