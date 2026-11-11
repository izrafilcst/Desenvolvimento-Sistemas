"""Revisão de segurança da demo de 10/11 (evidências em docs/evidencias/seguranca.md).
Achado aberto fica com xfail(strict=True, reason="S-n: ..."). Só segredos de teste aqui."""

import ast
import io
import json
import re
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
from flask import Flask, url_for
from werkzeug.security import check_password_hash

import app as modulo_app
import auth
import config
import db
import servicos
import simulador
from conftest import SENHA_TESTE, TOKEN

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
LIVRES = {"static", "paginas.login", "paginas.logout", "api.receber_sinal"}
SINAL = {"dispositivo": "MT-01", "pacote": 1, "lat": -15.79, "lon": -47.88, "bateria": 80}
BEARER = {"Authorization": f"Bearer {TOKEN}"}
CONTAGENS = ("SELECT COUNT(*) FROM posicao", "SELECT COUNT(*) FROM descarte")
FALTA = object()


# ------------------------------------------------------------------ apoio

def _rotas(app, metodo: str, fora=LIVRES) -> list[str]:
    """URLs do url_map que aceitam `metodo`, com 1 em todo parâmetro da rota."""
    with app.test_request_context():
        return [url_for(r.endpoint, **{a: 1 for a in r.arguments})
                for r in app.url_map.iter_rules()
                if metodo in r.methods and r.endpoint not in fora]


def _gravados(app) -> int:
    """Posições + descartes no banco: o que um POST /sinais poderia ter escrito."""
    with app.app_context():
        conn = db.get_db()
        return sum(conn.execute(sql).fetchone()[0] for sql in CONTAGENS)


def _criar_usuario(app, login: str, papel: str) -> None:
    with app.app_context():
        servicos.criar_usuario(db.get_repo(), login, SENHA_TESTE, papel)


def _corpo(**troca) -> str:
    corpo = {**SINAL, **troca}
    return json.dumps({k: v for k, v in corpo.items() if v is not FALTA})


def _token_csrf(resposta) -> str:
    return re.search(r'name="csrf_token" value="([^"]+)"', resposta.get_data(as_text=True)).group(1)


@pytest.fixture
def app_csrf(tmp_path, relogio):
    """Como o `app` do conftest, mas com o CSRF ligado (o padrão em produção)."""
    return modulo_app.create_app({
        "TESTING": True, "DATABASE": str(tmp_path / "csrf.db"), "SECRET_KEY": "chave-de-teste",
        "MESHTRACKER_TOKEN": TOKEN, "RELOGIO": relogio})


# ------------------------------------------------------- R10: papéis e sessão

def test_seg_url_map_so_tem_get_e_post(app):
    for regra in app.url_map.iter_rules():
        assert regra.methods <= {"GET", "HEAD", "OPTIONS", "POST"}, regra.rule
    esperadas = {"/operadores", "/operacoes", "/operacoes/1/avancar",
                 "/operacoes/1/inscricoes", "/inscricoes/1"}
    assert esperadas <= set(_rotas(app, "POST"))


def test_seg_observador_recebe_403_em_toda_escrita(app, obs_client):
    dados = {"apelido": "Intruso", "nome": "Intruso", "data": "2026-11-10", "local": "X",
             "operador_id": "1", "time": "Azul", "classe": "Médico", "dispositivo": "MT-09",
             "consentimento": "1"}
    for url in _rotas(app, "POST"):
        assert obs_client.post(url, data=dados).status_code == 403, url
    with app.app_context():
        assert servicos.listar_operadores(db.get_repo()) == []
        assert servicos.listar_operacoes(db.get_repo()) == []


def test_seg_sem_sessao_toda_pagina_vai_ao_login(app, client):
    fora = LIVRES | {"paginas.indice", "api.situacao", "api.operacoes"}
    for metodo in ("POST", "GET"):
        urls = _rotas(app, metodo, fora)
        assert urls
        for url in urls:
            resposta = client.open(url, method=metodo)
            assert resposta.status_code == 302, (metodo, url)
            assert resposta.headers["Location"].startswith("/login"), (metodo, url)


# ------------------------------------------------------------------- CSRF

def test_seg_csrf_formulario_sem_token_recusado(app_csrf):
    _criar_usuario(app_csrf, "org", "organizador")
    cliente = app_csrf.test_client()
    assert cliente.post("/login", data={"login": "org", "senha": SENHA_TESTE}).status_code == 400
    token = _token_csrf(cliente.get("/login"))
    entrar = {"login": "org", "senha": SENHA_TESTE, "csrf_token": token}
    assert cliente.post("/login", data=entrar).status_code == 302
    operador = {"apelido": "Falcão", "nome": "Marina Souza"}
    for url in ("/operadores", "/operacoes", "/logout"):
        assert cliente.post(url, data=operador).status_code == 400, url
    forjado = {**operador, "csrf_token": "forjado"}
    assert cliente.post("/operadores", data=forjado).status_code == 400
    with app_csrf.app_context():
        assert servicos.listar_operadores(db.get_repo()) == []
    token = _token_csrf(cliente.get("/operadores"))
    assert cliente.post("/operadores", data={**operador, "csrf_token": token}).status_code == 302


def test_seg_api_isenta_de_csrf_mas_exige_token(app_csrf):
    cliente = app_csrf.test_client()
    assert cliente.post("/api/v1/sinais", json=SINAL).status_code == 401
    assert cliente.post("/api/v1/sinais", json=SINAL, headers=BEARER).status_code == 202


# ---------------------------------------------------------- R11: token da API

@pytest.mark.parametrize("cabecalhos", [
    pytest.param({}, id="sem_cabecalho"),
    pytest.param({"Authorization": "Bearer errado"}, id="token_errado"),
    pytest.param({"Authorization": f"Bearer {TOKEN}x"}, id="token_com_sufixo"),
    pytest.param({"Authorization": f"Bearer {TOKEN[:-1]}"}, id="token_truncado"),
    pytest.param({"Authorization": f"Basic {TOKEN}"}, id="esquema_basic"),
    pytest.param({"Authorization": "Bearer "}, id="bearer_vazio"),
    pytest.param({"Authorization": TOKEN}, id="sem_esquema"),
    pytest.param({"X-Token": TOKEN}, id="outro_cabecalho"),
])
def test_seg_sinais_sem_token_valido_recebe_401(app, client, cabecalhos):
    resposta = client.post(f"/api/v1/sinais?token={TOKEN}", json=SINAL, headers=cabecalhos)
    assert resposta.status_code == 401
    assert resposta.get_json()["codigo"] == "nao_autorizado"
    assert _gravados(app) == 0


def test_seg_sinais_nao_aceita_sessao_no_lugar_do_token(app, org_client, obs_client):
    for cliente in (org_client, obs_client):
        assert cliente.post("/api/v1/sinais", json=SINAL).status_code == 401
    assert _gravados(app) == 0


def test_seg_sem_token_configurado_nada_passa(app, client):
    cfg = config.carregar({})                   # o código não traz token nem chave padrão
    assert cfg["MESHTRACKER_TOKEN"] is None and cfg["SECRET_KEY"] is None
    app.config["MESHTRACKER_TOKEN"] = None
    for valor in ("Bearer None", "Bearer ", f"Bearer {TOKEN}"):
        resposta = client.post("/api/v1/sinais", json=SINAL, headers={"Authorization": valor})
        assert resposta.status_code == 401, valor


def test_seg_token_comparado_com_compare_digest(client, monkeypatch):
    original, chamadas = auth.hmac.compare_digest, []

    def espiao(a, b):
        chamadas.append(b)
        return original(a, b)

    monkeypatch.setattr(auth.hmac, "compare_digest", espiao)
    assert client.post("/api/v1/sinais", json=SINAL, headers=BEARER).status_code == 202
    mesmo_tamanho = {"Authorization": "Bearer " + "x" * len(TOKEN)}
    assert client.post("/api/v1/sinais", json=SINAL, headers=mesmo_tamanho).status_code == 401
    assert chamadas.count(TOKEN.encode()) == 2


def test_seg_gets_da_api_exigem_sessao_ou_token(client, obs_client):
    for url in ("/api/v1/situacao", "/api/v1/operacoes"):
        assert client.get(url).status_code == 401, url
        assert client.get(url, headers={"Authorization": "Bearer errado"}).status_code == 401
        assert client.get(f"{url}?token={TOKEN}").status_code == 401, url
        assert client.get(url, headers=BEARER).status_code in (200, 404), url
        assert obs_client.get(url).status_code in (200, 404), url


# ------------------------------------------------- senha, cookie e debug

def test_seg_senha_guardada_como_hash_com_sal(app):
    _criar_usuario(app, "ana", "observador")
    _criar_usuario(app, "leo", "observador")
    with app.app_context():
        repo = db.get_repo()
        hashes = [repo.buscar_usuario_por_login(login)["senha_hash"] for login in ("ana", "leo")]
    for guardado in hashes:
        assert SENHA_TESTE not in guardado
        assert guardado.startswith(("scrypt:", "pbkdf2:"))
        assert check_password_hash(guardado, SENHA_TESTE)
    assert hashes[0] != hashes[1]


def test_seg_cookie_de_sessao_httponly_e_samesite_lax(app, client):
    _criar_usuario(app, "org", "organizador")
    resposta = client.post("/login", data={"login": "org", "senha": SENHA_TESTE})
    assert resposta.status_code == 302
    cookies = resposta.headers.getlist("Set-Cookie")
    sessao = [c for c in cookies if c.startswith(app.config["SESSION_COOKIE_NAME"] + "=")]
    assert len(sessao) == 1 and "HttpOnly" in sessao[0] and "SameSite=Lax" in sessao[0]
    assert not any(c.startswith("remember_token=") for c in cookies)


def test_seg_debug_desligado_em_python_src_app(monkeypatch, tmp_path):
    chamadas = []
    monkeypatch.setenv("MESHTRACKER_DB", str(tmp_path / "debug.db"))
    monkeypatch.setenv("MESHTRACKER_SECRET_KEY", "chave-de-teste")
    monkeypatch.setattr(Flask, "run", lambda self, **kw: chamadas.append(kw))
    assert modulo_app.main([]) == 0
    assert chamadas == [{"host": "127.0.0.1", "port": 5000, "debug": False}]


# ------------------------------------------------------------------- SQL

INJECOES = ["' OR 1=1 --", "Robert'); DROP TABLE operador;--"]


def test_seg_sql_injecao_no_apelido_gravada_literalmente(app, org_client):
    for apelido in INJECOES:
        resposta = org_client.post("/operadores", data={"apelido": apelido, "nome": apelido})
        assert resposta.status_code == 302, apelido
    with app.app_context():
        apelidos = sorted(o["apelido"] for o in servicos.listar_operadores(db.get_repo()))
    assert apelidos == sorted(INJECOES)
    assert "&#39; OR 1=1 --" in org_client.get("/operadores").get_data(as_text=True)


def test_seg_sql_injecao_no_login_nao_entra(app, client):
    _criar_usuario(app, "org", "organizador")
    for login in ("' OR 1=1 --", "org' --", "org'/*", "\" OR \"\"=\""):
        resposta = client.post("/login", data={"login": login, "senha": "' OR '1'='1"})
        assert resposta.status_code == 401, login


def _texto_montado(no) -> bool:
    """f-string, .format() ou texto somado/formatado com algo que não é constante."""
    if isinstance(no, ast.JoinedStr):
        return True
    if isinstance(no, ast.Call) and getattr(no.func, "attr", "") == "format":
        return True
    if isinstance(no, ast.BinOp) and isinstance(no.op, (ast.Add, ast.Mod)):
        lados = (no.left, no.right)
        tem_texto = any(isinstance(l, ast.Constant) and isinstance(l.value, str) for l in lados)
        constante = all(isinstance(l, (ast.Constant, ast.BinOp))
                        or (isinstance(l, ast.Name) and l.id.isupper()) for l in lados)
        return tem_texto and not constante
    return False


def test_seg_sql_so_com_parametros_no_codigo():
    for arquivo in ("repositorio.py", "db.py"):
        arvore = ast.parse((SRC / arquivo).read_text(encoding="utf-8"))
        montados = [no.lineno for no in ast.walk(arvore) if _texto_montado(no)]
        assert montados == [], f"{arquivo}: texto montado nas linhas {montados}"


# ------------------------------------------------------------------- XSS

XSS_APELIDO = "<script>alert(1)</script>"
XSS_NOME = '"><img src=x onerror=alert(1)>'


def test_seg_xss_apelido_e_nome_escapados_nas_paginas(app, org_client):
    dados = {"apelido": XSS_APELIDO, "nome": XSS_NOME}
    assert org_client.post("/operadores", data=dados).status_code == 302
    with app.app_context():
        repo = db.get_repo()
        operador_id = servicos.listar_operadores(repo)[0]["id"]
        op = servicos.criar_operacao(repo, XSS_APELIDO, "2026-11-10", XSS_NOME)
        servicos.inscrever(repo, op, operador_id, "Azul", "Médico", "MT-01", True)
    for url in ("/operadores", "/operacoes", f"/operacoes/{op}", f"/operacoes/{op}/mapa"):
        html = org_client.get(url).get_data(as_text=True)
        assert XSS_APELIDO not in html and "<img src=x" not in html, url
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html, url


def test_seg_xss_refletido_no_login_escapado(client):
    html = client.post("/login", data={"login": XSS_NOME, "senha": "x"}).get_data(as_text=True)
    assert "<img src=x" not in html
    html = client.get("/login", query_string={"next": "/" + XSS_NOME}).get_data(as_text=True)
    assert "<img src=x" not in html


def test_seg_templates_com_autoescape_sem_safe_nem_script_inline(app):
    assert app.select_jinja_autoescape("operadores.html")
    for arquivo in (SRC / "templates").glob("*.html"):
        texto = arquivo.read_text(encoding="utf-8")
        assert "|safe" not in texto.replace(" ", ""), arquivo.name
        assert "autoescape false" not in texto and "Markup" not in texto, arquivo.name
        assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", texto), arquivo.name
        assert not re.search(r"\son[a-z]+\s*=", texto), arquivo.name


def test_seg_mapa_js_so_usa_textcontent():
    js = (SRC / "static" / "js" / "mapa.js").read_text(encoding="utf-8")
    codigo = re.sub(r"/\*.*?\*/|//[^\n]*", "", js, flags=re.S)
    for proibido in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write",
                     "eval(", "new Function", "bindPopup", "bindTooltip"):
        assert proibido not in codigo, proibido
    assert "textContent" in codigo
    for valor in re.findall(r"\bhtml:\s*([^,}\n]+)", codigo):
        assert re.fullmatch(r"[A-Za-z_][\w.]*", valor.strip()), valor   # elemento DOM, nunca texto


# ------------------------------------------------- limites de entrada da API

CORPOS_INVALIDOS = {
    "nao_json": "isto nao e json", "lista": "[1, 2]", "sem_lat": _corpo(lat=FALTA),
    "lat_texto": _corpo(lat="1"), "lat_fora": _corpo(lat=90.5), "lon_fora": _corpo(lon=-180.5),
    "lat_nan": _corpo(lat=float("nan")), "lon_infinito": _corpo(lon=float("inf")),
    "bateria_acima": _corpo(bateria=100.5), "bateria_negativa": _corpo(bateria=-0.1),
    "pacote_negativo": _corpo(pacote=-1), "pacote_acima_do_sqlite": _corpo(pacote=2**63),
    "pacote_decimal": _corpo(pacote=1.5), "pacote_bool": _corpo(pacote=True),
    "pacote_5000_digitos": _corpo(pacote=0).replace('"pacote": 0', '"pacote": ' + "9" * 5000),
    "dispositivo_vazio": _corpo(dispositivo="   "), "dispositivo_33": _corpo(dispositivo="M" * 33),
    "dispositivo_numero": _corpo(dispositivo=123),
}


@pytest.mark.parametrize("nome", sorted(CORPOS_INVALIDOS))
def test_seg_limites_da_api_recebem_400(app, client, nome):
    resposta = client.post("/api/v1/sinais", data=CORPOS_INVALIDOS[nome],
                           content_type="application/json", headers=BEARER)
    assert resposta.status_code == 400
    assert resposta.get_json()["codigo"] == "formato_invalido"
    assert _gravados(app) == 0


def test_seg_parametros_e_ids_gigantes_nao_viram_500(client, org_client):
    for valor, status in (("abc", 400), ("1e3", 400), ("-1", 404), ("9" * 30, 404)):
        resposta = client.get(f"/api/v1/situacao?operacao={valor}", headers=BEARER)
        assert resposta.status_code == status, valor
    assert org_client.get("/operacoes/" + "9" * 30).status_code == 404


def test_seg_json_muito_aninhado_recebe_400(app, client):
    """S-2, corrigido em 65ed6c1."""
    app.config["MAX_CONTENT_LENGTH"] = None      # isola do S-1: aqui só importa o aninhamento
    resposta = client.post("/api/v1/sinais", data="[" * 100_000,
                           content_type="application/json", headers=BEARER)
    assert resposta.status_code == 400


def test_seg_corpo_enorme_na_api_recebe_413(client):
    """S-1, corrigido em 45b0305."""
    corpo = json.dumps({**SINAL, "enchimento": "A" * (2 * 1024 * 1024)})
    resposta = client.post("/api/v1/sinais", data=corpo, content_type="application/json",
                           headers=BEARER)
    assert resposta.status_code == 413
    assert resposta.get_json()["codigo"]          # 413 no formato de erro da API


def test_seg_corpo_enorme_no_login_recebe_413(client):
    """S-1, corrigido em 45b0305: barra antes do CSRF ler o formulário, sem sessão."""
    arquivo = (io.BytesIO(b"A" * (2 * 1024 * 1024)), "enchimento.bin")
    resposta = client.post("/login", data={"login": "x", "senha": "y", "f": arquivo},
                           content_type="multipart/form-data")
    assert resposta.status_code == 413


# ------------------------------------------------------ cabeçalhos HTTP

def test_seg_cabecalhos_de_seguranca(client):
    for url in ("/login", "/api/v1/operacoes", "/nao-existe"):
        resposta = client.get(url)
        csp = resposta.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp and "frame-ancestors 'none'" in csp, url
        script_src = csp.split("script-src")[1].split(";")[0]
        assert "'self'" in script_src and "unsafe" not in script_src, url
        assert resposta.headers["X-Frame-Options"] == "DENY", url
        assert resposta.headers["X-Content-Type-Options"] == "nosniff", url
        assert resposta.headers["Referrer-Policy"] == "same-origin", url
    assert client.get("/api/v1/operacoes").content_type == "application/json"


# -------------------------------------------- login: open redirect e enumeração

FORA_DO_SITE = ["//evil.example", "https://evil.example", "/\\evil.example", "\\\\evil.example",
                "/\t/evil.example", "http:/evil.example", "javascript:alert(1)",
                "///evil.example", " //evil.example"]


@pytest.mark.parametrize("destino, esperado", [(d, "/operacoes") for d in FORA_DO_SITE]
                         + [("/operacoes/1/mapa", "/operacoes/1/mapa")])
def test_seg_login_next_so_aceita_caminho_do_site(app, client, destino, esperado):
    _criar_usuario(app, "org", "organizador")
    pagina = client.get("/login", query_string={"next": destino}).get_data(as_text=True)
    assert "evil.example" not in pagina and "javascript:" not in pagina
    resposta = client.post("/login", data={"login": "org", "senha": SENHA_TESTE, "next": destino})
    assert resposta.status_code == 302
    assert resposta.headers["Location"] == esperado


def test_seg_login_mesma_resposta_para_login_inexistente(app, client):
    _criar_usuario(app, "org", "organizador")

    def corpo(login):
        resposta = client.post("/login", data={"login": login, "senha": "senha-errada-1"})
        html = re.sub(r'name="csrf_token" value="[^"]*"', "", resposta.get_data(as_text=True))
        return resposta.status_code, html.replace(f'value="{login}"', "")

    assert corpo("org") == corpo("zzz")
    assert corpo("org")[0] == 401


def test_seg_login_inexistente_tambem_confere_hash(repo, monkeypatch):
    """S-3, corrigido em ae6ce0a: o tempo não revela quais logins existem."""
    chamadas = []
    monkeypatch.setattr(servicos, "check_password_hash", lambda h, s: chamadas.append(h) or False)
    assert servicos.autenticar(repo, "ninguem", "senha-errada-1") is None
    assert len(chamadas) == 1


# ------------------------------------------- simulador, logs e segredos no git

def test_seg_simulador_nao_imprime_token_nem_posicao(monkeypatch, capsys):
    segredo, enviados = "segredo-do-simulador-0123456789", []

    def chamar_falso(metodo, url, token, corpo=None, timeout=5.0):
        assert token == segredo
        if metodo == "GET":
            return 200, {"operacao": {"centro_lat": -15.799, "centro_lon": -47.907}}
        enviados.append(corpo)
        return 201, {"status": "gravado"}

    monkeypatch.delenv("MESHTRACKER_TOKEN", raising=False)
    monkeypatch.setattr(simulador, "chamar", chamar_falso)
    argv = ["--token", segredo, "--ticks", "2", "--intervalo", "0.01", "--dispositivos", "MT-01",
            "--semente", "1"]
    assert simulador.main(argv) == 0
    saida = capsys.readouterr()
    assert segredo not in saida.out + saida.err
    linhas = [l for l in saida.out.splitlines() if not l.startswith("Centro em")]
    assert enviados and linhas
    for sinal in enviados:
        assert not any(str(sinal["lat"]) in l or str(sinal["lon"]) in l for l in linhas)
    monkeypatch.setattr(simulador, "chamar", lambda *a, **k: (401, {"erro": "Token inválido."}))
    assert simulador.main(["--token", segredo]) == 1
    saida = capsys.readouterr()
    assert segredo not in saida.out + saida.err


def test_seg_simulador_nao_reenvia_token_em_redirecionamento():
    recebidos = []

    class Servidor(BaseHTTPRequestHandler):
        def do_GET(self):
            destino = getattr(self.server, "destino", None)
            self.send_response(302 if destino else 200)
            if destino:
                self.send_header("Location", destino)
            else:
                recebidos.append(self.headers.get("Authorization"))
            self.end_headers()

        def log_message(self, *args):
            pass

    outro, origem = (HTTPServer(("127.0.0.1", 0), Servidor) for _ in range(2))
    origem.destino = f"http://127.0.0.1:{outro.server_port}/roubo"     # outra origem
    for servidor in (outro, origem):
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
    try:
        simulador.chamar("GET", f"http://127.0.0.1:{origem.server_port}/api/v1/situacao",
                         "tok-de-teste")
    finally:
        for servidor in (outro, origem):
            servidor.shutdown()
            servidor.server_close()
    assert recebidos == []


def test_seg_modulos_do_servidor_nao_registram_dados_em_log():
    for arquivo in ("api.py", "auth.py", "paginas.py", "servicos.py", "repositorio.py", "db.py"):
        texto = (SRC / arquivo).read_text(encoding="utf-8")
        assert "import logging" not in texto and ".logger." not in texto, arquivo
        assert not re.search(r"\bprint\(", texto), arquivo


def test_seg_nenhum_arquivo_sensivel_versionado():
    assert "instance/" in (RAIZ / ".gitignore").read_text(encoding="utf-8").split()
    if shutil.which("git") is None:
        pytest.skip("git ausente")
    saida = subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True)
    if saida.returncode != 0:
        pytest.skip("fora de um repositório git")
    sensivel = re.compile(r"(^|/)(instance/|\.env$|\.secret_key$)|\.(db|sqlite3?|pem|key)$")
    assert [f for f in saida.stdout.splitlines() if sensivel.search(f)] == []
