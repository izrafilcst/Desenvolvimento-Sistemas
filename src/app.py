"""Ponto de entrada do MeshTracker Central.

    python src/app.py                               sobe o servidor em 127.0.0.1:5000
    python src/app.py --porta 5001                  sobe em outra porta
    python src/app.py criar-usuario <login> <papel> cria usuário (senha pedida por getpass)
"""

import argparse
import getpass
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFProtect

sys.path.insert(0, str(Path(__file__).resolve().parent))

import api  # noqa: E402
import auth  # noqa: E402
import config  # noqa: E402
import db  # noqa: E402
import paginas  # noqa: E402
import servicos  # noqa: E402

csrf = CSRFProtect()

POLITICA_DE_CONTEUDO = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",      # o Leaflet posiciona marcadores com estilo inline
    "img-src 'self' data: https://tile.openstreetmap.org",
    "connect-src 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
])


ERROS_HTTP = {
    400: ("requisicao_invalida", "Requisição inválida."),
    403: ("proibido", "Seu papel não permite esta ação."),
    404: ("nao_encontrado", "Página ou recurso não encontrado."),
    405: ("metodo_nao_permitido", "Método não permitido."),
    413: ("corpo_grande", "Corpo da requisição grande demais."),
    500: ("erro_interno", "Erro interno. Tente de novo."),
}


def _tratador_de_erro(status: int, codigo: str, mensagem: str):
    """Em /api/ responde {"erro", "codigo"}; nas páginas, mostra templates/erro.html."""

    def tratar(_erro):
        if request.path.startswith("/api/"):
            return jsonify(erro=mensagem, codigo=codigo), status
        return render_template("erro.html", status=status, mensagem=mensagem), status

    return tratar


def create_app(sobrescrever: dict | None = None) -> Flask:
    """Monta o app. `sobrescrever` troca chaves da configuração (os testes usam)."""
    pasta = Path(__file__).resolve().parent
    app = Flask("meshtracker", root_path=str(pasta), instance_path=str(config.PASTA_INSTANCE))
    app.config.update(config.carregar())
    if sobrescrever:
        app.config.update(sobrescrever)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = config.ler_ou_criar_chave()

    db.init_app(app)
    csrf.init_app(app)
    auth.init_app(app)
    app.register_blueprint(paginas.bp)
    app.register_blueprint(api.bp)
    csrf.exempt(api.bp)

    for status, (codigo, mensagem) in ERROS_HTTP.items():
        app.register_error_handler(status, _tratador_de_erro(status, codigo, mensagem))

    @app.after_request
    def _cabecalhos_de_seguranca(resposta):
        resposta.headers.setdefault("Content-Security-Policy", POLITICA_DE_CONTEUDO)
        resposta.headers.setdefault("X-Content-Type-Options", "nosniff")
        resposta.headers.setdefault("X-Frame-Options", "DENY")
        resposta.headers.setdefault("Referrer-Policy", "same-origin")
        return resposta

    return app


def comando_criar_usuario(app: Flask, login: str, papel: str, senha: str) -> int:
    """Cria o usuário pela regra de servicos.py e devolve o id."""
    with app.app_context():
        return servicos.criar_usuario(db.get_repo(), login, senha, papel)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "criar-usuario":
        if len(argv) != 3:
            print("Uso: python src/app.py criar-usuario <login> <organizador|observador>")
            return 2
        login, papel = argv[1], argv[2]
        senha = getpass.getpass("Senha: ")
        if senha != getpass.getpass("Repita a senha: "):
            print("As senhas não conferem.")
            return 1
        try:
            comando_criar_usuario(create_app(), login, papel, senha)
        except servicos.ErroDeNegocio as erro:
            print(erro.mensagem)
            return 1
        print(f"Usuário {login} criado com o papel {papel}.")
        return 0

    parser = argparse.ArgumentParser(description="MeshTracker Central")
    parser.add_argument("--porta", type=int, default=5000)
    args = parser.parse_args(argv)
    create_app().run(host="127.0.0.1", port=args.porta, debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
