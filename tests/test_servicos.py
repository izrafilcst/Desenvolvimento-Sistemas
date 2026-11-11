"""Testes de servicos.py e repositorio.py: US01, US02 e as regras R1 a R6 (Incremento 1).

Nomes começam pela regra: test_r1_..., test_r6_... As regras R7 a R9, o rumo e os
usuários estão em test_servicos_inc2.py. Cada teste usa um banco SQLite temporário
(fixtures conn e repo) e o relógio injetado.
"""

import sqlite3

import pytest

import servicos
from repositorio import Conflito
from servicos import ErroDeNegocio


# ------------------------------------------------------------------ apoio

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


# --------------------------------------------------- US01 e US02: cadastros

def test_us01_cadastra_operador_e_lista_em_ordem_de_apelido(repo, relogio):
    novo_operador(repo, relogio, "zulu")
    novo_operador(repo, relogio, "alfa")
    operadores = servicos.listar_operadores(repo)
    assert [o["apelido"] for o in operadores] == ["alfa", "zulu"]
    assert operadores[0]["criado_em"] == relogio().isoformat()
    assert set(operadores[0]) == {"id", "apelido", "nome", "criado_em"}


def test_us01_apelido_repetido_sem_diferenciar_maiusculas(repo, relogio):
    novo_operador(repo, relogio, "Alfa")
    assert codigo_do_erro(novo_operador, repo, relogio, "ALFA") == "apelido_duplicado"
    assert len(servicos.listar_operadores(repo)) == 1


@pytest.mark.parametrize("apelido, nome", [
    ("", "Nome"),
    (" alfa", "Nome"),
    ("alfa ", "Nome"),
    ("a" * 33, "Nome"),
    ("alfa", ""),
    ("alfa", " Nome"),
    ("alfa", "n" * 101),
])
def test_us01_dados_invalidos_do_operador(repo, relogio, apelido, nome):
    codigo = codigo_do_erro(servicos.cadastrar_operador, repo, apelido, nome, relogio())
    assert codigo == "dados_invalidos"
    assert servicos.listar_operadores(repo) == []


def test_us01_aceita_apelido_e_nome_nos_limites(repo, relogio):
    servicos.cadastrar_operador(repo, "a" * 32, "n" * 100, relogio())
    assert len(servicos.listar_operadores(repo)) == 1


def test_us02_cria_operacao_planejada_com_centro_padrao(repo):
    operacao_id = nova_operacao(repo)
    operacao = servicos.obter_operacao(repo, operacao_id)
    assert operacao["situacao"] == "planejada"
    assert (operacao["centro_lat"], operacao["centro_lon"]) == servicos.CENTRO_PADRAO
    assert set(operacao) == {"id", "nome", "data", "local", "situacao",
                             "centro_lat", "centro_lon"}


def test_us02_cria_operacao_com_centro_informado(repo):
    operacao_id = servicos.criar_operacao(repo, "Op", "2026-12-01", "Local", -23.5, -46.6)
    operacao = servicos.obter_operacao(repo, operacao_id)
    assert (operacao["centro_lat"], operacao["centro_lon"]) == (-23.5, -46.6)


@pytest.mark.parametrize("nome, data, local, lat, lon", [
    ("", "2026-11-10", "Local", None, None),
    ("Op", "10/11/2026", "Local", None, None),
    ("Op", "2026-02-30", "Local", None, None),
    ("Op", "2026-11-10", "", None, None),
    ("o" * 101, "2026-11-10", "Local", None, None),
    ("Op", "2026-11-10", "Local", 91.0, 0.0),
    ("Op", "2026-11-10", "Local", 0.0, -180.5),
])
def test_us02_dados_invalidos_da_operacao(repo, nome, data, local, lat, lon):
    codigo = codigo_do_erro(servicos.criar_operacao, repo, nome, data, local, lat, lon)
    assert codigo == "dados_invalidos"
    assert servicos.listar_operacoes(repo) == []


def test_us02_lista_operacoes_da_mais_recente_com_contagem_de_inscritos(repo, relogio):
    antiga = servicos.criar_operacao(repo, "Antiga", "2026-10-01", "A")
    recente = servicos.criar_operacao(repo, "Recente", "2026-11-10", "B")
    operador = novo_operador(repo, relogio)
    inscrever(repo, recente, operador)
    operacoes = servicos.listar_operacoes(repo)
    assert [o["id"] for o in operacoes] == [recente, antiga]
    assert [o["inscritos"] for o in operacoes] == [1, 0]


def test_us02_operacao_inexistente(repo):
    assert codigo_do_erro(servicos.obter_operacao, repo, 999) == "operacao_inexistente"


# ------------------------------------------------------------- R1 a R5

def test_r1_operador_ja_cadastrado_se_inscreve_em_nova_operacao_sem_novo_cadastro(repo, relogio):
    operador = novo_operador(repo, relogio)
    op1, op2 = nova_operacao(repo, "Op 1"), nova_operacao(repo, "Op 2")
    inscrever(repo, op1, operador, "MT-01", "Azul", "Fuzileiro")
    inscrever(repo, op2, operador, "MT-01", "Vermelho", "Médico")
    assert len(servicos.listar_operadores(repo)) == 1
    assert servicos.listar_inscritos(repo, op1)[0]["time"] == "Azul"
    assert servicos.listar_inscritos(repo, op2)[0]["time"] == "Vermelho"


def test_r1_operador_inexistente_nao_e_inscrito(repo):
    operacao = nova_operacao(repo)
    assert codigo_do_erro(inscrever, repo, operacao, 999) == "operador_inexistente"


def test_r1_operacao_inexistente_nao_recebe_inscricao(repo, relogio):
    operador = novo_operador(repo, relogio)
    assert codigo_do_erro(inscrever, repo, 999, operador) == "operacao_inexistente"


def test_r2_inscricao_repetida_na_mesma_operacao_e_recusada(repo, relogio):
    operador = novo_operador(repo, relogio)
    operacao = nova_operacao(repo)
    inscrever(repo, operacao, operador, "MT-01")
    codigo = codigo_do_erro(inscrever, repo, operacao, operador, "MT-02", "Verde")
    assert codigo == "inscricao_duplicada"
    assert len(servicos.listar_inscritos(repo, operacao)) == 1


def test_r2_o_banco_recusa_a_inscricao_repetida_pelo_unique(repo, relogio, conn):
    operador = novo_operador(repo, relogio)
    operacao = nova_operacao(repo)
    repo.inserir_inscricao(operacao, operador, "Azul", "Fuzileiro", "MT-01", True)
    with pytest.raises(Conflito) as erro:
        repo.inserir_inscricao(operacao, operador, "Verde", "Médico", "MT-02", True)
    assert erro.value.restricao == "inscricao.operador"
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        conn.execute(
            "INSERT INTO inscricao (operador_id, operacao_id, time, classe, dispositivo,"
            " consentimento) VALUES (?, ?, 'Azul', 'Fuzileiro', 'MT-09', 1)",
            (operador, operacao))


def test_r3_dispositivo_repetido_na_mesma_operacao_e_recusado(repo, relogio):
    operacao = nova_operacao(repo)
    inscrever(repo, operacao, novo_operador(repo, relogio, "alfa"), "MT-01")
    outro = novo_operador(repo, relogio, "bravo")
    assert codigo_do_erro(inscrever, repo, operacao, outro, "MT-01") == "dispositivo_em_uso"
    assert len(servicos.listar_inscritos(repo, operacao)) == 1


def test_r3_dispositivo_normalizado_conta_como_o_mesmo(repo, relogio):
    operacao = nova_operacao(repo)
    inscrever(repo, operacao, novo_operador(repo, relogio, "alfa"), "MT-01")
    outro = novo_operador(repo, relogio, "bravo")
    assert codigo_do_erro(inscrever, repo, operacao, outro, " mt-01 ") == "dispositivo_em_uso"


def test_r3_o_mesmo_dispositivo_pode_ser_usado_em_outra_operacao(repo, relogio):
    op1, op2 = nova_operacao(repo, "Op 1"), nova_operacao(repo, "Op 2")
    inscrever(repo, op1, novo_operador(repo, relogio, "alfa"), "MT-01")
    inscrever(repo, op2, novo_operador(repo, relogio, "bravo"), "MT-01")
    assert len(servicos.listar_inscritos(repo, op2)) == 1


def test_r3_o_banco_recusa_o_dispositivo_repetido_pelo_unique(repo, relogio):
    operacao = nova_operacao(repo)
    repo.inserir_inscricao(operacao, novo_operador(repo, relogio, "alfa"),
                           "Azul", "Fuzileiro", "MT-01", True)
    with pytest.raises(Conflito) as erro:
        repo.inserir_inscricao(operacao, novo_operador(repo, relogio, "bravo"),
                               "Azul", "Fuzileiro", "MT-01", True)
    assert erro.value.restricao == "inscricao.dispositivo"


def test_r4_mudar_time_e_classe_altera_so_a_inscricao(repo, relogio):
    operador = novo_operador(repo, relogio)
    op1, op2 = nova_operacao(repo, "Op 1"), nova_operacao(repo, "Op 2")
    inscricao = inscrever(repo, op1, operador, "MT-01", "Azul", "Fuzileiro")
    outra = inscrever(repo, op2, operador, "MT-01", "Azul", "Fuzileiro")
    perfil_antes = repo.buscar_operador(operador)
    servicos.alterar_inscricao(repo, inscricao, "Vermelho", "Médico")
    alterada = repo.buscar_inscricao(inscricao)
    assert (alterada["time"], alterada["classe"]) == ("Vermelho", "Médico")
    assert repo.buscar_operador(operador) == perfil_antes
    intocada = repo.buscar_inscricao(outra)
    assert (intocada["time"], intocada["classe"]) == ("Azul", "Fuzileiro")


def test_r4_alteracao_recusa_time_ou_classe_fora_da_lista(repo, relogio):
    inscricao = inscrever(repo, nova_operacao(repo), novo_operador(repo, relogio))
    assert codigo_do_erro(servicos.alterar_inscricao, repo, inscricao,
                          "Roxo", "Médico") == "dados_invalidos"
    assert codigo_do_erro(servicos.alterar_inscricao, repo, inscricao,
                          "Azul", "Piloto") == "dados_invalidos"
    assert repo.buscar_inscricao(inscricao)["time"] == "Azul"


def test_r4_alteracao_de_inscricao_inexistente(repo):
    codigo = codigo_do_erro(servicos.alterar_inscricao, repo, 999, "Azul", "Médico")
    assert codigo == "inscricao_inexistente"


def test_r5_inscricao_sem_consentimento_e_recusada_e_nao_grava(repo, relogio):
    operador = novo_operador(repo, relogio)
    operacao = nova_operacao(repo)
    codigo = codigo_do_erro(inscrever, repo, operacao, operador, consentimento=False)
    assert codigo == "sem_consentimento"
    assert servicos.listar_inscritos(repo, operacao) == []


def test_r5_o_banco_tambem_recusa_inscricao_sem_consentimento(repo, relogio):
    operador = novo_operador(repo, relogio)
    operacao = nova_operacao(repo)
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        repo.inserir_inscricao(operacao, operador, "Azul", "Fuzileiro", "MT-01", False)


@pytest.mark.parametrize("time, classe, dispositivo", [
    ("Roxo", "Fuzileiro", "MT-01"),
    ("Azul", "Piloto", "MT-01"),
    ("Azul", "Fuzileiro", ""),
    ("Azul", "Fuzileiro", "   "),
    ("Azul", "Fuzileiro", "M" * 33),
])
def test_r1_inscricao_com_dados_invalidos(repo, relogio, time, classe, dispositivo):
    operador = novo_operador(repo, relogio)
    operacao = nova_operacao(repo)
    codigo = codigo_do_erro(inscrever, repo, operacao, operador, dispositivo, time, classe)
    assert codigo == "dados_invalidos"
    assert servicos.listar_inscritos(repo, operacao) == []


@pytest.mark.parametrize("time, classe", [(None, "Fuzileiro"), (["Azul"], "Fuzileiro"),
                                          ("Azul", None), ("Azul", ["Médico"])])
def test_r1_time_ou_classe_que_nao_sao_texto_dao_dados_invalidos(repo, relogio, time, classe):
    operador = novo_operador(repo, relogio)
    codigo = codigo_do_erro(inscrever, repo, nova_operacao(repo), operador,
                            time=time, classe=classe)
    assert codigo == "dados_invalidos"


def test_us02_nome_ou_local_ausentes_dao_dados_invalidos(repo):
    assert codigo_do_erro(servicos.criar_operacao, repo, None, "2026-11-10", "Local") == (
        "dados_invalidos")
    assert codigo_do_erro(servicos.criar_operacao, repo, "Op", "2026-11-10", None) == (
        "dados_invalidos")


def test_us02_nome_e_local_sao_gravados_sem_espacos_nas_pontas(repo):
    operacao = servicos.criar_operacao(repo, "  Op 1 ", "2026-11-10", " Campo ")
    gravada = servicos.obter_operacao(repo, operacao)
    assert (gravada["nome"], gravada["local"]) == ("Op 1", "Campo")


def test_r1_inscricao_grava_o_dispositivo_normalizado(repo, relogio):
    operacao = nova_operacao(repo)
    inscricao = inscrever(repo, operacao, novo_operador(repo, relogio), " mt-01 ")
    gravada = repo.buscar_inscricao(inscricao)
    assert gravada["dispositivo"] == "MT-01"
    assert gravada["consentimento"] in (1, True)


def test_r1_lista_de_inscritos_traz_cor_do_time_em_ordem_de_apelido(repo, relogio):
    operacao = nova_operacao(repo)
    inscrever(repo, operacao, novo_operador(repo, relogio, "zulu"), "MT-02", "Verde")
    inscrever(repo, operacao, novo_operador(repo, relogio, "alfa"), "MT-01", "Azul")
    inscritos = servicos.listar_inscritos(repo, operacao)
    assert [i["apelido"] for i in inscritos] == ["alfa", "zulu"]
    assert inscritos[0]["cor"] == servicos.TIMES["Azul"]
    assert set(inscritos[0]) == {"id", "operador_id", "apelido", "nome", "time", "cor",
                                 "classe", "dispositivo"}


def test_r1_lista_de_inscritos_de_operacao_inexistente(repo):
    assert codigo_do_erro(servicos.listar_inscritos, repo, 999) == "operacao_inexistente"


def test_r2_reenvio_identico_da_inscricao_acusa_inscricao_duplicada(repo, relogio):
    operador = novo_operador(repo, relogio)
    operacao = nova_operacao(repo)
    inscrever(repo, operacao, operador, "MT-01")
    assert codigo_do_erro(inscrever, repo, operacao, operador, "MT-01") == "inscricao_duplicada"


def test_r2_e_r3_juntas_a_mensagem_e_a_da_inscricao_repetida(repo, relogio):
    operacao = nova_operacao(repo)
    alfa = novo_operador(repo, relogio, "alfa")
    bravo = novo_operador(repo, relogio, "bravo")
    inscrever(repo, operacao, alfa, "MT-01")
    inscrever(repo, operacao, bravo, "MT-02")
    # alfa já está inscrito e tenta o dispositivo de bravo: viola R2 e R3 ao mesmo tempo
    assert codigo_do_erro(inscrever, repo, operacao, alfa, "MT-02") == "inscricao_duplicada"


# ------------------------------------------------------------------- R6

def test_r6_operacao_avanca_de_planejada_a_em_curso_e_a_encerrada(repo):
    operacao = nova_operacao(repo)
    assert servicos.obter_operacao(repo, operacao)["situacao"] == "planejada"
    assert servicos.avancar_situacao(repo, operacao) == "em_curso"
    assert servicos.obter_operacao(repo, operacao)["situacao"] == "em_curso"
    assert servicos.avancar_situacao(repo, operacao) == "encerrada"
    assert servicos.obter_operacao(repo, operacao)["situacao"] == "encerrada"


def test_r6_operacao_encerrada_nao_avanca(repo):
    operacao = nova_operacao(repo)
    servicos.avancar_situacao(repo, operacao)
    servicos.avancar_situacao(repo, operacao)
    assert codigo_do_erro(servicos.avancar_situacao, repo, operacao) == "transicao_invalida"
    assert servicos.obter_operacao(repo, operacao)["situacao"] == "encerrada"


def test_r6_avancar_operacao_inexistente(repo):
    assert codigo_do_erro(servicos.avancar_situacao, repo, 999) == "operacao_inexistente"


def test_r6_so_uma_operacao_pode_estar_em_curso(repo):
    primeira, segunda = nova_operacao(repo, "Op 1"), nova_operacao(repo, "Op 2")
    servicos.avancar_situacao(repo, primeira)
    assert codigo_do_erro(servicos.avancar_situacao, repo, segunda) == "outra_em_curso"
    assert servicos.obter_operacao(repo, segunda)["situacao"] == "planejada"


def test_r6_apos_encerrar_a_primeira_a_segunda_pode_iniciar(repo):
    primeira, segunda = nova_operacao(repo, "Op 1"), nova_operacao(repo, "Op 2")
    servicos.avancar_situacao(repo, primeira)
    servicos.avancar_situacao(repo, primeira)
    assert servicos.avancar_situacao(repo, segunda) == "em_curso"
    assert repo.operacao_em_curso()["id"] == segunda


def test_r6_o_banco_recusa_duas_operacoes_em_curso_pelo_indice_unico(repo):
    primeira, segunda = nova_operacao(repo, "Op 1"), nova_operacao(repo, "Op 2")
    repo.atualizar_situacao(primeira, "em_curso")
    with pytest.raises(Conflito) as erro:
        repo.atualizar_situacao(segunda, "em_curso")
    assert erro.value.restricao == "operacao.em_curso"
    assert repo.buscar_operacao(segunda)["situacao"] == "planejada"


def test_r6_operacao_em_curso_do_repositorio(repo):
    assert repo.operacao_em_curso() is None
    operacao = nova_operacao(repo)
    repo.atualizar_situacao(operacao, "em_curso")
    assert repo.operacao_em_curso()["id"] == operacao


def test_r6_proxima_situacao_e_so_a_transicao_valida():
    assert servicos.proxima_situacao("planejada") == "em_curso"
    assert servicos.proxima_situacao("em_curso") == "encerrada"
    assert servicos.proxima_situacao("encerrada") is None


def test_r6_inscricao_em_operacao_encerrada_e_recusada(repo, relogio):
    operacao = nova_operacao(repo)
    alfa, bravo = novo_operador(repo, relogio, "alfa"), novo_operador(repo, relogio, "bravo")
    inscrever(repo, operacao, alfa, "MT-01")
    servicos.avancar_situacao(repo, operacao)
    servicos.avancar_situacao(repo, operacao)
    assert codigo_do_erro(inscrever, repo, operacao, bravo, "MT-02") == "operacao_encerrada"
    assert len(servicos.listar_inscritos(repo, operacao)) == 1


def test_r6_encerrada_vence_as_outras_checagens_da_inscricao(repo, relogio):
    operacao = nova_operacao(repo)
    servicos.avancar_situacao(repo, operacao)
    servicos.avancar_situacao(repo, operacao)
    codigo = codigo_do_erro(inscrever, repo, operacao, 999, consentimento=False)
    assert codigo == "operacao_encerrada"


def test_r6_inscricao_em_operacao_em_curso_e_permitida(repo, relogio):
    operacao = nova_operacao(repo)
    servicos.avancar_situacao(repo, operacao)
    inscrever(repo, operacao, novo_operador(repo, relogio))
    assert len(servicos.listar_inscritos(repo, operacao)) == 1


def test_r6_alteracao_de_inscricao_em_operacao_encerrada_e_recusada(repo, relogio):
    operacao = nova_operacao(repo)
    inscricao = inscrever(repo, operacao, novo_operador(repo, relogio))
    servicos.avancar_situacao(repo, operacao)
    servicos.avancar_situacao(repo, operacao)
    codigo = codigo_do_erro(servicos.alterar_inscricao, repo, inscricao, "Verde", "Médico")
    assert codigo == "operacao_encerrada"
    assert repo.buscar_inscricao(inscricao)["time"] == "Azul"
