"""Testes de acesso: login e logout (US07), sessão, R10 (o observador só lê), CSRF e o
comando criar-usuario. As páginas em si (US01 a US04) estão em test_rotas.py.
"""

import re
from html import unescape
from urllib.parse import urlparse

import pytest

import db
import servicos
from app import comando_criar_usuario, create_app, main
from conftest import INICIO, SENHA_TESTE

REGEX_ALERTA = re.compile(r'<p class="mensagem mensagem-erro" role="alert">(.*?)</p>', re.S)
REGEX_ACTION = re.compile(r'<form[^>]*\baction="([^"]*)"')
REGEX_TOKEN = re.compile(r'name="csrf_token" value="([^"]+)"')


# ------------------------------------------------------------------ apoio

def html(resposta) -> str:
    return resposta.get_data(as_text=True)


def alerta(resposta) -> str | None:
    """Texto da mensagem de erro da página, ou None se não há."""
    achado = REGEX_ALERTA.search(html(resposta))
    return unescape(achado.group(1)).strip() if achado else None


def acoes_dos_formularios(resposta) -> list[str]:
    return REGEX_ACTION.findall(html(resposta))


def caminho_do_redirecionamento(resposta) -> str:
    return urlparse(resposta.headers["Location"]).path


def segundo_app(app):
    """Um app novo sobre o mesmo arquivo de banco, como depois de reiniciar."""
    chaves = ("TESTING", "DATABASE", "SECRET_KEY", "WTF_CSRF_ENABLED", "MESHTRACKER_TOKEN",
              "RELOGIO", "ATRASADO_S", "PERDIDO_S")
    return create_app({chave: app.config[chave] for chave in chaves})


def semear_operador(app, apelido="Falcao", nome="João Silva") -> int:
    with app.app_context():
        return servicos.cadastrar_operador(db.get_repo(), apelido, nome, INICIO)


def semear_operacao(app, nome="Operação Alfa", data="2026-11-10", local="Campo Norte") -> int:
    with app.app_context():
        return servicos.criar_operacao(db.get_repo(), nome, data, local)


def semear_inscricao(app, operacao_id, operador_id, time="Azul", classe="Fuzileiro",
                     dispositivo="MT-01") -> int:
    with app.app_context():
        return servicos.inscrever(db.get_repo(), operacao_id, operador_id, time, classe,
                                  dispositivo, True)


def inscrever(client, operacao_id, operador, omitir=(), **mudancas):
    """POST do formulário de inscrição; `omitir` tira campos (o checkbox desmarcado não é enviado)."""
    dados = {"operador_id": operador, "time": "Azul", "classe": "Fuzileiro",
             "dispositivo": "MT-01", "consentimento": "1", **mudancas}
    for campo in omitir:
        dados.pop(campo)
    return client.post(f"/operacoes/{operacao_id}/inscricoes", data=dados)


def inscritos_de(app, operacao_id) -> list[dict]:
    with app.app_context():
        return servicos.listar_inscritos(db.get_repo(), operacao_id)


# --------------------------------------------------------- US07: login

def test_us07_login_correto_abre_a_sessao(client, org_client):
    resposta = client.post("/login", data={"login": "org", "senha": SENHA_TESTE})
    assert resposta.status_code == 302
    assert caminho_do_redirecionamento(resposta) == "/operacoes"
    assert client.get("/operacoes").status_code == 200


@pytest.mark.parametrize("login, senha", [
    ("org", "senha-errada-123"),
    ("fantasma", SENHA_TESTE),
    ("", ""),
])
def test_us07_login_ou_senha_errados_voltam_401_com_a_mesma_mensagem(client, org_client, login, senha):
    resposta = client.post("/login", data={"login": login, "senha": senha})
    assert resposta.status_code == 401
    assert alerta(resposta) == "Login ou senha incorretos."
    assert client.get("/operacoes").status_code == 302          # continua sem sessão


def test_us07_login_errado_nao_devolve_a_senha_digitada(client, org_client):
    resposta = client.post("/login", data={"login": "org", "senha": "senha-errada-123"})
    assert "senha-errada-123" not in html(resposta)
    assert 'value="org"' in html(resposta)


def test_us07_sem_sessao_as_paginas_levam_ao_login(client):
    for caminho in ("/operadores", "/operacoes", "/operacoes/1", "/operacoes/1/mapa"):
        resposta = client.get(caminho)
        assert resposta.status_code == 302, caminho
        assert caminho_do_redirecionamento(resposta) == "/login", caminho
    assert client.get("/", follow_redirects=True).request.path == "/login"


def test_us07_depois_do_login_volta_para_a_pagina_pedida(client, org_client):
    destino = urlparse(client.get("/operadores").headers["Location"])
    assert destino.query                                       # o Flask-Login manda ?next=...
    pagina = html(client.get(f"/login?{destino.query}"))
    assert 'name="next" value="/operadores"' in pagina
    resposta = client.post("/login", data={"login": "org", "senha": SENHA_TESTE, "next": "/operadores"})
    assert caminho_do_redirecionamento(resposta) == "/operadores"


@pytest.mark.parametrize("proximo", [
    "//evil.example", "https://evil.example/x", "http://evil.example", "/\\evil.example",
    "/\t/evil.example", "evil.example", "javascript:alert(1)", "",
])
def test_us07_next_que_nao_e_caminho_relativo_e_ignorado(client, org_client, proximo):
    resposta = client.post("/login", data={"login": "org", "senha": SENHA_TESTE, "next": proximo})
    assert resposta.status_code == 302
    destino = urlparse(resposta.headers["Location"])
    assert (destino.netloc, destino.path) == ("", "/operacoes")


def test_us07_next_externo_na_url_do_login_nao_vira_campo_do_formulario(client):
    pagina = html(client.get("/login?next=//evil.example"))
    assert "evil.example" not in pagina


def test_us07_logout_e_por_post_e_encerra_a_sessao(org_client):
    assert org_client.get("/logout").status_code == 405
    assert org_client.get("/operacoes").status_code == 200
    resposta = org_client.post("/logout")
    assert resposta.status_code == 302
    assert caminho_do_redirecionamento(resposta) == "/login"
    assert org_client.get("/operacoes").status_code == 302


def test_us07_comando_criar_usuario_cria_e_o_login_funciona(app, client):
    usuario_id = comando_criar_usuario(app, "ana", "observador", "senha-da-ana-1")
    assert usuario_id
    with app.app_context():
        gravado = db.get_repo().buscar_usuario_por_login("ana")
    assert gravado["papel"] == "observador"
    assert gravado["senha_hash"] != "senha-da-ana-1"           # a senha fica em hash
    resposta = client.post("/login", data={"login": "ana", "senha": "senha-da-ana-1"})
    assert resposta.status_code == 302
    assert client.get("/operacoes").status_code == 200


def test_us07_comando_criar_usuario_recusa_login_repetido_e_papel_invalido(app):
    comando_criar_usuario(app, "ana", "organizador", "senha-da-ana-1")
    with pytest.raises(servicos.ErroDeNegocio) as repetido:
        comando_criar_usuario(app, "ana", "observador", "outra-senha-2")
    assert repetido.value.codigo == "login_duplicado"
    with pytest.raises(servicos.ErroDeNegocio) as papel:
        comando_criar_usuario(app, "bia", "administrador", "senha-da-bia-1")
    assert papel.value.codigo == "papel_invalido"


def test_us07_main_criar_usuario_pergunta_a_senha_e_cria(tmp_path, monkeypatch, capsys):
    banco = tmp_path / "terminal.db"
    monkeypatch.setenv("MESHTRACKER_DB", str(banco))
    monkeypatch.setenv("MESHTRACKER_SECRET_KEY", "chave-de-teste")
    monkeypatch.setattr("getpass.getpass", lambda _pergunta="": "senha-do-leo-1")
    assert main(["criar-usuario", "leo", "organizador"]) == 0
    assert "leo" in capsys.readouterr().out
    reiniciado = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False}).test_client()
    resposta = reiniciado.post("/login", data={"login": "leo", "senha": "senha-do-leo-1"})
    assert resposta.status_code == 302
    assert reiniciado.get("/operacoes").status_code == 200


# --------------------------------------------------------- R10: observador

def paginas_do_observador(app):
    operacao = semear_operacao(app)
    operador = semear_operador(app)
    semear_inscricao(app, operacao, operador)
    return ["/operadores", "/operacoes", f"/operacoes/{operacao}"]


def test_r10_observador_ve_as_listas(app, obs_client):
    for caminho in paginas_do_observador(app):
        assert obs_client.get(caminho).status_code == 200, caminho
    pagina = html(obs_client.get("/operacoes/1"))
    assert "Falcao" in pagina and "Abrir mapa" in pagina


def test_r10_observador_nao_ve_formularios_de_escrita(app, obs_client):
    for caminho in paginas_do_observador(app):
        assert acoes_dos_formularios(obs_client.get(caminho)) == ["/logout"], caminho


def test_r10_observador_nao_ve_botoes_de_transicao(app, obs_client):
    pagina = html(obs_client.get(paginas_do_observador(app)[2]))
    assert "Iniciar operação" not in pagina and "Encerrar operação" not in pagina


def test_r10_organizador_ve_os_formularios(app, org_client):
    for caminho in paginas_do_observador(app):
        assert len(acoes_dos_formularios(org_client.get(caminho))) > 1, caminho


def regras_de_escrita() -> list[str]:
    """Toda regra com POST fora de /api/, menos /login e /logout, com os <int:...> trocados por 1."""
    app = create_app({"TESTING": True, "DATABASE": ":memory:", "SECRET_KEY": "x"})
    regras = [r.rule for r in app.url_map.iter_rules()
              if "POST" in r.methods and not r.rule.startswith("/api/")
              and r.rule not in ("/login", "/logout")]
    return sorted({re.sub(r"<[^>]+>", "1", regra) for regra in regras})


def test_r10_a_lista_de_escritas_cobre_as_rotas_da_demo():
    esperadas = {"/operadores", "/operacoes", "/operacoes/1/avancar", "/operacoes/1/inscricoes",
                 "/inscricoes/1"}
    assert esperadas <= set(regras_de_escrita())


@pytest.mark.parametrize("caminho", regras_de_escrita())
def test_r10_observador_recebe_403_em_toda_escrita(obs_client, caminho):
    resposta = obs_client.post(caminho, data={})
    assert resposta.status_code == 403
    assert "Seu papel não permite esta ação." in html(resposta)


@pytest.mark.parametrize("caminho", regras_de_escrita())
def test_r10_sem_sessao_toda_escrita_leva_ao_login(client, caminho):
    resposta = client.post(caminho, data={})
    assert resposta.status_code == 302
    assert caminho_do_redirecionamento(resposta) == "/login"


def test_r10_o_403_do_observador_nao_muda_os_dados(app, obs_client):
    operacao = semear_operacao(app)
    operador = semear_operador(app)
    obs_client.post("/operadores", data={"apelido": "Intruso", "nome": "Nao Pode"})
    obs_client.post("/operacoes", data={"nome": "Nova", "data": "2026-11-10", "local": "X"})
    obs_client.post(f"/operacoes/{operacao}/avancar")
    inscrever(obs_client, operacao, operador)
    with app.app_context():
        repo = db.get_repo()
        assert [o["apelido"] for o in servicos.listar_operadores(repo)] == ["Falcao"]
        assert [o["situacao"] for o in servicos.listar_operacoes(repo)] == ["planejada"]
    assert inscritos_de(app, operacao) == []


# ------------------------------------------------------------------- CSRF

@pytest.fixture
def app_com_csrf(app):
    novo = segundo_app(app)
    novo.config["WTF_CSRF_ENABLED"] = True
    return novo


def token_da_pagina(cliente, caminho) -> str:
    return REGEX_TOKEN.search(html(cliente.get(caminho))).group(1)


def test_csrf_post_sem_token_e_recusado_e_com_token_passa(app_com_csrf, app):
    with app.app_context():
        servicos.criar_usuario(db.get_repo(), "org", SENHA_TESTE, "organizador")
    cliente = app_com_csrf.test_client()
    sem_token = cliente.post("/login", data={"login": "org", "senha": SENHA_TESTE})
    assert sem_token.status_code == 400
    token = token_da_pagina(cliente, "/login")
    assert cliente.post("/login", data={"login": "org", "senha": SENHA_TESTE,
                                        "csrf_token": token}).status_code == 302
    assert cliente.post("/operadores", data={"apelido": "Falcao", "nome": "João"}).status_code == 400
    token = token_da_pagina(cliente, "/operadores")
    resposta = cliente.post("/operadores", data={"apelido": "Falcao", "nome": "João", "csrf_token": token})
    assert resposta.status_code == 302


def test_csrf_todo_formulario_das_paginas_leva_o_token(app_com_csrf, app):
    operacao = semear_operacao(app)
    semear_operador(app)
    semear_inscricao(app, operacao, 1)
    with app.app_context():
        servicos.criar_usuario(db.get_repo(), "org", SENHA_TESTE, "organizador")
    cliente = app_com_csrf.test_client()
    token = token_da_pagina(cliente, "/login")
    cliente.post("/login", data={"login": "org", "senha": SENHA_TESTE, "csrf_token": token})
    for caminho in ("/operadores", "/operacoes", f"/operacoes/{operacao}"):
        pagina = html(cliente.get(caminho))
        assert pagina.count("<form") == len(REGEX_TOKEN.findall(pagina)), caminho
