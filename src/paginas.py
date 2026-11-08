"""Páginas HTML (blueprint "paginas"). Rotas não contêm regra de negócio:
chamam servicos.py e mostram ErroDeNegocio.mensagem na própria página.

Rotas que este blueprint expõe (contrato da demo):

    GET  /                                  -> redireciona para /operacoes
    GET  /login, POST /login                -> endpoint "paginas.login"
    POST /logout
    GET  /operadores, POST /operadores                       (US01)
    GET  /operacoes,  POST /operacoes                        (US02)
    GET  /operacoes/<int:operacao_id>                        (US02 a US04)
    POST /operacoes/<int:operacao_id>/avancar                (R6)
    POST /operacoes/<int:operacao_id>/inscricoes             (US03)
    POST /inscricoes/<int:inscricao_id>                      (R4: muda time e classe)
    GET  /operacoes/<int:operacao_id>/mapa                   (US06, template de mapa-api)

GET exige login (organizador ou observador). Todo POST, menos /login e
/logout, usa auth.somente_organizador (R10).

Erro de regra (ErroDeNegocio): a mesma página volta com status 400, a mensagem
em <p class="mensagem mensagem-erro" role="alert"> e os valores digitados.
Operação ou inscrição que não existe vira 404. Sucesso: flash e redirect (PRG).
"""

import math
from urllib.parse import urlsplit

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

import auth
import db
import servicos
from servicos import ErroDeNegocio

bp = Blueprint("paginas", __name__)

ROTULO_SITUACAO = {"planejada": "Planejada", "em_curso": "Em curso", "encerrada": "Encerrada"}
NAO_ENCONTRADO = ("operacao_inexistente", "inscricao_inexistente")
MARCADO = ("1", "on", "true", "sim")
MAIOR_ID = 2**63 - 1          # o INTEGER do SQLite; ids maiores nunca existem (e estourariam o driver)


# ------------------------------------------------------------------ apoio

@bp.app_template_filter("data_br")
def data_br(iso: str) -> str:
    """2026-11-10 vira 10/11/2026; qualquer outro texto passa como veio."""
    partes = str(iso).split("-")
    return "/".join(reversed(partes)) if len(partes) == 3 else str(iso)


@bp.app_template_filter("rotulo_situacao")
def rotulo_situacao(situacao: str) -> str:
    return ROTULO_SITUACAO.get(situacao, situacao)


@bp.url_value_preprocessor
def _recusar_id_gigante(_endpoint, valores):
    if any(isinstance(v, int) and v > MAIOR_ID for v in (valores or {}).values()):
        abort(404)


def _agora():
    return current_app.config["RELOGIO"]()


def _texto(nome: str) -> str:
    return request.form.get(nome, "").strip()


def _inteiro(nome: str, rotulo: str) -> int:
    try:
        valor = int(_texto(nome))
    except ValueError:
        valor = 0
    if not 0 < valor <= MAIOR_ID:
        raise ErroDeNegocio("dados_invalidos", f"{rotulo} inválido.")
    return valor


def _coordenada(nome: str, rotulo: str) -> float | None:
    bruto = _texto(nome).replace(",", ".")
    if not bruto:
        return None
    try:
        valor = float(bruto)
    except ValueError:
        valor = math.nan
    if not math.isfinite(valor):
        raise ErroDeNegocio("dados_invalidos", f"{rotulo} inválida.")
    return valor


def _centro() -> tuple[float | None, float | None]:
    lat = _coordenada("centro_lat", "Latitude")
    lon = _coordenada("centro_lon", "Longitude")
    if (lat is None) != (lon is None):
        raise ErroDeNegocio("dados_invalidos",
                            "Informe latitude e longitude do centro, ou deixe as duas em branco.")
    return lat, lon


def _consentimento() -> bool:
    return _texto("consentimento").lower() in MARCADO


def _destino_seguro(destino: str | None) -> str | None:
    """Só caminho relativo do próprio site: começa com "/", não com "//", sem barra
    invertida nem caracteres de controle (o navegador os trataria como "//")."""
    if not destino or not destino.startswith("/") or destino.startswith("//"):
        return None
    if "\\" in destino or not destino.isprintable():
        return None
    partes = urlsplit(destino)
    return None if partes.scheme or partes.netloc else destino


# ------------------------------------------------------------ sessão (US07)

@bp.get("/")
def indice():
    return redirect(url_for("paginas.operacoes"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    proximo = _destino_seguro(request.values.get("next"))
    if request.method == "GET":
        return render_template("login.html", proximo=proximo, valores=request.form)
    usuario = servicos.autenticar(db.get_repo(), _texto("login"), request.form.get("senha", ""))
    if usuario is None:
        return render_template("login.html", proximo=proximo, valores=request.form,
                               erro="Login ou senha incorretos."), 401
    login_user(auth.Usuario.de_dict(usuario))
    return redirect(proximo or url_for("paginas.operacoes"))


@bp.post("/logout")
def logout():
    logout_user()
    flash("Você saiu.", "sucesso")
    return redirect(url_for("paginas.login"))


# ----------------------------------------------------------- operadores (US01)

def _pagina_operadores(erro: str | None = None, status: int = 200):
    operadores = servicos.listar_operadores(db.get_repo())
    return render_template("operadores.html", operadores=operadores,
                           erro=erro, valores=request.form), status


@bp.get("/operadores")
@login_required
def operadores():
    return _pagina_operadores()


@bp.post("/operadores")
@auth.somente_organizador
def operadores_criar():
    try:
        servicos.cadastrar_operador(db.get_repo(), _texto("apelido"), _texto("nome"), _agora())
    except ErroDeNegocio as erro:
        return _pagina_operadores(erro.mensagem, 400)
    flash("Operador cadastrado.", "sucesso")
    return redirect(url_for("paginas.operadores"))


# ------------------------------------------------------------ operações (US02)

def _pagina_operacoes(erro: str | None = None, status: int = 200):
    lista = servicos.listar_operacoes(db.get_repo())
    return render_template("operacoes.html", operacoes=lista, erro=erro, valores=request.form), status


@bp.get("/operacoes")
@login_required
def operacoes():
    return _pagina_operacoes()


@bp.post("/operacoes")
@auth.somente_organizador
def operacoes_criar():
    try:
        lat, lon = _centro()
        novo_id = servicos.criar_operacao(db.get_repo(), _texto("nome"), _texto("data"),
                                          _texto("local"), lat, lon)
    except ErroDeNegocio as erro:
        return _pagina_operacoes(erro.mensagem, 400)
    flash("Operação criada.", "sucesso")
    return redirect(url_for("paginas.operacao", operacao_id=novo_id))


# -------------------------------------------------- operação e inscritos (US02 a US04)

def _pagina_operacao(operacao_id: int, erro: str | None = None, status: int = 200,
                     edicao: dict | None = None):
    """`edicao` = {inscricao_id, time, classe}: devolve à linha o que o usuário tinha escolhido."""
    repo = db.get_repo()
    try:
        operacao = servicos.obter_operacao(repo, operacao_id)
        inscritos = servicos.listar_inscritos(repo, operacao_id)
    except ErroDeNegocio:
        abort(404)
    proxima = servicos.proxima_situacao(operacao["situacao"])
    return render_template(
        "operacao.html", operacao=operacao, inscritos=inscritos, proxima=proxima,
        rotulo_transicao=servicos.ROTULO_TRANSICAO.get(proxima),
        operadores=servicos.listar_operadores(repo),
        times=servicos.TIMES, classes=servicos.CLASSES,
        erro=erro, valores=request.form, edicao=edicao), status


def _falha(erro: ErroDeNegocio, operacao_id: int, edicao: dict | None = None):
    if erro.codigo in NAO_ENCONTRADO:
        abort(404)
    return _pagina_operacao(operacao_id, erro.mensagem, 400, edicao)


@bp.get("/operacoes/<int:operacao_id>")
@login_required
def operacao(operacao_id: int):
    return _pagina_operacao(operacao_id)


@bp.post("/operacoes/<int:operacao_id>/avancar")
@auth.somente_organizador
def operacao_avancar(operacao_id: int):
    try:
        nova = servicos.avancar_situacao(db.get_repo(), operacao_id)
    except ErroDeNegocio as erro:
        return _falha(erro, operacao_id)
    flash(f"Operação {ROTULO_SITUACAO.get(nova, nova).lower()}.", "sucesso")
    return redirect(url_for("paginas.operacao", operacao_id=operacao_id))


@bp.post("/operacoes/<int:operacao_id>/inscricoes")
@auth.somente_organizador
def inscricao_criar(operacao_id: int):
    try:
        servicos.inscrever(db.get_repo(), operacao_id, _inteiro("operador_id", "Operador"),
                           _texto("time"), _texto("classe"), request.form.get("dispositivo", ""),
                           _consentimento())
    except ErroDeNegocio as erro:
        return _falha(erro, operacao_id)
    flash("Operador inscrito.", "sucesso")
    return redirect(url_for("paginas.operacao", operacao_id=operacao_id))


@bp.post("/inscricoes/<int:inscricao_id>")
@auth.somente_organizador
def inscricao_alterar(inscricao_id: int):
    repo = db.get_repo()
    inscricao = repo.buscar_inscricao(inscricao_id)    # só para saber a que operação voltar
    if inscricao is None:
        abort(404)
    operacao_id = inscricao["operacao_id"]
    time, classe = _texto("time"), _texto("classe")
    try:
        servicos.alterar_inscricao(repo, inscricao_id, time, classe)
    except ErroDeNegocio as erro:
        return _falha(erro, operacao_id,
                      {"inscricao_id": inscricao_id, "time": time, "classe": classe})
    flash("Inscrição atualizada.", "sucesso")
    return redirect(url_for("paginas.operacao", operacao_id=operacao_id))


# ------------------------------------------------------------------- mapa

@bp.get("/operacoes/<int:operacao_id>/mapa")
@login_required
def mapa(operacao_id: int):
    """US06. A página só desenha o mapa; os dados vêm de GET /api/v1/situacao?operacao=<id>."""
    try:
        operacao = servicos.obter_operacao(db.get_repo(), operacao_id)
    except servicos.ErroDeNegocio:
        abort(404)
    return render_template("mapa.html", operacao=operacao)
