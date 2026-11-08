"""Roteiro funcional da demo de 10/11, de ponta a ponta, só pelo test client.

Percorre o que o professor vai ver: cadastrar 5 operadores, rodar a Operação 1,
reinscrever os mesmos 5 numa Operação 2 sem novo cadastro (H1/R1), as três
recusas (R2, R3, R5), a passagem para em curso (R6), os sinais pela API (R7,
R8, R11), os quatro estados (R9, H2) e o observador (R10).

Cada teste parte de um banco novo e monta o cenário com as fixtures abaixo:

    operadores        {apelido: id} dos 5 operadores já cadastrados pelo formulário
    operacao1         id da Operação 1, com os 5 inscritos e encerrada
    operacao2         id da Operação 2, planejada, com os mesmos 5 em outros times
    operacao2_em_curso  a mesma, já em curso
"""

import re
import time
from html import unescape

import pytest

import db
import servicos
from conftest import TOKEN

OPERADORES = [
    ("Falcão", "Marina Souza"),
    ("Lobo", "Carlos Lima"),
    ("Coruja", "Beatriz Alves"),
    ("Raposa", "Rafael Mota"),
    ("Pantera", "Helena Dias"),
]
# (apelido, time, classe, dispositivo)
INSCRITOS_1 = [
    ("Falcão", "Azul", "Fuzileiro", "MT-01"),
    ("Lobo", "Vermelho", "Suporte", "MT-02"),
    ("Coruja", "Verde", "Atirador designado", "MT-03"),
    ("Raposa", "Amarelo", "Médico", "MT-04"),
    ("Pantera", "Verde", "Fuzileiro", "MT-05"),
]
INSCRITOS_2 = [
    ("Falcão", "Vermelho", "Médico", "MT-01"),
    ("Lobo", "Verde", "Fuzileiro", "MT-02"),
    ("Coruja", "Amarelo", "Suporte", "MT-03"),
    ("Raposa", "Azul", "Atirador designado", "MT-04"),
    ("Pantera", "Amarelo", "Fuzileiro", "MT-05"),
]

MSG_DUPLICADA = "Este operador já está inscrito nesta operação."
MSG_DISPOSITIVO = "Este dispositivo já pertence a outra inscrição desta operação."
MSG_CONSENTIMENTO = "A inscrição exige o consentimento de rastreamento."

REGEX_ALERTA = re.compile(r'<p class="mensagem mensagem-erro" role="alert">(.*?)</p>', re.S)
REGEX_ACTION = re.compile(r'<form[^>]*\baction="([^"]*)"')


# ------------------------------------------------------------------ apoio

def html(resposta) -> str:
    return resposta.get_data(as_text=True)


def alerta(resposta) -> str | None:
    achado = REGEX_ALERTA.search(html(resposta))
    return unescape(achado.group(1)).strip() if achado else None


def acoes(resposta) -> list[str]:
    return REGEX_ACTION.findall(html(resposta))


def id_da_operacao_criada(resposta) -> int:
    assert resposta.status_code == 302
    return int(resposta.headers["Location"].rstrip("/").split("/")[-1])


def listar_inscritos_da_pagina(pagina) -> list[str]:
    return re.findall(r"<td>(MT-\d\d)</td>", html(pagina))


def listar_operadores(app) -> list[dict]:
    with app.app_context():
        return servicos.listar_operadores(db.get_repo())


def listar_inscritos(app, operacao_id: int) -> list[dict]:
    with app.app_context():
        return servicos.listar_inscritos(db.get_repo(), operacao_id)


def criar_operacao(org, nome: str, data: str) -> int:
    resposta = org.post("/operacoes", data={"nome": nome, "data": data, "local": "Parque da Cidade",
                                            "centro_lat": "-15.799", "centro_lon": "-47.907"})
    return id_da_operacao_criada(resposta)


def avancar(org, operacao_id: int):
    return org.post(f"/operacoes/{operacao_id}/avancar")


def inscrever(org, operacao_id: int, operador_id: int, time_: str, classe: str,
              dispositivo: str, consentimento: bool = True):
    dados = {"operador_id": str(operador_id), "time": time_, "classe": classe,
             "dispositivo": dispositivo}
    if consentimento:
        dados["consentimento"] = "1"
    return org.post(f"/operacoes/{operacao_id}/inscricoes", data=dados)


def inscrever_todos(org, operacao_id: int, operadores: dict, lista: list) -> None:
    for apelido, time_, classe, dispositivo in lista:
        resposta = inscrever(org, operacao_id, operadores[apelido], time_, classe, dispositivo)
        assert resposta.status_code == 302, (apelido, alerta(resposta))


def sinal(client, cabecalho, dispositivo: str, pacote: int, lat=-15.799, lon=-47.907):
    return client.post("/api/v1/sinais", headers=cabecalho, json={
        "dispositivo": dispositivo, "pacote": pacote, "lat": lat, "lon": lon, "bateria": 80})


def estados(client, cabecalho, operacao_id: int) -> dict:
    resposta = client.get(f"/api/v1/situacao?operacao={operacao_id}", headers=cabecalho)
    assert resposta.status_code == 200
    return {i["dispositivo"]: i["estado"] for i in resposta.get_json()["inscritos"]}


# --------------------------------------------------------------- cenários

@pytest.fixture
def operadores(app, org_client) -> dict:
    """Passo 1: cadastra os 5 operadores pelo formulário (US01)."""
    for apelido, nome in OPERADORES:
        resposta = org_client.post("/operadores", data={"apelido": apelido, "nome": nome})
        assert resposta.status_code == 302
    return {o["apelido"]: o["id"] for o in listar_operadores(app)}


@pytest.fixture
def operacao1(org_client, operadores) -> int:
    """Passo 2: Operação 1 com os 5 inscritos, planejada -> em curso -> encerrada."""
    operacao_id = criar_operacao(org_client, "Operação Alfa", "2026-10-25")
    inscrever_todos(org_client, operacao_id, operadores, INSCRITOS_1)
    assert avancar(org_client, operacao_id).status_code == 302
    assert avancar(org_client, operacao_id).status_code == 302
    return operacao_id


@pytest.fixture
def operacao2(org_client, operadores, operacao1) -> int:
    """Passo 3: Operação 2, os mesmos 5 operadores, outros times, sem novo cadastro."""
    operacao_id = criar_operacao(org_client, "Operação Bravo", "2026-11-10")
    inscrever_todos(org_client, operacao_id, operadores, INSCRITOS_2)
    return operacao_id


@pytest.fixture
def operacao2_em_curso(org_client, operacao2) -> int:
    assert avancar(org_client, operacao2).status_code == 302
    return operacao2


# ------------------------------------------------- passos 1 a 3: cadastro e H1

def test_funcional_cadastra_cinco_operadores(org_client, operadores):
    pagina = org_client.get("/operadores")

    assert pagina.status_code == 200
    assert len(operadores) == 5
    for apelido, nome in OPERADORES:
        assert apelido in html(pagina)
        assert nome in html(pagina)


def test_funcional_operacao1_vai_de_planejada_a_encerrada(org_client, operadores):
    operacao_id = criar_operacao(org_client, "Operação Alfa", "2026-10-25")
    assert "Planejada" in html(org_client.get(f"/operacoes/{operacao_id}"))
    inscrever_todos(org_client, operacao_id, operadores, INSCRITOS_1)

    avancar(org_client, operacao_id)
    assert "Em curso" in html(org_client.get(f"/operacoes/{operacao_id}"))
    avancar(org_client, operacao_id)

    pagina = org_client.get(f"/operacoes/{operacao_id}")
    assert "Encerrada" in html(pagina)
    assert "Operação encerrada" in html(pagina)
    assert "Iniciar operação" not in html(pagina)
    assert "Encerrar operação" not in html(pagina)
    assert avancar(org_client, operacao_id).status_code == 400
    assert len(listar_inscritos_da_pagina(pagina)) == 5


def test_funcional_h1_reinscreve_os_cinco_na_operacao2_sem_novo_cadastro(
        app, org_client, operadores, operacao1):
    antes = listar_operadores(app)
    inicio = time.perf_counter()

    operacao_id = criar_operacao(org_client, "Operação Bravo", "2026-11-10")
    inscrever_todos(org_client, operacao_id, operadores, INSCRITOS_2)
    pagina = org_client.get(f"/operacoes/{operacao_id}")

    # Medida do fluxo pelo test client (o tempo do organizador está em docs/evidencias/funcional.md).
    assert time.perf_counter() - inicio < 180
    assert pagina.status_code == 200
    assert listar_operadores(app) == antes             # R1: nenhum cadastro novo, perfis intactos
    assert len(listar_operadores(app)) == 5
    inscritos = {i["apelido"]: i for i in listar_inscritos(app, operacao_id)}
    assert len(inscritos) == 5
    for apelido, time_, classe, dispositivo in INSCRITOS_2:
        assert (inscritos[apelido]["time"], inscritos[apelido]["classe"],
                inscritos[apelido]["dispositivo"]) == (time_, classe, dispositivo)
        assert inscritos[apelido]["operador_id"] == operadores[apelido]
    # Os times mudaram em relação à Operação 1 (R4) e a Operação 1 continua como estava.
    antigos = {i["apelido"]: i["time"] for i in listar_inscritos(app, operacao1)}
    assert all(antigos[a] != inscritos[a]["time"] for a in antigos)


def test_funcional_alterar_time_e_classe_nao_muda_o_perfil(app, org_client, operadores, operacao2):
    antes = listar_operadores(app)
    inscrito = listar_inscritos(app, operacao2)[0]

    resposta = org_client.post(f"/inscricoes/{inscrito['id']}",
                               data={"time": "Azul", "classe": "Suporte"})

    assert resposta.status_code == 302
    novo = next(i for i in listar_inscritos(app, operacao2) if i["id"] == inscrito["id"])
    assert (novo["time"], novo["classe"]) == ("Azul", "Suporte")
    assert listar_operadores(app) == antes


def test_funcional_operacao_encerrada_nao_aceita_inscricao(org_client, operadores, operacao1):
    resposta = inscrever(org_client, operacao1, operadores["Falcão"], "Azul", "Fuzileiro", "MT-09")

    assert resposta.status_code == 400
    assert "encerrada" in alerta(resposta)


# ------------------------------------------------------- passo 4: as 3 recusas

def test_funcional_recusa_inscricao_duplicada(app, org_client, operadores, operacao2):
    resposta = inscrever(org_client, operacao2, operadores["Falcão"], "Azul", "Suporte", "MT-77")

    assert resposta.status_code == 400
    assert alerta(resposta) == MSG_DUPLICADA
    assert len(listar_inscritos(app, operacao2)) == 5


def test_funcional_recusa_dispositivo_repetido(app, org_client, operadores, operacao1):
    outra = criar_operacao(org_client, "Operação Charlie", "2026-11-22")
    assert inscrever(org_client, outra, operadores["Falcão"], "Azul", "Fuzileiro", "MT-01"
                     ).status_code == 302

    resposta = inscrever(org_client, outra, operadores["Lobo"], "Verde", "Suporte", " mt-01 ")

    assert resposta.status_code == 400
    assert alerta(resposta) == MSG_DISPOSITIVO
    assert [i["apelido"] for i in listar_inscritos(app, outra)] == ["Falcão"]


def test_funcional_recusa_inscricao_sem_consentimento(app, org_client, operadores, operacao1):
    outra = criar_operacao(org_client, "Operação Charlie", "2026-11-22")

    resposta = inscrever(org_client, outra, operadores["Falcão"], "Azul", "Fuzileiro", "MT-01",
                         consentimento=False)

    assert resposta.status_code == 400
    assert alerta(resposta) == MSG_CONSENTIMENTO
    assert listar_inscritos(app, outra) == []


# --------------------------------------------------- passo 5: em curso (R6)

def test_funcional_operacao2_passa_para_em_curso(org_client, operacao2):
    assert "Planejada" in html(org_client.get(f"/operacoes/{operacao2}"))

    assert avancar(org_client, operacao2).status_code == 302

    pagina = org_client.get(f"/operacoes/{operacao2}")
    assert "Em curso" in html(pagina)
    assert "Encerrar operação" in html(pagina)


def test_funcional_so_uma_operacao_em_curso_por_vez(org_client, operacao2_em_curso):
    outra = criar_operacao(org_client, "Operação Charlie", "2026-11-22")

    resposta = avancar(org_client, outra)

    assert resposta.status_code == 400
    assert "Já existe outra operação em curso" in alerta(resposta)


# ------------------------------------------------------- passo 6: sinais (API)

def test_funcional_api_recusa_sem_token_e_com_token_errado(client, operacao2_em_curso):
    corpo = {"dispositivo": "MT-01", "pacote": 1, "lat": -15.799, "lon": -47.907, "bateria": 80}

    assert client.post("/api/v1/sinais", json=corpo).status_code == 401
    assert client.get("/api/v1/situacao").status_code == 401
    errado = {"Authorization": "Bearer outro-token"}
    resposta = client.post("/api/v1/sinais", json=corpo, headers=errado)
    assert resposta.status_code == 401
    assert resposta.get_json()["codigo"] == "nao_autorizado"


def test_funcional_sinais_201_200_e_202(client, cabecalho_token, operacao2_em_curso):
    assert cabecalho_token == {"Authorization": f"Bearer {TOKEN}"}

    primeiro = sinal(client, cabecalho_token, "MT-01", 1)
    repetido = sinal(client, cabecalho_token, "MT-01", 1)
    estranho = sinal(client, cabecalho_token, "MT-99", 1)

    assert (primeiro.status_code, primeiro.get_json()) == (201, {"status": "gravado"})
    assert (repetido.status_code, repetido.get_json()) == (200, {"status": "duplicado"})
    assert (estranho.status_code, estranho.get_json()) == (202, {"status": "descartado"})
    situacao = client.get("/api/v1/situacao", headers=cabecalho_token).get_json()
    assert situacao["operacao"]["id"] == operacao2_em_curso
    assert situacao["descartados"] == 1
    mt01 = next(i for i in situacao["inscritos"] if i["dispositivo"] == "MT-01")
    assert mt01["estado"] == "ativo"
    assert all(i["dispositivo"] != "MT-99" for i in situacao["inscritos"])    # MT-99 nunca vira posição


def test_funcional_sinal_fora_de_operacao_em_curso_e_descartado(client, cabecalho_token, operacao2):
    resposta = sinal(client, cabecalho_token, "MT-01", 1)     # a Operação 2 ainda está planejada

    assert resposta.status_code == 202


# ------------------------------------------------ passo 7: os quatro estados

def test_funcional_quatro_estados_com_o_relogio(client, cabecalho_token, relogio, operacao2_em_curso):
    # sem_sinal: ninguém mandou nada ainda.
    assert set(estados(client, cabecalho_token, operacao2_em_curso).values()) == {"sem_sinal"}

    # ativo: os cinco mandam um sinal.
    for numero in range(1, 6):
        assert sinal(client, cabecalho_token, f"MT-0{numero}", 1).status_code == 201
    assert set(estados(client, cabecalho_token, operacao2_em_curso).values()) == {"ativo"}

    # Só o MT-03 se cala. Os outros continuam mandando a cada 20 s.
    def todos_menos_mt03(pacote: int) -> None:
        for numero in (1, 2, 4, 5):
            assert sinal(client, cabecalho_token, f"MT-0{numero}", pacote).status_code == 201

    relogio.avancar(30)
    todos_menos_mt03(2)
    assert estados(client, cabecalho_token, operacao2_em_curso)["MT-03"] == "ativo"      # 30 s
    relogio.avancar(31)
    todos_menos_mt03(3)
    situacao = estados(client, cabecalho_token, operacao2_em_curso)
    assert situacao["MT-03"] == "atrasado"                                               # 61 s
    assert {situacao[d] for d in ("MT-01", "MT-02", "MT-04", "MT-05")} == {"ativo"}
    relogio.avancar(60)
    todos_menos_mt03(4)
    situacao = estados(client, cabecalho_token, operacao2_em_curso)
    assert situacao["MT-03"] == "perdido"                                                # 121 s
    assert {situacao[d] for d in ("MT-01", "MT-02", "MT-04", "MT-05")} == {"ativo"}

    # Um sinal novo traz o MT-03 de volta.
    assert sinal(client, cabecalho_token, "MT-03", 2).status_code == 201
    assert estados(client, cabecalho_token, operacao2_em_curso)["MT-03"] == "ativo"


def test_funcional_limites_exatos_dos_estados(client, cabecalho_token, relogio, operacao2_em_curso):
    sinal(client, cabecalho_token, "MT-03", 1)

    relogio.avancar(60)
    assert estados(client, cabecalho_token, operacao2_em_curso)["MT-03"] == "ativo"      # 60 s
    relogio.avancar(1)
    assert estados(client, cabecalho_token, operacao2_em_curso)["MT-03"] == "atrasado"    # 61 s
    relogio.avancar(59)
    assert estados(client, cabecalho_token, operacao2_em_curso)["MT-03"] == "atrasado"    # 120 s
    relogio.avancar(1)
    assert estados(client, cabecalho_token, operacao2_em_curso)["MT-03"] == "perdido"     # 121 s


# ---------------------------------------------------- passo 8: o observador

def test_funcional_observador_ve_a_operacao_sem_formularios(obs_client, operacao2_em_curso):
    pagina = obs_client.get(f"/operacoes/{operacao2_em_curso}")

    assert pagina.status_code == 200
    assert "Operação Bravo" in html(pagina)
    for apelido, _ in OPERADORES:
        assert apelido in html(pagina)
    assert acoes(pagina) == ["/logout"]                  # só o "Sair"; nenhum formulário de escrita
    for texto in ("Inscrever", "Encerrar operação", "Iniciar operação", "Alterar"):
        assert texto not in html(pagina)
    assert "Abrir mapa" in html(pagina)


def test_funcional_observador_ve_a_lista_de_operadores_e_operacoes_sem_formularios(
        obs_client, operacao2_em_curso):
    operadores_ = obs_client.get("/operadores")
    operacoes_ = obs_client.get("/operacoes")

    assert operadores_.status_code == operacoes_.status_code == 200
    assert acoes(operadores_) == ["/logout"]
    assert acoes(operacoes_) == ["/logout"]
    assert "Cadastrar" not in html(operadores_)


def test_funcional_observador_ve_o_mapa_e_a_situacao(obs_client, client, cabecalho_token,
                                                     operacao2_em_curso):
    sinal(client, cabecalho_token, "MT-01", 1)

    mapa = obs_client.get(f"/operacoes/{operacao2_em_curso}/mapa")
    api = obs_client.get(f"/api/v1/situacao?operacao={operacao2_em_curso}")

    assert mapa.status_code == 200
    assert f'data-operacao-id="{operacao2_em_curso}"' in html(mapa)
    assert api.status_code == 200                                # a sessão basta, sem token
    assert len(api.get_json()["inscritos"]) == 5


def test_funcional_observador_recebe_403_em_toda_escrita(app, obs_client, operadores, operacao2):
    inscrito = listar_inscritos(app, operacao2)[0]
    antes = (listar_operadores(app), listar_inscritos(app, operacao2))

    respostas = [
        obs_client.post("/operadores", data={"apelido": "Novo", "nome": "Fulano de Tal"}),
        obs_client.post("/operacoes", data={"nome": "X", "data": "2026-12-01", "local": "Y"}),
        avancar(obs_client, operacao2),
        inscrever(obs_client, operacao2, operadores["Falcão"], "Azul", "Suporte", "MT-88"),
        obs_client.post(f"/inscricoes/{inscrito['id']}", data={"time": "Azul", "classe": "Suporte"}),
    ]

    assert [r.status_code for r in respostas] == [403] * 5
    assert (listar_operadores(app), listar_inscritos(app, operacao2)) == antes
    with app.app_context():
        assert servicos.obter_operacao(db.get_repo(), operacao2)["situacao"] == "planejada"


def test_funcional_sem_login_vai_para_o_login(client, operacao2):
    for caminho in ("/operadores", "/operacoes", f"/operacoes/{operacao2}",
                    f"/operacoes/{operacao2}/mapa"):
        resposta = client.get(caminho)
        assert resposta.status_code == 302
        assert "/login" in resposta.headers["Location"]


# ----------------------------------------------------- o roteiro numa tacada só

def test_funcional_roteiro_de_ponta_a_ponta(app, client, org_client, obs_client, cabecalho_token,
                                            relogio):
    # 1. Cinco operadores, uma vez só.
    for apelido, nome in OPERADORES:
        org_client.post("/operadores", data={"apelido": apelido, "nome": nome})
    ids = {o["apelido"]: o["id"] for o in listar_operadores(app)}
    assert len(ids) == 5

    # 2. Operação 1, cinco inscritos, até encerrada.
    primeira = criar_operacao(org_client, "Operação Alfa", "2026-10-25")
    inscrever_todos(org_client, primeira, ids, INSCRITOS_1)
    avancar(org_client, primeira)
    avancar(org_client, primeira)

    # 3. Operação 2: os mesmos cinco, outros times, sem novo cadastro (H1).
    segunda = criar_operacao(org_client, "Operação Bravo", "2026-11-10")
    inscrever_todos(org_client, segunda, ids, INSCRITOS_2)
    assert len(listar_operadores(app)) == 5

    # 4. As três recusas.
    assert alerta(inscrever(org_client, segunda, ids["Lobo"], "Azul", "Suporte", "MT-70")
                  ) == MSG_DUPLICADA
    terceira = criar_operacao(org_client, "Operação Charlie", "2026-11-22")
    inscrever(org_client, terceira, ids["Falcão"], "Azul", "Fuzileiro", "MT-01")
    assert alerta(inscrever(org_client, terceira, ids["Lobo"], "Verde", "Suporte", "MT-01")
                  ) == MSG_DISPOSITIVO
    assert alerta(inscrever(org_client, terceira, ids["Coruja"], "Verde", "Suporte", "MT-03",
                            consentimento=False)) == MSG_CONSENTIMENTO

    # 5. Em curso, e os sinais pela API.
    assert avancar(org_client, segunda).status_code == 302
    assert client.post("/api/v1/sinais", json={"dispositivo": "MT-01", "pacote": 1, "lat": -15.8,
                                               "lon": -47.9, "bateria": 90}).status_code == 401
    assert sinal(client, cabecalho_token, "MT-01", 1).status_code == 201
    assert sinal(client, cabecalho_token, "MT-01", 1).status_code == 200
    assert sinal(client, cabecalho_token, "MT-99", 1).status_code == 202

    # 6. Os estados, no relógio injetado (H2).
    for numero in range(2, 6):
        sinal(client, cabecalho_token, f"MT-0{numero}", 1)
    relogio.avancar(121)
    assert set(estados(client, cabecalho_token, segunda).values()) == {"perdido"}
    sinal(client, cabecalho_token, "MT-01", 2)
    assert estados(client, cabecalho_token, segunda)["MT-01"] == "ativo"

    # 7. O observador vê tudo e não escreve.
    assert acoes(obs_client.get(f"/operacoes/{segunda}")) == ["/logout"]
    assert obs_client.get(f"/operacoes/{segunda}/mapa").status_code == 200
    assert avancar(obs_client, segunda).status_code == 403
