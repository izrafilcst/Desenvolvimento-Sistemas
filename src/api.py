"""API /api/v1 (ADR-003, US05 e US08). Isenta de CSRF; autentica por token ou sessão.

Contrato (documentado em docs/api.md):

    POST /api/v1/sinais       auth.exigir_token  (R11)
        corpo {dispositivo, pacote, lat, lon, bateria}
        401 sem token ou token errado; 400 formato inválido;
        202 {"status":"descartado"} (R7); 200 {"status":"duplicado"} (R8);
        201 {"status":"gravado"}
    GET  /api/v1/situacao[?operacao=<id>]   auth.sessao_ou_token
        sem parâmetro: a operação em curso (404 sem_operacao_em_curso se não há);
        com parâmetro: a operação pedida (404 operacao_inexistente)
    GET  /api/v1/operacoes                  auth.sessao_ou_token

Erros sempre como {"erro": "...", "codigo": "..."}.
"""

import math

from flask import Blueprint, current_app, jsonify, request

import auth
import db
import servicos

bp = Blueprint("api", __name__, url_prefix="/api/v1")

STATUS_DO_SINAL = {"gravado": 201, "duplicado": 200, "descartado": 202}
MAIOR_INTEIRO = 2**63 - 1           # limite do INTEGER do SQLite
TAMANHO_MAXIMO_DISPOSITIVO = 32


class FormatoInvalido(ValueError):
    """Corpo ou parâmetro fora do contrato. A mensagem diz qual campo."""


def _erro(mensagem: str, codigo: str, status: int):
    return jsonify(erro=mensagem, codigo=codigo), status


# ------------------------------------------------------------ validação (400)

def _numero(corpo: dict, campo: str, minimo: float, maximo: float) -> float:
    """Número JSON (bool não conta), finito e dentro de [minimo, maximo]."""
    valor = corpo[campo]
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise FormatoInvalido(f"Campo '{campo}' precisa ser um número.")
    try:
        numero = float(valor)           # inteiro enorme estoura aqui, e não em isfinite
    except OverflowError:
        numero = math.inf
    if not math.isfinite(numero):
        raise FormatoInvalido(f"Campo '{campo}' precisa ser um número finito.")
    if not minimo <= numero <= maximo:
        raise FormatoInvalido(f"Campo '{campo}' precisa estar entre {minimo:g} e {maximo:g}.")
    return numero


def _pacote(corpo: dict) -> int:
    valor = corpo["pacote"]
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise FormatoInvalido("Campo 'pacote' precisa ser um número inteiro.")
    if not 0 <= valor <= MAIOR_INTEIRO:
        raise FormatoInvalido("Campo 'pacote' precisa ser um inteiro maior ou igual a zero.")
    return valor


def _dispositivo(corpo: dict) -> str:
    valor = corpo["dispositivo"]
    if not isinstance(valor, str):
        raise FormatoInvalido("Campo 'dispositivo' precisa ser um texto.")
    if not 1 <= len(valor.strip()) <= TAMANHO_MAXIMO_DISPOSITIVO:
        raise FormatoInvalido(
            f"Campo 'dispositivo' precisa ter de 1 a {TAMANHO_MAXIMO_DISPOSITIVO} caracteres.")
    return valor


def validar_sinal(corpo) -> dict:
    """Confere o corpo de POST /sinais e devolve os campos já convertidos.
    Levanta FormatoInvalido (mensagem com o nome do campo) se algo foge do contrato."""
    if not isinstance(corpo, dict):
        raise FormatoInvalido("O corpo precisa ser um objeto JSON.")
    for campo in ("dispositivo", "pacote", "lat", "lon", "bateria"):
        if campo not in corpo:
            raise FormatoInvalido(f"Campo '{campo}' ausente.")
    return {
        "dispositivo": _dispositivo(corpo),
        "pacote": _pacote(corpo),
        "lat": _numero(corpo, "lat", -90, 90),
        "lon": _numero(corpo, "lon", -180, 180),
        "bateria": _numero(corpo, "bateria", 0, 100),
    }


def _id_da_operacao(bruto: str) -> int:
    try:
        return int(bruto)
    except ValueError:
        raise FormatoInvalido("Parâmetro 'operacao' precisa ser um número inteiro.") from None


# --------------------------------------------------------------------- rotas

@bp.post("/sinais")
@auth.exigir_token
def receber_sinal():
    """US05, R7, R8, R11. O formato é conferido aqui; as regras ficam em servicos.py."""
    try:
        sinal = validar_sinal(request.get_json(silent=True))
    except FormatoInvalido as erro:
        return _erro(str(erro), "formato_invalido", 400)
    agora = current_app.config["RELOGIO"]()
    resultado = servicos.receber_sinal(
        db.get_repo(), sinal["dispositivo"], sinal["pacote"],
        sinal["lat"], sinal["lon"], sinal["bateria"], agora)
    return jsonify(status=resultado), STATUS_DO_SINAL[resultado]


def _situacao_pedida(repo, bruto: str | None, agora, atrasado_s: int, perdido_s: int):
    """A situação pedida ou a da operação em curso. Levanta FormatoInvalido ou ErroDeNegocio."""
    if bruto is None:
        situacao = servicos.situacao_em_curso(repo, agora, atrasado_s, perdido_s)
        if situacao is None:
            raise servicos.ErroDeNegocio("sem_operacao_em_curso", "Não há operação em curso.")
        return situacao
    operacao_id = _id_da_operacao(bruto)
    if not 0 <= operacao_id <= MAIOR_INTEIRO:
        raise servicos.ErroDeNegocio("operacao_inexistente", "Operação inexistente.")
    return servicos.situacao_da_operacao(repo, operacao_id, agora, atrasado_s, perdido_s)


@bp.get("/situacao")
@auth.sessao_ou_token
def situacao():
    """US06. A situação ao vivo de uma operação (R9 aplicada em servicos.py)."""
    config = current_app.config
    try:
        dados = _situacao_pedida(db.get_repo(), request.args.get("operacao"),
                                 config["RELOGIO"](), config["ATRASADO_S"], config["PERDIDO_S"])
    except FormatoInvalido as erro:
        return _erro(str(erro), "formato_invalido", 400)
    except servicos.ErroDeNegocio as erro:
        return _erro(erro.mensagem, erro.codigo, 404)
    return jsonify(dados)


@bp.get("/operacoes")
@auth.sessao_ou_token
def operacoes():
    """US02. Todas as operações, para o gateway e as páginas saberem o que existe."""
    return jsonify(operacoes=servicos.listar_operacoes(db.get_repo()))
