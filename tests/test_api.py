"""API /api/v1 (US05, US06, US08; R7, R8, R9, R11), e mapa.

Os testes de formato (400) e de autenticação (401) não dependem
de servicos.py: trocam a regra por um dublê. Os demais usam as regras reais
(R6 a R9) e só passam depois que o agente regras terminar.
"""

import json
import re
from pathlib import Path

import pytest

import db
import servicos

RAIZ = Path(__file__).resolve().parent.parent
SINAL = {"dispositivo": "MT-01", "pacote": 1, "lat": -15.79, "lon": -47.88, "bateria": 90}


def sinal(**mudancas):
    return {**SINAL, **mudancas}


def sem_campo(campo):
    return {k: v for k, v in SINAL.items() if k != campo}


def postar(client, corpo, cabecalho):
    """Manda o corpo como JSON; texto bruto vai como está (permite NaN e JSON quebrado)."""
    dados = corpo if isinstance(corpo, str) else json.dumps(corpo)
    return client.post("/api/v1/sinais", data=dados, content_type="application/json", headers=cabecalho)


def preparar(app, dispositivos=("MT-01",), iniciar=True):
    """Cria uma operação com um inscrito por dispositivo e devolve o id."""
    with app.app_context():
        repo = db.get_repo()
        agora = app.config["RELOGIO"]()
        operacao = servicos.criar_operacao(repo, "Operação Teste", "2026-11-10", "Parque")
        for i, dispositivo in enumerate(dispositivos, start=1):
            operador = servicos.cadastrar_operador(repo, f"op{i}", f"Operador {i}", agora)
            servicos.inscrever(repo, operacao, operador, "Azul", "Fuzileiro", dispositivo, True)
        if iniciar:
            servicos.avancar_situacao(repo, operacao)
    return operacao


def situacao(client, cabecalho, operacao_id):
    resposta = client.get(f"/api/v1/situacao?operacao={operacao_id}", headers=cabecalho)
    assert resposta.status_code == 200
    return resposta.get_json()


def inscrito(dados, dispositivo="MT-01"):
    return next(i for i in dados["inscritos"] if i["dispositivo"] == dispositivo)


def contar_posicoes(app, inscricao_id):
    with app.app_context():
        return db.get_repo().contar_posicoes(inscricao_id)


@pytest.fixture
def servico_falso(monkeypatch):
    """Troca servicos.receber_sinal por um dublê que guarda as chamadas e devolve `resultado`."""
    class Falso:
        resultado = "gravado"
        chamadas = []

    def receber(repo, dispositivo, pacote, lat, lon, bateria, agora):
        Falso.chamadas.append((dispositivo, pacote, lat, lon, bateria, agora))
        return Falso.resultado

    Falso.chamadas = []
    monkeypatch.setattr(servicos, "receber_sinal", receber)
    return Falso


@pytest.fixture
def ler(request, client, cabecalho_token):
    """GET como observador, como organizador e com o token: os três podem ler (US08)."""
    if request.param == "token":
        return lambda url: client.get(url, headers=cabecalho_token)
    return request.getfixturevalue(request.param).get


LEITORES = pytest.mark.parametrize("ler", ["obs_client", "org_client", "token"], indirect=True)


# ------------------------------------------------------------- 400: formato

CASOS_400 = [
    pytest.param("[1, 2]", None, id="corpo-lista"),
    pytest.param('"texto"', None, id="corpo-texto"),
    pytest.param("null", None, id="corpo-null"),
    pytest.param("{isto nao e json", None, id="json-quebrado"),
    pytest.param("", None, id="corpo-vazio"),
    *[pytest.param(sem_campo(c), c, id=f"falta-{c}") for c in SINAL],
    pytest.param(sinal(dispositivo=123), "dispositivo", id="dispositivo-numero"),
    pytest.param(sinal(dispositivo=None), "dispositivo", id="dispositivo-null"),
    pytest.param(sinal(dispositivo=["MT-01"]), "dispositivo", id="dispositivo-lista"),
    pytest.param(sinal(dispositivo=""), "dispositivo", id="dispositivo-vazio"),
    pytest.param(sinal(dispositivo="   "), "dispositivo", id="dispositivo-so-espacos"),
    pytest.param(sinal(dispositivo="M" * 33), "dispositivo", id="dispositivo-33-caracteres"),
    pytest.param(sinal(pacote="1"), "pacote", id="pacote-texto"),
    pytest.param(sinal(pacote=True), "pacote", id="pacote-bool"),
    pytest.param(sinal(pacote=1.5), "pacote", id="pacote-fracionario"),
    pytest.param(sinal(pacote=None), "pacote", id="pacote-null"),
    pytest.param(sinal(pacote=-1), "pacote", id="pacote-negativo"),
    pytest.param(sinal(pacote=2**63), "pacote", id="pacote-maior-que-o-banco"),
    pytest.param(sinal(lat="1"), "lat", id="lat-texto"),
    pytest.param(sinal(lat=True), "lat", id="lat-bool"),
    pytest.param(sinal(lat=None), "lat", id="lat-null"),
    pytest.param(sinal(lat=90.0001), "lat", id="lat-acima-de-90"),
    pytest.param(sinal(lat=-90.0001), "lat", id="lat-abaixo-de-menos-90"),
    pytest.param(sinal(lat=float("nan")), "lat", id="lat-nan"),
    pytest.param(sinal(lat=float("inf")), "lat", id="lat-infinito"),
    pytest.param(sinal(lat=10**400), "lat", id="lat-inteiro-enorme"),
    pytest.param(sinal(lon="1"), "lon", id="lon-texto"),
    pytest.param(sinal(lon=False), "lon", id="lon-bool"),
    pytest.param(sinal(lon=None), "lon", id="lon-null"),
    pytest.param(sinal(lon=180.0001), "lon", id="lon-acima-de-180"),
    pytest.param(sinal(lon=-180.0001), "lon", id="lon-abaixo-de-menos-180"),
    pytest.param(sinal(lon=float("-inf")), "lon", id="lon-menos-infinito"),
    pytest.param(sinal(bateria="90"), "bateria", id="bateria-texto"),
    pytest.param(sinal(bateria=True), "bateria", id="bateria-bool"),
    pytest.param(sinal(bateria=None), "bateria", id="bateria-null"),
    pytest.param(sinal(bateria=-0.1), "bateria", id="bateria-abaixo-de-0"),
    pytest.param(sinal(bateria=100.1), "bateria", id="bateria-acima-de-100"),
    pytest.param(sinal(bateria=float("nan")), "bateria", id="bateria-nan"),
]


@pytest.mark.parametrize("corpo, campo", CASOS_400)
def test_sinal_com_formato_invalido_devolve_400(client, cabecalho_token, servico_falso, corpo, campo):
    resposta = postar(client, corpo, cabecalho_token)
    assert resposta.status_code == 400
    dados = resposta.get_json()
    assert dados["codigo"] == "formato_invalido"
    assert campo is None or f"'{campo}'" in dados["erro"]
    assert servico_falso.chamadas == []


@pytest.mark.parametrize("mudancas", [
    dict(lat=90), dict(lat=-90), dict(lon=180), dict(lon=-180), dict(bateria=0), dict(bateria=100),
    dict(pacote=0), dict(dispositivo="M" * 32), dict(dispositivo=" mt-01 "), dict(extra="ignorado"),
], ids=lambda m: "-".join(f"{k}={str(v)[:8]}" for k, v in m.items()))
def test_sinal_nos_limites_do_formato_e_aceito(client, cabecalho_token, servico_falso, mudancas):
    resposta = postar(client, sinal(**mudancas), cabecalho_token)
    assert resposta.status_code == 201
    assert len(servico_falso.chamadas) == 1


def test_sinal_chega_ao_servico_com_tipos_e_relogio_certos(client, cabecalho_token, servico_falso, relogio):
    postar(client, sinal(pacote=7, lat=-16, lon=-48, bateria=80), cabecalho_token)
    dispositivo, pacote, lat, lon, bateria, agora = servico_falso.chamadas[0]
    assert (dispositivo, pacote, lat, lon, bateria) == ("MT-01", 7, -16.0, -48.0, 80.0)
    assert isinstance(lat, float) and isinstance(bateria, float)
    assert agora == relogio()


@pytest.mark.parametrize("resultado, status", [("gravado", 201), ("duplicado", 200), ("descartado", 202)])
def test_sinal_traduz_o_resultado_do_servico_em_status_http(
        client, cabecalho_token, servico_falso, resultado, status):
    servico_falso.resultado = resultado
    resposta = postar(client, SINAL, cabecalho_token)
    assert (resposta.status_code, resposta.get_json()) == (status, {"status": resultado})


def test_sinal_nao_exige_csrf(app, client, cabecalho_token, servico_falso):
    app.config["WTF_CSRF_ENABLED"] = True   # no app de verdade o CSRF fica ligado
    assert postar(client, SINAL, cabecalho_token).status_code == 201


# ------------------------------------------------------------ 401: token (R11)

def test_r11_sem_token_devolve_401_no_formato_de_erro(client, servico_falso):
    resposta = postar(client, SINAL, {})
    assert resposta.status_code == 401
    dados = resposta.get_json()
    assert dados["codigo"] == "nao_autorizado" and dados["erro"]
    assert servico_falso.chamadas == []


@pytest.mark.parametrize("cabecalho", [
    {"Authorization": "Bearer token-errado"},
    {"Authorization": "Bearer "},
    {"Authorization": "Basic dG9rZW4="},
    {"Authorization": "token-de-teste-0123456789"},
], ids=["token-errado", "bearer-vazio", "esquema-basic", "sem-esquema"])
def test_r11_token_errado_devolve_401(client, servico_falso, cabecalho):
    assert postar(client, SINAL, cabecalho).status_code == 401
    assert servico_falso.chamadas == []


@pytest.mark.parametrize("configurado", [None, ""])
def test_r11_sem_token_configurado_nenhum_sinal_passa(app, client, servico_falso, cabecalho_token, configurado):
    app.config["MESHTRACKER_TOKEN"] = configurado
    for cabecalho in (cabecalho_token, {"Authorization": "Bearer "}, {}):
        assert postar(client, SINAL, cabecalho).status_code == 401
    assert servico_falso.chamadas == []


def test_r11_o_401_vem_antes_da_validacao_do_corpo(client):
    assert postar(client, "isto nao e json", {}).status_code == 401


def test_r11_sinal_sem_token_nao_grava(app, client, cabecalho_token):
    operacao = preparar(app)
    postar(client, SINAL, {})
    dados = situacao(client, cabecalho_token, operacao)
    assert inscrito(dados)["estado"] == "sem_sinal"


# ----------------------------------------------------- R7: descarte e contagem

def test_r7_sinal_sem_inscricao_e_descartado_e_contado(app, client, cabecalho_token):
    operacao = preparar(app)
    resposta = postar(client, sinal(dispositivo="MT-99"), cabecalho_token)
    assert (resposta.status_code, resposta.get_json()) == (202, {"status": "descartado"})
    dados = situacao(client, cabecalho_token, operacao)
    assert dados["descartados"] == 1
    assert inscrito(dados)["lat"] is None
    assert contar_posicoes(app, inscrito(dados)["inscricao_id"]) == 0


def test_r7_descartes_se_acumulam(app, client, cabecalho_token):
    operacao = preparar(app)
    for pacote in (1, 2, 3):
        assert postar(client, sinal(dispositivo="MT-99", pacote=pacote), cabecalho_token).status_code == 202
    assert situacao(client, cabecalho_token, operacao)["descartados"] == 3


def test_r7_sem_operacao_em_curso_o_sinal_e_descartado(app, client, cabecalho_token):
    resposta = postar(client, SINAL, cabecalho_token)
    assert (resposta.status_code, resposta.get_json()) == (202, {"status": "descartado"})
    with app.app_context():
        linhas = db.get_db().execute("SELECT operacao_id, motivo, dispositivo FROM descarte").fetchall()
    assert [tuple(linha) for linha in linhas] == [(None, "sem_operacao_em_curso", "MT-01")]


@pytest.mark.parametrize("avancos", [0, 2], ids=["planejada", "encerrada"])
def test_r7_operacao_fora_de_curso_descarta_ate_o_inscrito(app, client, cabecalho_token, avancos):
    operacao = preparar(app, iniciar=False)
    with app.app_context():
        for _ in range(avancos):
            servicos.avancar_situacao(db.get_repo(), operacao)
    assert postar(client, SINAL, cabecalho_token).status_code == 202
    assert inscrito(situacao(client, cabecalho_token, operacao))["estado"] == "sem_sinal"


# -------------------------------------------------------------- 201 e R8

def test_sinal_valido_de_inscrito_e_gravado_e_aparece_na_situacao(app, client, cabecalho_token):
    operacao = preparar(app)
    resposta = postar(client, SINAL, cabecalho_token)
    assert (resposta.status_code, resposta.get_json()) == (201, {"status": "gravado"})
    item = inscrito(situacao(client, cabecalho_token, operacao))
    assert (item["lat"], item["lon"], item["bateria"]) == (-15.79, -47.88, 90)
    assert (item["estado"], item["segundos"]) == ("ativo", 0)
    assert (item["apelido"], item["time"], item["cor"]) == ("op1", "Azul", servicos.TIMES["Azul"])


def test_r7_dispositivo_chega_normalizado(app, client, cabecalho_token):
    preparar(app)
    assert postar(client, sinal(dispositivo=" mt-01 "), cabecalho_token).status_code == 201


def test_r8_pacote_repetido_vale_uma_vez_e_nao_cria_posicao(app, client, cabecalho_token):
    operacao = preparar(app)
    assert postar(client, SINAL, cabecalho_token).status_code == 201
    repetido = postar(client, sinal(lat=-15.5, lon=-47.5, bateria=10), cabecalho_token)
    assert (repetido.status_code, repetido.get_json()) == (200, {"status": "duplicado"})
    item = inscrito(situacao(client, cabecalho_token, operacao))
    assert (item["lat"], item["lon"], item["bateria"]) == (-15.79, -47.88, 90)
    assert contar_posicoes(app, item["inscricao_id"]) == 1


def test_r8_pacote_novo_depois_do_duplicado_grava(app, client, cabecalho_token):
    preparar(app)
    for pacote, status in ((1, 201), (1, 200), (2, 201)):
        assert postar(client, sinal(pacote=pacote), cabecalho_token).status_code == status


def test_r8_o_mesmo_pacote_de_outro_dispositivo_nao_e_duplicado(app, client, cabecalho_token):
    preparar(app, dispositivos=("MT-01", "MT-02"))
    assert postar(client, sinal(dispositivo="MT-01"), cabecalho_token).status_code == 201
    assert postar(client, sinal(dispositivo="MT-02"), cabecalho_token).status_code == 201


def test_r9_estado_na_api_acompanha_o_relogio(app, client, cabecalho_token, relogio):
    operacao = preparar(app)
    postar(client, SINAL, cabecalho_token)
    esperado = [(60, "ativo", 60), (1, "atrasado", 61), (59, "atrasado", 120), (1, "perdido", 121)]
    for avanco, estado, segundos in esperado:
        relogio.avancar(avanco)
        item = inscrito(situacao(client, cabecalho_token, operacao))
        assert (item["estado"], item["segundos"]) == (estado, segundos)


def test_situacao_traz_o_rumo_do_ultimo_deslocamento(app, client, cabecalho_token, relogio):
    operacao = preparar(app)
    postar(client, sinal(pacote=1, lat=-15.0), cabecalho_token)
    assert inscrito(situacao(client, cabecalho_token, operacao))["rumo"] is None
    relogio.avancar(2)
    postar(client, sinal(pacote=2, lat=-14.999), cabecalho_token)     # um passo para o norte
    assert inscrito(situacao(client, cabecalho_token, operacao))["rumo"] == 0.0


# ------------------------------------------------------------------ GETs

@LEITORES
def test_situacao_sem_parametro_devolve_a_operacao_em_curso(app, ler):
    operacao = preparar(app)
    resposta = ler("/api/v1/situacao")
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados["operacao"]["id"] == operacao and dados["operacao"]["situacao"] == "em_curso"
    assert set(dados) == {"operacao", "descartados", "inscritos"}
    assert set(dados["inscritos"][0]) == {
        "inscricao_id", "apelido", "time", "cor", "classe", "dispositivo",
        "estado", "segundos", "lat", "lon", "bateria", "rumo"}
    assert dados["inscritos"][0]["estado"] == "sem_sinal"


@LEITORES
def test_situacao_com_parametro_aceita_operacao_fora_de_curso(app, ler):
    operacao = preparar(app, iniciar=False)
    resposta = ler(f"/api/v1/situacao?operacao={operacao}")
    assert resposta.status_code == 200
    assert resposta.get_json()["operacao"]["situacao"] == "planejada"


@LEITORES
def test_situacao_sem_operacao_em_curso_devolve_404(app, ler):
    preparar(app, iniciar=False)
    resposta = ler("/api/v1/situacao")
    assert resposta.status_code == 404
    assert resposta.get_json()["codigo"] == "sem_operacao_em_curso"


@pytest.mark.parametrize("valor", ["abc", "", "1.5", "1e3", "0x10"])
def test_situacao_com_operacao_que_nao_e_inteiro_devolve_400(client, cabecalho_token, valor):
    resposta = client.get(f"/api/v1/situacao?operacao={valor}", headers=cabecalho_token)
    assert resposta.status_code == 400
    dados = resposta.get_json()
    assert dados["codigo"] == "formato_invalido" and "'operacao'" in dados["erro"]


@pytest.mark.parametrize("valor", ["999", "0", "-1", "9" * 30])
def test_situacao_com_operacao_inexistente_devolve_404(client, cabecalho_token, valor):
    resposta = client.get(f"/api/v1/situacao?operacao={valor}", headers=cabecalho_token)
    assert resposta.status_code == 404
    assert resposta.get_json()["codigo"] == "operacao_inexistente"


@LEITORES
def test_operacoes_lista_as_operacoes(app, ler):
    assert ler("/api/v1/operacoes").get_json() == {"operacoes": []}
    operacao = preparar(app)
    lista = ler("/api/v1/operacoes").get_json()["operacoes"]
    assert [(o["id"], o["nome"], o["situacao"], o["inscritos"]) for o in lista] == [
        (operacao, "Operação Teste", "em_curso", 1)]


@pytest.mark.parametrize("url", ["/api/v1/situacao", "/api/v1/operacoes", "/api/v1/situacao?operacao=1"])
def test_r11_gets_sem_credencial_devolvem_401(client, url):
    resposta = client.get(url)
    assert resposta.status_code == 401
    assert resposta.get_json()["codigo"] == "nao_autorizado"


@pytest.mark.parametrize("url", ["/api/v1/situacao", "/api/v1/operacoes"])
def test_r11_gets_com_token_errado_ou_nao_configurado_devolvem_401(app, client, cabecalho_token, url):
    assert client.get(url, headers={"Authorization": "Bearer errado"}).status_code == 401
    app.config["MESHTRACKER_TOKEN"] = None
    assert client.get(url, headers=cabecalho_token).status_code == 401


def test_erros_da_api_sao_json_com_erro_e_codigo(client, cabecalho_token):
    for resposta in (client.get("/api/v1/nao-existe", headers=cabecalho_token),
                     client.get("/api/v1/sinais", headers=cabecalho_token),
                     postar(client, "[]", cabecalho_token), client.get("/api/v1/operacoes")):
        assert resposta.status_code in (400, 401, 404, 405)
        assert resposta.is_json and set(resposta.get_json()) == {"erro", "codigo"}


# ------------------------------------------------------------------ mapa

def test_mapa_usa_leaflet_e_dados_da_operacao_sem_script_inline(app, obs_client):
    operacao = preparar(app)
    resposta = obs_client.get(f"/operacoes/{operacao}/mapa")
    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    for esperado in (f'data-operacao-id="{operacao}"', 'data-url-situacao="/api/v1/situacao"',
                     "vendor/leaflet/leaflet.css", "css/mapa.css",
                     "vendor/leaflet/leaflet.js", "js/mapa.js"):
        assert esperado in html
    assert 'data-centro-lat="' in html and 'data-centro-lon="' in html
    assert not re.search(r"<script(?![^>]*\bsrc=)", html)       # a CSP não aceita script inline


def test_mapa_js_so_escreve_texto_do_servidor_por_textcontent(client):
    codigo = (RAIZ / "src/static/js/mapa.js").read_text(encoding="utf-8")
    assert not re.search(r"\.(innerHTML|outerHTML)\b|insertAdjacentHTML|document\.write", codigo)
    assert client.get("/static/js/mapa.js").status_code == 200
    assert client.get("/static/css/mapa.css").status_code == 200
