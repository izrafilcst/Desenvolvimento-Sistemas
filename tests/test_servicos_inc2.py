"""Testes de R7 a R9, rumo e usuários (Incremento 2); R1 a R6 estão em test_servicos.py.
Nomes: test_r7_..., test_r9_..., test_rumo_..., test_usuario_... Banco temporário e relógio injetado."""

import pytest
from werkzeug.security import check_password_hash

import servicos
from repositorio import Conflito
from servicos import ErroDeNegocio


def novo_operador(repo, relogio, apelido="alfa", nome=None):
    return servicos.cadastrar_operador(repo, apelido, nome or apelido.title(), relogio())


def nova_operacao(repo, nome="Operação 1", data="2026-11-10", local="Campo Norte"):
    return servicos.criar_operacao(repo, nome, data, local)


def inscrever(repo, operacao_id, operador_id, dispositivo="MT-01", time="Azul",
              classe="Fuzileiro", consentimento=True):
    return servicos.inscrever(repo, operacao_id, operador_id, time, classe,
                              dispositivo, consentimento)


def codigo_do_erro(funcao, *args, **kwargs):
    with pytest.raises(ErroDeNegocio) as erro:
        funcao(*args, **kwargs)
    return erro.value.codigo


# ------------------------------------------------------------ R7 e R8

def operacao_em_curso_com_inscrito(repo, relogio, dispositivo="MT-01", apelido="alfa"):
    """Operação em curso com um operador inscrito; devolve (operacao_id, inscricao_id)."""
    operacao = nova_operacao(repo)
    inscricao = inscrever(repo, operacao, novo_operador(repo, relogio, apelido), dispositivo)
    servicos.avancar_situacao(repo, operacao)
    return operacao, inscricao


def sinal(repo, relogio, dispositivo="MT-01", pacote=1, lat=-15.79, lon=-47.88, bateria=80.0):
    return servicos.receber_sinal(repo, dispositivo, pacote, lat, lon, bateria, relogio())


def todas_as_posicoes(conn):
    return conn.execute("SELECT COUNT(*) FROM posicao").fetchone()[0]


def todos_os_descartes(conn):
    linhas = conn.execute(
        "SELECT operacao_id, dispositivo, motivo, recebido_em FROM descarte ORDER BY id")
    return [tuple(linha) for linha in linhas]


def test_r7_sinal_de_dispositivo_inscrito_e_gravado_como_posicao(repo, relogio, conn):
    _, inscricao = operacao_em_curso_com_inscrito(repo, relogio)
    assert sinal(repo, relogio, pacote=7, lat=-15.8, lon=-47.9, bateria=55.5) == "gravado"
    (posicao,) = repo.ultimas_posicoes(inscricao)
    assert (posicao["pacote"], posicao["lat"], posicao["lon"], posicao["bateria"]) == (
        7, -15.8, -47.9, 55.5)
    assert posicao["recebido_em"] == relogio().isoformat()
    assert todos_os_descartes(conn) == []


def test_r7_sinal_de_dispositivo_sem_inscricao_e_descartado_e_contado(repo, relogio, conn):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    assert sinal(repo, relogio, dispositivo="MT-99") == "descartado"
    assert repo.contar_descartes(operacao) == 1
    assert todos_os_descartes(conn) == [
        (operacao, "MT-99", "sem_inscricao", relogio().isoformat())]
    assert todas_as_posicoes(conn) == 0


def test_r7_sinal_sem_operacao_em_curso_e_descartado_e_contado(repo, relogio, conn):
    operacao = nova_operacao(repo)
    inscrever(repo, operacao, novo_operador(repo, relogio), "MT-01")   # planejada, não em curso
    assert sinal(repo, relogio, dispositivo="MT-01") == "descartado"
    assert todos_os_descartes(conn) == [
        (None, "MT-01", "sem_operacao_em_curso", relogio().isoformat())]
    assert repo.contar_descartes(operacao) == 0
    assert todas_as_posicoes(conn) == 0


def test_r7_sinal_depois_do_encerramento_tambem_e_descartado(repo, relogio, conn):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    servicos.avancar_situacao(repo, operacao)
    assert sinal(repo, relogio) == "descartado"
    assert todas_as_posicoes(conn) == 0


def test_r7_inscricao_em_outra_operacao_nao_vale_para_a_operacao_em_curso(repo, relogio, conn):
    antiga = nova_operacao(repo, "Antiga")
    inscrever(repo, antiga, novo_operador(repo, relogio, "alfa"), "MT-01")
    servicos.avancar_situacao(repo, antiga)
    servicos.avancar_situacao(repo, antiga)
    atual, _ = operacao_em_curso_com_inscrito(repo, relogio, "MT-02", "bravo")
    assert sinal(repo, relogio, dispositivo="MT-01") == "descartado"
    assert repo.contar_descartes(atual) == 1
    assert todas_as_posicoes(conn) == 0


def test_r7_cada_sinal_descartado_e_contado(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    for pacote in (1, 2, 3):
        sinal(repo, relogio, dispositivo="MT-99", pacote=pacote)
    assert repo.contar_descartes(operacao) == 3


def test_r7_dispositivo_do_sinal_e_normalizado_como_na_inscricao(repo, relogio):
    _, inscricao = operacao_em_curso_com_inscrito(repo, relogio, "MT-01")
    assert sinal(repo, relogio, dispositivo=" mt-01 ") == "gravado"
    assert repo.contar_posicoes(inscricao) == 1


def test_r8_pacote_repetido_nao_cria_posicao_nova(repo, relogio):
    _, inscricao = operacao_em_curso_com_inscrito(repo, relogio)
    assert sinal(repo, relogio, pacote=5) == "gravado"
    assert sinal(repo, relogio, pacote=5) == "duplicado"
    assert repo.contar_posicoes(inscricao) == 1


def test_r8_o_duplicado_nao_altera_a_posicao_ja_gravada_nem_vira_descarte(repo, relogio, conn):
    _, inscricao = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio, pacote=5, lat=-15.8, lon=-47.9)
    sinal(repo, relogio, pacote=5, lat=-10.0, lon=-40.0)
    (posicao,) = repo.ultimas_posicoes(inscricao)
    assert (posicao["lat"], posicao["lon"]) == (-15.8, -47.9)
    assert todos_os_descartes(conn) == []


def test_r8_pacotes_diferentes_do_mesmo_dispositivo_sao_gravados(repo, relogio):
    _, inscricao = operacao_em_curso_com_inscrito(repo, relogio)
    assert [sinal(repo, relogio, pacote=p) for p in (1, 2, 3)] == ["gravado"] * 3
    assert repo.contar_posicoes(inscricao) == 3


def test_r8_o_mesmo_numero_de_pacote_vale_para_cada_dispositivo(repo, relogio):
    operacao, primeira = operacao_em_curso_com_inscrito(repo, relogio, "MT-01", "alfa")
    segunda = repo.inserir_inscricao(operacao, novo_operador(repo, relogio, "bravo"),
                                     "Verde", "Médico", "MT-02", True)
    assert sinal(repo, relogio, dispositivo="MT-01", pacote=1) == "gravado"
    assert sinal(repo, relogio, dispositivo="MT-02", pacote=1) == "gravado"
    assert (repo.contar_posicoes(primeira), repo.contar_posicoes(segunda)) == (1, 1)


def test_r8_o_mesmo_numero_de_pacote_vale_em_outra_operacao(repo, relogio):
    primeira, inscricao_1 = operacao_em_curso_com_inscrito(repo, relogio, "MT-01", "alfa")
    sinal(repo, relogio, pacote=1)
    servicos.avancar_situacao(repo, primeira)
    segunda = nova_operacao(repo, "Op 2")
    inscricao_2 = inscrever(repo, segunda, repo.listar_operadores()[0]["id"], "MT-01")
    servicos.avancar_situacao(repo, segunda)
    assert sinal(repo, relogio, pacote=1) == "gravado"
    assert (repo.contar_posicoes(inscricao_1), repo.contar_posicoes(inscricao_2)) == (1, 1)


def test_r8_o_banco_recusa_o_pacote_repetido_pelo_unique(repo, relogio):
    _, inscricao = operacao_em_curso_com_inscrito(repo, relogio)
    repo.inserir_posicao(inscricao, 1, -15.0, -47.0, 90.0, relogio().isoformat())
    with pytest.raises(Conflito) as erro:
        repo.inserir_posicao(inscricao, 1, -16.0, -48.0, 80.0, relogio().isoformat())
    assert erro.value.restricao == "posicao.pacote"
    assert repo.contar_posicoes(inscricao) == 1


def test_r8_ultimas_posicoes_vem_da_mais_recente_e_respeitam_o_limite(repo, relogio):
    _, inscricao = operacao_em_curso_com_inscrito(repo, relogio)
    for pacote in range(1, 6):
        sinal(repo, relogio, pacote=pacote)
    assert [p["pacote"] for p in repo.ultimas_posicoes(inscricao)] == [5, 4, 3, 2, 1]
    assert [p["pacote"] for p in repo.ultimas_posicoes(inscricao, limite=2)] == [5, 4]
    assert set(repo.ultimas_posicoes(inscricao)[0]) == {
        "id", "pacote", "lat", "lon", "bateria", "recebido_em"}


def test_r8_busca_da_inscricao_pelo_dispositivo_na_operacao(repo, relogio):
    operacao, inscricao = operacao_em_curso_com_inscrito(repo, relogio, "MT-01")
    assert repo.inscricao_por_dispositivo(operacao, "MT-01")["id"] == inscricao
    assert repo.inscricao_por_dispositivo(operacao, "MT-99") is None


# ------------------------------------------------------------------- R9

def situacao(repo, relogio, operacao, atrasado_s=60, perdido_s=120):
    return servicos.situacao_da_operacao(repo, operacao, relogio(), atrasado_s, perdido_s)


@pytest.mark.parametrize("segundos, esperado", [
    (None, "sem_sinal"),
    (0, "ativo"),
    (59, "ativo"),
    (60, "ativo"),
    (61, "atrasado"),
    (119, "atrasado"),
    (120, "atrasado"),
    (121, "perdido"),
    (3600, "perdido"),
])
def test_r9_estado_por_tempo_com_limites_padrao(segundos, esperado):
    assert servicos.estado_por_tempo(segundos, 60, 120) == esperado


@pytest.mark.parametrize("segundos, esperado", [
    (None, "sem_sinal"),
    (10, "ativo"),
    (11, "atrasado"),
    (25, "atrasado"),
    (26, "perdido"),
])
def test_r9_estado_por_tempo_com_limites_configurados_10_e_25(segundos, esperado):
    assert servicos.estado_por_tempo(segundos, 10, 25) == esperado


@pytest.mark.parametrize("segundos, esperado", [
    (300, "ativo"),
    (301, "atrasado"),
    (900, "atrasado"),
    (901, "perdido"),
])
def test_r9_estado_por_tempo_com_limites_configurados_300_e_900(segundos, esperado):
    assert servicos.estado_por_tempo(segundos, 300, 900) == esperado


def test_r9_estados_do_modulo_cobrem_o_que_a_funcao_devolve():
    devolvidos = {servicos.estado_por_tempo(s, 60, 120) for s in (None, 0, 61, 121)}
    assert devolvidos == set(servicos.ESTADOS)


def test_r9_inscrito_que_nunca_enviou_sinal_esta_sem_sinal(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    (inscrito,) = situacao(repo, relogio, operacao)["inscritos"]
    assert inscrito["estado"] == "sem_sinal"
    assert inscrito["segundos"] is None
    assert (inscrito["lat"], inscrito["lon"], inscrito["bateria"], inscrito["rumo"]) == (
        None, None, None, None)


@pytest.mark.parametrize("passados, esperado", [
    (59, "ativo"),
    (60, "ativo"),
    (61, "atrasado"),
    (119, "atrasado"),
    (120, "atrasado"),
    (121, "perdido"),
])
def test_r9_situacao_da_operacao_com_relogio_injetado(repo, relogio, passados, esperado):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio)
    relogio.avancar(passados)
    (inscrito,) = situacao(repo, relogio, operacao)["inscritos"]
    assert inscrito["segundos"] == passados
    assert inscrito["estado"] == esperado


@pytest.mark.parametrize("passados, esperado", [
    (10, "ativo"),
    (11, "atrasado"),
    (20, "atrasado"),
    (21, "perdido"),
])
def test_r9_situacao_da_operacao_com_limites_10_e_20(repo, relogio, passados, esperado):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio)
    relogio.avancar(passados)
    (inscrito,) = situacao(repo, relogio, operacao, atrasado_s=10, perdido_s=20)["inscritos"]
    assert inscrito["estado"] == esperado


def test_r9_um_sinal_novo_volta_o_estado_para_ativo(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio, pacote=1)
    relogio.avancar(130)
    assert situacao(repo, relogio, operacao)["inscritos"][0]["estado"] == "perdido"
    sinal(repo, relogio, pacote=2)
    relogio.avancar(5)
    inscrito = situacao(repo, relogio, operacao)["inscritos"][0]
    assert (inscrito["estado"], inscrito["segundos"]) == ("ativo", 5)


def test_r9_segundos_e_a_parte_inteira_do_tempo_desde_o_ultimo_sinal(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio)
    relogio.avancar(59.9)
    (inscrito,) = situacao(repo, relogio, operacao)["inscritos"]
    assert inscrito["segundos"] == 59
    assert isinstance(inscrito["segundos"], int)


def test_r9_relogio_atras_do_ultimo_sinal_nao_gera_segundos_negativos(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio)
    relogio.avancar(-5)
    (inscrito,) = situacao(repo, relogio, operacao)["inscritos"]
    assert (inscrito["segundos"], inscrito["estado"]) == (0, "ativo")


def test_r9_cada_inscrito_tem_o_seu_estado(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio, "MT-01", "alfa")
    repo.inserir_inscricao(operacao, novo_operador(repo, relogio, "bravo"),
                           "Verde", "Médico", "MT-02", True)
    sinal(repo, relogio, dispositivo="MT-01")
    relogio.avancar(90)
    sinal(repo, relogio, dispositivo="MT-02")
    relogio.avancar(40)
    por_apelido = {i["apelido"]: i for i in situacao(repo, relogio, operacao)["inscritos"]}
    assert (por_apelido["alfa"]["segundos"], por_apelido["alfa"]["estado"]) == (130, "perdido")
    assert (por_apelido["bravo"]["segundos"], por_apelido["bravo"]["estado"]) == (40, "ativo")


def test_r9_situacao_traz_a_operacao_os_descartados_e_os_dados_do_inscrito(repo, relogio):
    operacao, inscricao = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio, pacote=1, lat=-15.8, lon=-47.9, bateria=77.0)
    sinal(repo, relogio, dispositivo="MT-99")
    resultado = situacao(repo, relogio, operacao)
    assert set(resultado) == {"operacao", "descartados", "inscritos"}
    assert resultado["operacao"] == servicos.obter_operacao(repo, operacao)
    assert resultado["descartados"] == 1
    assert resultado["inscritos"] == [{
        "inscricao_id": inscricao, "apelido": "alfa", "time": "Azul",
        "cor": servicos.TIMES["Azul"], "classe": "Fuzileiro", "dispositivo": "MT-01",
        "estado": "ativo", "segundos": 0, "lat": -15.8, "lon": -47.9, "bateria": 77.0,
        "rumo": None}]


def test_r9_situacao_de_operacao_inexistente(repo, relogio):
    assert codigo_do_erro(situacao, repo, relogio, 999) == "operacao_inexistente"


def test_r9_situacao_em_curso_e_none_quando_nao_ha_operacao_em_curso(repo, relogio):
    nova_operacao(repo)
    assert servicos.situacao_em_curso(repo, relogio(), 60, 120) is None


def test_r9_situacao_em_curso_devolve_a_operacao_em_curso(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    sinal(repo, relogio)
    relogio.avancar(61)
    resultado = servicos.situacao_em_curso(repo, relogio(), 60, 120)
    assert resultado["operacao"]["id"] == operacao
    assert resultado["inscritos"][0]["estado"] == "atrasado"


# ------------------------------------------------------------------ rumo

@pytest.mark.parametrize("destino, esperado", [
    ((1.0, 0.0), 0.0),      # norte
    ((0.0, 1.0), 90.0),     # leste
    ((-1.0, 0.0), 180.0),   # sul
    ((0.0, -1.0), 270.0),   # oeste
    ((1.0, 1.0), 45.0),     # nordeste, no equador
    ((-1.0, -1.0), 225.0),  # sudoeste, no equador
])
def test_rumo_dos_pontos_cardeais(destino, esperado):
    assert servicos.calcular_rumo(0.0, 0.0, *destino) == pytest.approx(esperado, abs=0.1)


def test_rumo_de_pontos_iguais_e_none():
    assert servicos.calcular_rumo(-15.79, -47.88, -15.79, -47.88) is None


def test_rumo_de_nova_york_a_londres_confere_com_o_valor_conhecido():
    rumo = servicos.calcular_rumo(40.7128, -74.0060, 51.5074, -0.1278)
    assert rumo == pytest.approx(51.2, abs=0.2)


def test_rumo_tem_uma_casa_decimal():
    rumo = servicos.calcular_rumo(-15.7939, -47.8828, -23.5505, -46.6333)
    assert rumo == round(rumo, 1)
    assert 170 < rumo < 180


def test_rumo_nunca_chega_a_360():
    rumo = servicos.calcular_rumo(0.0, 0.0, 1.0, -0.0001)   # um fio a oeste do norte
    assert rumo == 0.0
    assert 0.0 <= servicos.calcular_rumo(0.0, 0.0, 1.0, -0.5) < 360.0


def enviar_trajeto(repo, relogio, pontos, dispositivo="MT-01"):
    for pacote, (lat, lon) in enumerate(pontos, start=1):
        sinal(repo, relogio, dispositivo=dispositivo, pacote=pacote, lat=lat, lon=lon)
        relogio.avancar(1)


def test_rumo_da_situacao_sai_das_duas_ultimas_posicoes_distintas(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    enviar_trajeto(repo, relogio, [(0.0, 0.0), (0.0, 1.0)])   # foi para o leste
    (inscrito,) = situacao(repo, relogio, operacao)["inscritos"]
    assert inscrito["rumo"] == pytest.approx(90.0, abs=0.1)


def test_rumo_continua_o_ultimo_quando_o_operador_parou(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    enviar_trajeto(repo, relogio, [(0.0, 0.0), (1.0, 0.0), (1.0, 0.0), (1.0, 0.0)])
    (inscrito,) = situacao(repo, relogio, operacao)["inscritos"]
    assert inscrito["rumo"] == pytest.approx(0.0, abs=0.1)   # último movimento: norte


def test_rumo_usa_so_o_par_mais_recente_quando_mudou_de_direcao(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    enviar_trajeto(repo, relogio, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])   # norte, depois leste
    (inscrito,) = situacao(repo, relogio, operacao)["inscritos"]
    assert inscrito["rumo"] == pytest.approx(90.0, abs=0.5)


def test_rumo_e_none_com_uma_so_posicao(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    enviar_trajeto(repo, relogio, [(0.0, 0.0)])
    assert situacao(repo, relogio, operacao)["inscritos"][0]["rumo"] is None


def test_rumo_e_none_quando_todas_as_posicoes_sao_iguais(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    enviar_trajeto(repo, relogio, [(0.0, 0.0)] * 4)
    assert situacao(repo, relogio, operacao)["inscritos"][0]["rumo"] is None


def test_rumo_olha_so_as_dez_ultimas_posicoes(repo, relogio):
    operacao, _ = operacao_em_curso_com_inscrito(repo, relogio)
    enviar_trajeto(repo, relogio, [(0.0, 0.0)] + [(1.0, 0.0)] * 10)   # só a primeira é diferente
    assert situacao(repo, relogio, operacao)["inscritos"][0]["rumo"] is None


# --------------------------------------------------------------- usuarios

SENHA = "senha-de-teste-123"


def test_usuario_cria_com_senha_em_hash_e_nao_em_texto(repo, conn):
    usuario_id = servicos.criar_usuario(repo, "org", SENHA, "organizador")
    gravado = repo.buscar_usuario_por_id(usuario_id)
    assert gravado["login"] == "org"
    assert gravado["papel"] == "organizador"
    assert gravado["senha_hash"] != SENHA
    assert SENHA not in gravado["senha_hash"]
    assert check_password_hash(gravado["senha_hash"], SENHA)
    bruto = conn.execute("SELECT senha_hash FROM usuario WHERE id = ?", (usuario_id,)).fetchone()
    assert SENHA not in bruto[0]


def test_usuario_busca_por_login_devolve_dict_ou_none(repo):
    usuario_id = servicos.criar_usuario(repo, "obs", SENHA, "observador")
    encontrado = repo.buscar_usuario_por_login("obs")
    assert isinstance(encontrado, dict)
    assert set(encontrado) == {"id", "login", "senha_hash", "papel"}
    assert encontrado["id"] == usuario_id
    assert repo.buscar_usuario_por_login("nao-existe") is None
    assert repo.buscar_usuario_por_id(999) is None


def test_usuario_login_repetido_e_recusado(repo):
    servicos.criar_usuario(repo, "org", SENHA, "organizador")
    assert codigo_do_erro(servicos.criar_usuario, repo, "org", SENHA, "observador") == (
        "login_duplicado")


def test_usuario_o_banco_recusa_login_repetido_pelo_unique(repo):
    repo.inserir_usuario("org", "hash", "organizador")
    with pytest.raises(Conflito) as erro:
        repo.inserir_usuario("org", "outro-hash", "observador")
    assert erro.value.restricao == "usuario.login"


@pytest.mark.parametrize("login", ["ab", "a" * 33, "Org", "com espaco", "acentuação", "a@b.com", ""])
def test_usuario_login_invalido(repo, login):
    assert codigo_do_erro(servicos.criar_usuario, repo, login, SENHA, "organizador") == (
        "dados_invalidos")


@pytest.mark.parametrize("login", ["abc", "a" * 32, "org.1", "obs_2", "a-b"])
def test_usuario_login_valido(repo, login):
    assert servicos.criar_usuario(repo, login, SENHA, "observador") > 0


def test_usuario_senha_curta_e_recusada(repo):
    assert codigo_do_erro(servicos.criar_usuario, repo, "org", "1234567", "organizador") == (
        "dados_invalidos")
    assert servicos.criar_usuario(repo, "org", "12345678", "organizador") > 0


def test_usuario_papel_fora_da_lista_e_recusado(repo):
    assert codigo_do_erro(servicos.criar_usuario, repo, "org", SENHA, "admin") == (
        "papel_invalido")
    assert repo.buscar_usuario_por_login("org") is None


def test_usuario_autentica_com_login_e_senha_certos(repo):
    usuario_id = servicos.criar_usuario(repo, "org", SENHA, "organizador")
    assert servicos.autenticar(repo, "org", SENHA) == {
        "id": usuario_id, "login": "org", "papel": "organizador"}


def test_usuario_nao_autentica_com_senha_errada_ou_login_desconhecido(repo):
    servicos.criar_usuario(repo, "org", SENHA, "organizador")
    assert servicos.autenticar(repo, "org", "senha-errada-123") is None
    assert servicos.autenticar(repo, "ninguem", SENHA) is None
    assert servicos.autenticar(repo, "", "") is None
