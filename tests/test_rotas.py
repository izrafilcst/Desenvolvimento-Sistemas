"""Testes das páginas do organizador (US01 a US04), pelo cliente HTTP do Flask.

As regras R1 a R6 são de servicos.py; aqui se confere o que a página mostra:
a recusa vira mensagem na própria página (status 400, nunca 500), os valores
digitados voltam no formulário e o sucesso redireciona (PRG). Login, sessão,
R10, CSRF e criar-usuario estão em test_rotas_acesso.py.
"""

import re
from html import unescape
from urllib.parse import urlparse

import pytest

import db
import servicos
from app import create_app
from conftest import INICIO, SENHA_TESTE

REGEX_ALERTA = re.compile(r'<p class="mensagem mensagem-erro" role="alert">(.*?)</p>', re.S)


# ------------------------------------------------------------------ apoio

def html(resposta) -> str:
    return resposta.get_data(as_text=True)


def alerta(resposta) -> str | None:
    """Texto da mensagem de erro da página, ou None se não há."""
    achado = REGEX_ALERTA.search(html(resposta))
    return unescape(achado.group(1)).strip() if achado else None


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


# ------------------------------------------------------ US01: operadores

def test_us01_cadastra_operador_e_mostra_na_lista(org_client):
    resposta = org_client.post("/operadores", data={"apelido": "Falcao", "nome": "João Silva"})
    assert resposta.status_code == 302
    assert caminho_do_redirecionamento(resposta) == "/operadores"
    pagina = html(org_client.get("/operadores"))
    assert "Falcao" in pagina and "João Silva" in pagina


def test_us01_apelido_repetido_aparece_como_mensagem_na_pagina(org_client):
    org_client.post("/operadores", data={"apelido": "Falcao", "nome": "João Silva"})
    resposta = org_client.post("/operadores", data={"apelido": "falcao", "nome": "Outro Nome"})
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert "<h1>Operadores</h1>" in html(resposta)
    assert 'value="Outro Nome"' in html(resposta)           # o que foi digitado continua no formulário
    with org_client.application.app_context():
        assert len(servicos.listar_operadores(db.get_repo())) == 1


@pytest.mark.parametrize("dados", [
    {"apelido": "", "nome": "João"},
    {"apelido": "Falcao", "nome": ""},
    {"apelido": "x" * 33, "nome": "João"},
    {"nome": "João"},
])
def test_us01_dados_invalidos_voltam_400_sem_erro_500(org_client, dados):
    resposta = org_client.post("/operadores", data=dados)
    assert resposta.status_code == 400
    assert alerta(resposta)


def test_us01_texto_do_usuario_e_escapado(org_client):
    org_client.post("/operadores", data={"apelido": "<b>x</b>", "nome": "<i>y</i>"})
    pagina = html(org_client.get("/operadores"))
    assert "&lt;b&gt;x&lt;/b&gt;" in pagina and "&lt;i&gt;y&lt;/i&gt;" in pagina
    assert "<b>x</b>" not in pagina and "<i>y</i>" not in pagina


def test_us01_operador_continua_la_depois_de_reiniciar(app, org_client):
    org_client.post("/operadores", data={"apelido": "Falcao", "nome": "João Silva"})
    novo = segundo_app(app).test_client()
    novo.post("/login", data={"login": "org", "senha": SENHA_TESTE})
    assert "Falcao" in html(novo.get("/operadores"))


# ------------------------------------------------------- US02: operações

def test_us02_cria_operacao_planejada_e_abre_a_pagina_dela(org_client):
    resposta = org_client.post("/operacoes", data={
        "nome": "Operação Alfa", "data": "2026-11-10", "local": "Campo Norte"})
    assert resposta.status_code == 302
    pagina = html(org_client.get(resposta.headers["Location"]))
    assert "Operação Alfa" in pagina and "10/11/2026" in pagina and "Campo Norte" in pagina
    assert "Planejada" in pagina


def test_us02_lista_mostra_situacao_e_numero_de_inscritos(app, org_client):
    operacao = semear_operacao(app)
    semear_inscricao(app, operacao, semear_operador(app))
    pagina = html(org_client.get("/operacoes"))
    linha = re.search(r"<tr>(?:(?!</tr>).)*Operação Alfa.*?</tr>", pagina, re.S).group(0)
    assert "Planejada" in linha and "<td>1</td>" in linha
    assert f'href="/operacoes/{operacao}"' in linha


def test_us02_centro_opcional_aceita_virgula_decimal(app, org_client):
    resposta = org_client.post("/operacoes", data={
        "nome": "Com centro", "data": "2026-11-10", "local": "Campo Sul",
        "centro_lat": "-23,55", "centro_lon": "-46.63"})
    assert resposta.status_code == 302
    with app.app_context():
        operacao = servicos.listar_operacoes(db.get_repo())[0]
    assert (operacao["centro_lat"], operacao["centro_lon"]) == (-23.55, -46.63)


@pytest.mark.parametrize("mudanca", [
    {"nome": ""},
    {"local": ""},
    {"data": "2026-02-30"},
    {"data": "ontem"},
    {"centro_lat": "abc", "centro_lon": "-46"},
    {"centro_lat": "nan", "centro_lon": "-46"},
    {"centro_lat": "-23.5"},                                  # só a latitude
    {"centro_lat": "91", "centro_lon": "-46"},
    {"centro_lat": "-23", "centro_lon": "181"},
])
def test_us02_dados_invalidos_voltam_400_e_preservam_o_formulario(org_client, mudanca):
    dados = {"nome": "Operação Beta", "data": "2026-11-10", "local": "Campo Leste", **mudanca}
    resposta = org_client.post("/operacoes", data=dados)
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert "<h1>Operações</h1>" in html(resposta)
    for valor in dados.values():
        assert not valor or f'value="{valor}"' in html(resposta)


def test_r6_so_o_botao_da_transicao_valida(app, org_client):
    operacao = semear_operacao(app)
    url = f"/operacoes/{operacao}"
    pagina = html(org_client.get(url))
    assert "Iniciar operação" in pagina and "Encerrar operação" not in pagina
    org_client.post(f"{url}/avancar")
    pagina = html(org_client.get(url))
    assert "Encerrar operação" in pagina and "Iniciar operação" not in pagina
    org_client.post(f"{url}/avancar")
    pagina = html(org_client.get(url))
    assert "Encerrada" in pagina
    assert "Encerrar operação" not in pagina and "Iniciar operação" not in pagina
    assert f"{url}/avancar" not in pagina


def test_r6_encerrada_nao_avanca_e_a_recusa_aparece_na_pagina(app, org_client):
    operacao = semear_operacao(app)
    for _ in range(2):
        assert org_client.post(f"/operacoes/{operacao}/avancar").status_code == 302
    resposta = org_client.post(f"/operacoes/{operacao}/avancar")
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert "Encerrada" in html(resposta)


def test_r6_so_uma_operacao_em_curso_por_vez(app, org_client):
    primeira = semear_operacao(app, nome="Primeira")
    segunda = semear_operacao(app, nome="Segunda")
    assert org_client.post(f"/operacoes/{primeira}/avancar").status_code == 302
    resposta = org_client.post(f"/operacoes/{segunda}/avancar")
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert "Planejada" in html(org_client.get(f"/operacoes/{segunda}"))


def test_r6_operacao_encerrada_nao_aceita_inscricao_e_nao_mostra_o_formulario(app, org_client):
    operacao = semear_operacao(app)
    operador = semear_operador(app)
    for _ in range(2):
        org_client.post(f"/operacoes/{operacao}/avancar")
    assert f"/operacoes/{operacao}/inscricoes" not in html(org_client.get(f"/operacoes/{operacao}"))
    resposta = inscrever(org_client, operacao, operador)
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert inscritos_de(app, operacao) == []


def test_r6_inscricao_de_operacao_encerrada_nao_muda(app, org_client):
    operacao = semear_operacao(app)
    inscricao = semear_inscricao(app, operacao, semear_operador(app))
    for _ in range(2):
        org_client.post(f"/operacoes/{operacao}/avancar")
    assert f"/inscricoes/{inscricao}" not in html(org_client.get(f"/operacoes/{operacao}"))
    resposta = org_client.post(f"/inscricoes/{inscricao}", data={"time": "Verde", "classe": "Médico"})
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert inscritos_de(app, operacao)[0]["time"] == "Azul"


def test_us02_operacao_continua_la_com_a_situacao_depois_de_reiniciar(app, org_client):
    operacao = semear_operacao(app)
    org_client.post(f"/operacoes/{operacao}/avancar")
    novo = segundo_app(app).test_client()
    novo.post("/login", data={"login": "org", "senha": SENHA_TESTE})
    assert "Em curso" in html(novo.get(f"/operacoes/{operacao}"))


# --------------------------------------- US03 e US04: inscrição e inscritos

def test_us03_formulario_oferece_operador_times_e_classes(app, org_client):
    operacao = semear_operacao(app)
    semear_operador(app, apelido="Falcao")
    pagina = html(org_client.get(f"/operacoes/{operacao}"))
    for campo in ("operador_id", "time", "classe", "dispositivo", "consentimento"):
        assert f'name="{campo}"' in pagina
    assert "Falcao" in pagina
    for nome in (*servicos.TIMES, *servicos.CLASSES):
        assert f'value="{nome}"' in pagina


def test_us04_inscrito_aparece_com_apelido_time_cor_classe_e_dispositivo(app, org_client):
    operacao = semear_operacao(app)
    operador = semear_operador(app)
    resposta = inscrever(org_client, operacao, operador, time="Vermelho", classe="Médico",
                         dispositivo="mt-07 ")
    assert resposta.status_code == 302
    assert caminho_do_redirecionamento(resposta) == f"/operacoes/{operacao}"
    pagina = html(org_client.get(f"/operacoes/{operacao}"))
    linha = re.search(r"<tr>(?:(?!</tr>).)*Falcao.*?</tr>", pagina, re.S).group(0)
    for esperado in ("Vermelho", "Médico", "MT-07", servicos.TIMES["Vermelho"]):
        assert esperado in linha


def test_r1_inscrever_em_duas_operacoes_nao_pede_novo_cadastro(app, org_client):
    primeira, segunda = semear_operacao(app, nome="Primeira"), semear_operacao(app, nome="Segunda")
    operador = semear_operador(app)
    assert inscrever(org_client, primeira, operador).status_code == 302
    assert inscrever(org_client, segunda, operador).status_code == 302
    assert html(org_client.get("/operadores")).count("Falcao") == 1


def test_r2_inscricao_duplicada_aparece_como_mensagem(app, org_client):
    operacao = semear_operacao(app)
    operador = semear_operador(app)
    inscrever(org_client, operacao, operador)
    resposta = inscrever(org_client, operacao, operador, dispositivo="MT-02")
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert len(inscritos_de(app, operacao)) == 1


def test_r3_dispositivo_repetido_aparece_como_mensagem(app, org_client):
    operacao = semear_operacao(app)
    inscrever(org_client, operacao, semear_operador(app, apelido="Falcao"))
    resposta = inscrever(org_client, operacao, semear_operador(app, apelido="Coruja"),
                         dispositivo="mt-01")
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert [i["apelido"] for i in inscritos_de(app, operacao)] == ["Falcao"]


def test_r3_o_mesmo_dispositivo_pode_ir_para_outra_operacao(app, org_client):
    primeira, segunda = semear_operacao(app, nome="Primeira"), semear_operacao(app, nome="Segunda")
    operador = semear_operador(app)
    assert inscrever(org_client, primeira, operador).status_code == 302
    assert inscrever(org_client, segunda, operador).status_code == 302


def test_r5_sem_consentimento_aparece_como_mensagem(app, org_client):
    operacao = semear_operacao(app)
    operador = semear_operador(app)
    resposta = inscrever(org_client, operacao, operador, omitir=("consentimento",))
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert inscritos_de(app, operacao) == []


def test_r5_o_formulario_nao_trava_a_recusa_no_navegador(app, org_client):
    """Sem `required` no checkbox, a recusa R5 chega ao servidor e aparece como mensagem."""
    operacao = semear_operacao(app)
    semear_operador(app)
    pagina = html(org_client.get(f"/operacoes/{operacao}"))
    checkbox = re.search(r'<input[^>]*name="consentimento"[^>]*>', pagina).group(0)
    assert "required" not in checkbox


def test_us03_recusa_devolve_os_valores_digitados(app, org_client):
    operacao = semear_operacao(app)
    semear_operador(app, apelido="Falcao")
    coruja = semear_operador(app, apelido="Coruja")
    resposta = inscrever(org_client, operacao, coruja, omitir=("consentimento",),
                         time="Verde", classe="Suporte", dispositivo="MT-55")
    pagina = html(resposta)
    assert 'value="MT-55"' in pagina
    assert re.search(rf'<option value="{coruja}"\s+selected', pagina)
    assert re.search(r'<option value="Verde"\s+selected', pagina)
    assert re.search(r'<option value="Suporte"\s+selected', pagina)


@pytest.mark.parametrize("mudanca", [
    {"operador_id": "abc"},
    {"operador_id": ""},
    {"operador_id": "999999"},
    {"operador_id": "99999999999999999999"},
    {"time": "Roxo"},
    {"classe": "Mago"},
    {"dispositivo": ""},
    {"dispositivo": "x" * 33},
])
def test_us03_dados_invalidos_voltam_400_sem_erro_500(app, org_client, mudanca):
    operacao = semear_operacao(app)
    operador = semear_operador(app)
    resposta = inscrever(org_client, operacao, operador, **mudanca)
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert inscritos_de(app, operacao) == []


def test_r4_mudar_time_e_classe_altera_so_a_inscricao(app, org_client):
    primeira, segunda = semear_operacao(app, nome="Primeira"), semear_operacao(app, nome="Segunda")
    operador = semear_operador(app)
    inscricao = semear_inscricao(app, primeira, operador, time="Azul", classe="Fuzileiro")
    semear_inscricao(app, segunda, operador, time="Verde", classe="Médico")
    with app.app_context():
        perfil = servicos.listar_operadores(db.get_repo())
    resposta = org_client.post(f"/inscricoes/{inscricao}", data={"time": "Vermelho", "classe": "Suporte"})
    assert resposta.status_code == 302
    assert caminho_do_redirecionamento(resposta) == f"/operacoes/{primeira}"
    primeiro = inscritos_de(app, primeira)[0]
    assert (primeiro["time"], primeiro["classe"]) == ("Vermelho", "Suporte")
    segundo = inscritos_de(app, segunda)[0]
    assert (segundo["time"], segundo["classe"]) == ("Verde", "Médico")
    with app.app_context():
        assert servicos.listar_operadores(db.get_repo()) == perfil


@pytest.mark.parametrize("dados", [
    {"time": "Roxo", "classe": "Suporte"},
    {"time": "Verde", "classe": "Mago"},
    {"time": "", "classe": ""},
])
def test_r4_alteracao_invalida_volta_400_e_nao_muda_nada(app, org_client, dados):
    operacao = semear_operacao(app)
    inscricao = semear_inscricao(app, operacao, semear_operador(app))
    resposta = org_client.post(f"/inscricoes/{inscricao}", data=dados)
    assert resposta.status_code == 400
    assert alerta(resposta)
    assert inscritos_de(app, operacao)[0]["time"] == "Azul"


def test_us03_inscricao_continua_la_depois_de_reiniciar(app, org_client):
    operacao = semear_operacao(app)
    inscrever(org_client, operacao, semear_operador(app))
    novo = segundo_app(app).test_client()
    novo.post("/login", data={"login": "org", "senha": SENHA_TESTE})
    pagina = html(novo.get(f"/operacoes/{operacao}"))
    assert "Falcao" in pagina and "MT-01" in pagina


def test_operacao_ou_inscricao_inexistente_e_404(org_client):
    assert org_client.get("/operacoes/999").status_code == 404
    assert org_client.post("/operacoes/999/avancar").status_code == 404
    assert inscrever(org_client, 999, 1).status_code == 404
    assert org_client.post("/inscricoes/999", data={"time": "Azul", "classe": "Médico"}).status_code == 404


@pytest.mark.parametrize("metodo, caminho", [
    ("get", "/operacoes/99999999999999999999"),
    ("post", "/operacoes/99999999999999999999/avancar"),
    ("post", "/operacoes/99999999999999999999/inscricoes"),
    ("post", "/inscricoes/99999999999999999999"),
])
def test_id_gigante_na_url_e_404_e_nao_500(org_client, metodo, caminho):
    assert getattr(org_client, metodo)(caminho, data={}).status_code == 404


def test_paginas_declaram_icone_para_o_navegador_nao_pedir_favicon(client, org_client):
    assert 'rel="icon"' in html(client.get("/login"))
    assert 'rel="icon"' in html(org_client.get("/operacoes"))
