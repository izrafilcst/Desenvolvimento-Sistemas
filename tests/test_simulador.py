"""Simulador de operadores (src/simulador.py): lógica pura, laço, linha de comando e uma
passada contra a API de verdade. Só o último teste usa as regras reais (R6 a R9);
os demais não dependem de servicos.py nem de rede.
"""

import http.server
import math
import random
import re
import threading
from contextlib import contextmanager
from urllib.parse import urlparse

import pytest

import api
import db
import servicos
import simulador

CENTRO = (-15.7939, -47.8828)
SINAL = {"dispositivo": "MT-01", "pacote": 1, "lat": -15.79, "lon": -47.88, "bateria": 90}


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


def percurso(semente, ticks, dt=2.0, raio=simulador.RAIO_M):
    rng = random.Random(semente)
    op = simulador.novo_operador("MT-01", rng)
    trilha = [op]
    for _ in range(ticks):
        op = simulador.mover(op, rng, dt, raio)
        trilha.append(op)
    return trilha


def test_simulador_fica_no_raio_de_300m_em_2000_ticks():
    for semente in (1, 2, 3):
        distancias = [math.hypot(op.x, op.y) for op in percurso(semente, 2000)]
        assert max(distancias) <= 300.0
        assert max(distancias) > 30       # e anda de verdade: não ficou parado perto do centro


def test_simulador_o_mesmo_percurso_se_repete_com_a_mesma_semente():
    assert percurso(42, 100) == percurso(42, 100)
    assert percurso(42, 100) != percurso(43, 100)


def test_simulador_rumo_muda_com_desvio_perto_de_30_graus():
    trilha = percurso(7, 3000, raio=1e9)              # raio enorme: sem viradas na borda
    giros = [((b.rumo - a.rumo + 180) % 360) - 180 for a, b in zip(trilha, trilha[1:])]
    media = sum(giros) / len(giros)
    desvio = math.sqrt(sum((g - media) ** 2 for g in giros) / len(giros))
    assert all(g != 0 for g in giros)
    assert 27 < desvio < 33 and abs(media) < 3


def test_simulador_velocidade_fica_entre_0_5_e_2_5_m_por_s_e_10_por_cento_parado():
    trilha = percurso(11, 5000, dt=2.0, raio=1e9)
    passos = [math.hypot(b.x - a.x, b.y - a.y) / 2.0 for a, b in zip(trilha, trilha[1:])]
    parados = [p for p in passos if p == 0]
    andando = [p for p in passos if p > 0]
    assert 0.07 < len(parados) / len(passos) < 0.13
    assert min(andando) >= 0.5 - 1e-9 and max(andando) <= 2.5 + 1e-9


class RngFixo:
    """Gerador sem sorte: gauss(0, s) = 0, nunca fica parado, sempre a velocidade máxima."""
    def gauss(self, media, desvio): return 0.0
    def random(self): return 0.5
    def uniform(self, a, b): return b


def test_simulador_na_borda_vira_para_dentro_sem_sair():
    op = simulador.Operador("MT-01", 299.0, 0.0, 90.0, 80.0, 0)      # perto da borda, indo para leste
    novo = simulador.mover(op, RngFixo(), dt=2.0)                    # 5 m para leste sairiam do raio
    assert math.hypot(novo.x, novo.y) < math.hypot(op.x, op.y)
    assert novo.rumo == pytest.approx(270.0)                         # virou para o centro (oeste)
    assert novo.x == pytest.approx(294.0)


def test_simulador_rumo_para_o_centro_nos_quatro_cantos():
    assert simulador.rumo_para_o_centro(0, 100) == pytest.approx(180)    # ao norte do centro: vai para o sul
    assert simulador.rumo_para_o_centro(100, 0) == pytest.approx(270)
    assert simulador.rumo_para_o_centro(0, -100) == pytest.approx(0)
    assert simulador.rumo_para_o_centro(-100, 0) == pytest.approx(90)


def test_simulador_converte_metros_em_lat_lon():
    lat, lon = simulador.para_lat_lon(CENTRO, 0, 0)
    assert (lat, lon) == CENTRO
    lat, _ = simulador.para_lat_lon(CENTRO, 0, 111.32)
    assert lat - CENTRO[0] == pytest.approx(0.001)
    _, lon = simulador.para_lat_lon(CENTRO, 111.32 * math.cos(math.radians(CENTRO[0])), 0)
    assert lon - CENTRO[1] == pytest.approx(0.001)


def test_simulador_reenvio_acontece_em_cerca_de_10_por_cento():
    rng = random.Random(5)
    taxa = sum(simulador.deve_reenviar(rng) for _ in range(20000)) / 20000
    assert 0.09 < taxa < 0.11
    assert simulador.deve_reenviar(rng, probabilidade=0) is False
    assert simulador.deve_reenviar(rng, probabilidade=1.1) is True


def test_simulador_bateria_comeca_entre_70_e_100_e_so_cai():
    rng = random.Random(9)
    inicial = [simulador.novo_operador(f"MT-0{i}", rng).bateria for i in range(1, 50)]
    assert all(70 <= b <= 100 for b in inicial)
    bateria = 75.0
    for _ in range(3000):
        nova = simulador.descarregar(bateria, rng)
        assert 0 <= nova <= bateria
        bateria = nova
    assert 0 <= bateria < 75


def test_simulador_parar_corta_o_dispositivo_depois_de_n_segundos():
    assert simulador.ainda_enviando("MT-03", "MT-03", 20, 19.9)
    assert not simulador.ainda_enviando("MT-03", "MT-03", 20, 20)
    assert simulador.ainda_enviando("MT-01", "MT-03", 20, 500)
    assert simulador.ainda_enviando("MT-03", None, 20, 500)


def test_simulador_sinal_montado_respeita_o_contrato_do_post():
    op = simulador.Operador("MT-01", 100.0, 50.0, 10.0, 88.88, 4)
    corpo = simulador.montar_sinal(op, CENTRO)
    assert set(corpo) == set(SINAL) and corpo["pacote"] == 4 and corpo["bateria"] == 88.9
    assert api.validar_sinal(corpo) == corpo            # a API aceita o que o simulador manda


class Mundo:
    """Servidor, relógio e tela falsos para rodar o simulador sem rede nem espera."""
    def __init__(self):
        self.vistos, self.enviados, self.linhas, self.t = set(), [], [], 0.0

    def enviar(self, url, token, sinal):
        chave = (sinal["dispositivo"], sinal["pacote"])
        self.enviados.append(sinal)
        if chave in self.vistos:
            return 200, {"status": "duplicado"}
        self.vistos.add(chave)
        return 201, {"status": "gravado"}

    def dormir(self, segundos):
        self.t += segundos

    def agora(self):
        return self.t

    def rodar(self, ticks, dispositivos=("MT-01", "MT-02", "MT-03"), enviar=None, **extra):
        cfg = simulador.Configuracao("http://x", "t", list(dispositivos), CENTRO, ticks=ticks, **extra)
        simulador.rodar(cfg, random.Random(3), enviar or self.enviar, self.dormir, self.agora, self.linhas.append)


def test_simulador_envia_pacotes_crescentes_e_reenvia_o_anterior_em_10_por_cento():
    mundo = Mundo()
    mundo.rodar(500)
    ultimo_novo, reenvios = {}, 0
    for s in mundo.enviados:                      # na ordem em que o servidor recebeu
        d = s["dispositivo"]
        if s["pacote"] <= ultimo_novo.get(d, 0):
            assert s["pacote"] == ultimo_novo[d] - 1      # reenvio: o pacote anterior ao último novo
            reenvios += 1
        else:
            assert s["pacote"] == ultimo_novo.get(d, 0) + 1     # pacote novo: sempre o próximo
            ultimo_novo[d] = s["pacote"]
    assert ultimo_novo == {"MT-01": 500, "MT-02": 500, "MT-03": 500}
    assert 0.07 < reenvios / (500 * 3) < 0.13


def test_simulador_escreve_uma_linha_por_envio_com_hora_dispositivo_pacote_e_status():
    mundo = Mundo()
    mundo.rodar(30, dispositivos=("MT-01",))
    padrao = re.compile(r"^\d\d:\d\d:\d\d MT-01 pacote \d+ -> (201 gravado|200 duplicado)$")
    assert len(mundo.linhas) == len(mundo.enviados) >= 30
    assert all(padrao.match(linha) for linha in mundo.linhas)


def test_simulador_parar_e_apos_calam_o_dispositivo_no_tempo_certo():
    mundo = Mundo()
    mundo.rodar(30, parar="MT-03", apos=20)         # ticks a cada 2 s: o MT-03 envia nos ticks de 0 a 18 s
    assert max(s["pacote"] for s in mundo.enviados if s["dispositivo"] == "MT-03") == 10
    assert max(s["pacote"] for s in mundo.enviados if s["dispositivo"] == "MT-01") == 30
    assert sum("MT-03 parou de enviar" in linha for linha in mundo.linhas) == 1


def test_simulador_erro_de_rede_nao_derruba_o_laco():
    mundo = Mundo()
    mundo.rodar(5, dispositivos=("MT-01",),
                enviar=lambda url, token, sinal: (None, {"erro": "erro de rede: recusou"}))
    assert len(mundo.linhas) == 5
    assert all(linha.endswith("-> erro de rede: recusou") for linha in mundo.linhas)


@contextmanager
def servidor_http(resposta):
    """http.server em thread no 127.0.0.1. `resposta(handler)` responde; `recebidos` guarda
    (método, caminho, cabeçalhos) de cada pedido. Devolve (porta, recebidos)."""
    recebidos = []

    class Tratador(http.server.BaseHTTPRequestHandler):
        def _tratar(self):
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            recebidos.append((self.command, self.path, dict(self.headers)))
            resposta(self)

        do_GET = do_POST = _tratar

        def log_message(self, *args):
            pass

    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Tratador)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        yield servidor.server_address[1], recebidos
    finally:
        servidor.shutdown()
        servidor.server_close()


@pytest.mark.parametrize("metodo, corpo", [("GET", None), ("POST", SINAL)])
def test_simulador_nao_segue_redirecionamento(metodo, corpo):
    def vazio(h):
        h.send_response(200)
        h.send_header("Content-Length", "0")
        h.end_headers()

    with servidor_http(vazio) as (porta_alvo, no_alvo):
        def redirecionar(h):
            h.send_response(302)
            h.send_header("Location", f"http://127.0.0.1:{porta_alvo}/roubo")
            h.send_header("Content-Length", "0")
            h.end_headers()

        with servidor_http(redirecionar) as (porta, recebidos):
            status, dados = simulador.chamar(metodo, f"http://127.0.0.1:{porta}/api/v1/x", "segredo", corpo, timeout=3)
    assert (status, dados) == (302, {})
    assert len(recebidos) == 1 and recebidos[0][2]["Authorization"] == "Bearer segredo"
    assert no_alvo == []                       # o token nunca chegou ao host do Location


def test_simulador_chamar_sem_servidor_devolve_none_em_vez_de_levantar():
    status, corpo = simulador.chamar("POST", "http://127.0.0.1:9/api/v1/sinais", "t", SINAL, timeout=2)
    assert status is None and "erro de rede" in corpo["erro"]
    assert simulador.chamar("GET", "isto-nao-e-url", "t")[0] is None


def situacao_falsa(monkeypatch, status=200, corpo=None):
    chamadas = []

    def chamar(metodo, url, token, corpo_enviado=None, timeout=5.0):
        chamadas.append((metodo, url, token))
        return status, corpo or {}

    monkeypatch.setattr(simulador, "chamar", chamar)
    return chamadas


def test_simulador_sem_operacao_em_curso_avisa_e_sai_com_1(monkeypatch, capsys):
    situacao_falsa(monkeypatch, 404, {"erro": "Não há operação em curso.", "codigo": "sem_operacao_em_curso"})
    assert simulador.main(["--token", "t", "--url", "http://x"]) == 1
    assert "operação em curso" in capsys.readouterr().err


@pytest.mark.parametrize("status, corpo, trecho", [
    (401, {"codigo": "nao_autorizado"}, "token"), (None, {"erro": "erro de rede: recusou"}, "recusou")])
def test_simulador_outros_problemas_tambem_saem_com_1_e_mensagem(monkeypatch, capsys, status, corpo, trecho):
    situacao_falsa(monkeypatch, status, corpo)
    assert simulador.main(["--token", "t", "--url", "http://x"]) == 1
    assert trecho in capsys.readouterr().err


def test_simulador_sem_token_nem_variavel_sai_com_1(monkeypatch, capsys):
    monkeypatch.delenv("MESHTRACKER_TOKEN", raising=False)
    assert simulador.main(["--url", "http://x"]) == 1
    assert "MESHTRACKER_TOKEN" in capsys.readouterr().err


def test_simulador_url_que_nao_e_http_e_recusada(monkeypatch, capsys):
    chamadas = situacao_falsa(monkeypatch)
    assert simulador.main(["--token", "t", "--url", "file:///etc/passwd"]) == 1
    assert chamadas == []


def test_simulador_le_token_e_centro_e_monta_a_configuracao(monkeypatch):
    monkeypatch.setenv("MESHTRACKER_TOKEN", "do-ambiente")
    operacao = {"operacao": {"centro_lat": -10.5, "centro_lon": -45.25}}
    chamadas = situacao_falsa(monkeypatch, 200, operacao)
    recebidas = []
    monkeypatch.setattr(simulador, "rodar", lambda cfg, rng: recebidas.append(cfg))
    argv = ["--url", "http://127.0.0.1:5000/", "--dispositivos", "mt-01,MT-02", " MT-03", "mt-01",
            "--parar", "mt-03", "--apos", "5", "--semente", "1", "--pacote-inicial", "100"]
    assert simulador.main(argv) == 0
    assert chamadas == [("GET", "http://127.0.0.1:5000/api/v1/situacao", "do-ambiente")]
    cfg = recebidas[0]
    assert (cfg.centro, cfg.dispositivos, cfg.parar, cfg.apos) == ((-10.5, -45.25), ["MT-01", "MT-02", "MT-03"], "MT-03", 5)
    assert (cfg.intervalo, cfg.pacote_inicial, cfg.token) == (2.0, 100, "do-ambiente")


def test_simulador_dispositivos_padrao_sao_mt01_a_mt05_e_mt99():
    assert simulador.DISPOSITIVOS_PADRAO == ["MT-01", "MT-02", "MT-03", "MT-04", "MT-05", "MT-99"]


def test_simulador_contra_a_api_inscrito_aparece_e_mt99_e_descartado(
        app, client, cabecalho_token, monkeypatch, capsys):
    operacao = preparar(app)

    def chamar(metodo, url, token, corpo=None, timeout=5.0):
        resposta = client.open(urlparse(url).path, method=metodo, json=corpo,
                               headers={"Authorization": f"Bearer {token}"})
        return resposta.status_code, resposta.get_json() or {}

    monkeypatch.setattr(simulador, "chamar", chamar)
    token = cabecalho_token["Authorization"].split()[1]
    argv = ["--url", "http://teste", "--token", token, "--dispositivos", "MT-01", "MT-99",
            "--ticks", "5", "--intervalo", "0.01", "--semente", "1"]
    assert simulador.main(argv) == 0
    saida = capsys.readouterr().out
    assert re.search(r"MT-01 pacote \d+ -> 201 gravado", saida)
    assert re.search(r"MT-99 pacote \d+ -> 202 descartado", saida)
    dados = situacao(client, cabecalho_token, operacao)
    assert dados["descartados"] >= 5
    item = inscrito(dados)
    assert item["estado"] == "ativo" and item["lat"] is not None
    assert abs(item["lat"] - dados["operacao"]["centro_lat"]) < 0.01
