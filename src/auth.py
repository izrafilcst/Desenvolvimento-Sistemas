"""Sessão com papéis (US07, R10) e token do gateway (US08, R11).

- Páginas: login_required do Flask-Login para ler; somente_organizador para
  escrever. Sem sessão, redireciona para o login; observador recebe 403.
- API: exigir_token (POST /api/v1/sinais) e sessao_ou_token (GETs).
  Sem credencial válida, 401 com {"erro": "...", "codigo": "nao_autorizado"}.
"""

import hmac
from functools import wraps

from flask import abort, current_app, jsonify, request
from flask_login import LoginManager, UserMixin, current_user

import db

login_manager = LoginManager()
login_manager.login_view = "paginas.login"
login_manager.login_message = "Entre para continuar."
login_manager.login_message_category = "aviso"


class Usuario(UserMixin):
    def __init__(self, id: int, login: str, papel: str):
        self.id = id
        self.login = login
        self.papel = papel

    @property
    def eh_organizador(self) -> bool:
        return self.papel == "organizador"

    @classmethod
    def de_dict(cls, dados: dict) -> "Usuario":
        return cls(dados["id"], dados["login"], dados["papel"])


@login_manager.user_loader
def _carregar_usuario(usuario_id: str):
    try:
        dados = db.get_repo().buscar_usuario_por_id(int(usuario_id))
    except ValueError:
        return None
    return Usuario.de_dict(dados) if dados else None


def init_app(app) -> None:
    login_manager.init_app(app)


def somente_organizador(view):
    """R10. Sem sessão: redireciona para o login. Observador: 403.
    Roda antes de qualquer acesso ao banco, então o id da URL não precisa existir."""

    @wraps(view)
    def envolvida(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.eh_organizador:
            abort(403)
        return view(*args, **kwargs)

    return envolvida


def token_valido() -> bool:
    """R11. Confere `Authorization: Bearer <token>` com MESHTRACKER_TOKEN por
    hmac.compare_digest. Sem MESHTRACKER_TOKEN configurado, nunca é válido."""
    esperado = current_app.config.get("MESHTRACKER_TOKEN")
    if not esperado:
        return False
    cabecalho = request.headers.get("Authorization", "")
    tipo, _, recebido = cabecalho.partition(" ")
    if tipo != "Bearer" or not recebido:
        return False
    return hmac.compare_digest(recebido.strip().encode("utf-8"), esperado.encode("utf-8"))


def _nao_autorizado():
    resposta = jsonify(erro="Token ausente ou inválido.", codigo="nao_autorizado")
    resposta.status_code = 401
    resposta.headers["WWW-Authenticate"] = "Bearer"
    return resposta


def exigir_token(view):
    """R11. Só passa com o token do gateway; senão 401 no formato de erro da API."""

    @wraps(view)
    def envolvida(*args, **kwargs):
        if not token_valido():
            return _nao_autorizado()
        return view(*args, **kwargs)

    return envolvida


def sessao_ou_token(view):
    """US08. GETs da API: aceita a sessão (organizador ou observador) ou o token."""

    @wraps(view)
    def envolvida(*args, **kwargs):
        if not (current_user.is_authenticated or token_valido()):
            return _nao_autorizado()
        return view(*args, **kwargs)

    return envolvida
