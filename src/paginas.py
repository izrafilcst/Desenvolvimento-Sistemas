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
"""

from flask import Blueprint, abort, render_template
from flask_login import login_required

import db
import servicos

bp = Blueprint("paginas", __name__)


@bp.get("/operacoes/<int:operacao_id>/mapa")
@login_required
def mapa(operacao_id: int):
    """US06. A página só desenha o mapa; os dados vêm de GET /api/v1/situacao?operacao=<id>."""
    try:
        operacao = servicos.obter_operacao(db.get_repo(), operacao_id)
    except servicos.ErroDeNegocio:
        abort(404)
    return render_template("mapa.html", operacao=operacao)
