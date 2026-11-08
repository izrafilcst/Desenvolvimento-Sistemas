"""Dados da demo (src/demo_seed.py): semear sobre o banco temporário de conftest."""

from datetime import datetime, timezone

import demo_seed
import servicos
from werkzeug.security import check_password_hash

AGORA = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
SENHA_ORG = "senha-org-demo-123"
SENHA_OBS = "senha-obs-demo-123"


def _semear(repo):
    return demo_seed.semear(repo, AGORA, SENHA_ORG, SENHA_OBS)


def _operacoes_por_nome(repo):
    return {op["nome"]: op for op in servicos.listar_operacoes(repo)}


def test_cria_cinco_operadores(repo):
    _semear(repo)
    operadores = servicos.listar_operadores(repo)
    assert sorted(o["apelido"] for o in operadores) == sorted(
        apelido for apelido, _ in demo_seed.OPERADORES)
    assert len(operadores) == 5


def test_tres_operacoes_com_as_situacoes_certas(repo):
    resumo = _semear(repo)
    ops = _operacoes_por_nome(repo)
    assert set(ops) == {"Operação Alfa", "Operação Bravo", "Operação Charlie"}
    assert ops["Operação Alfa"]["situacao"] == "encerrada"
    assert ops["Operação Bravo"]["situacao"] == "em_curso"
    assert ops["Operação Charlie"]["situacao"] == "planejada"
    assert ops["Operação Alfa"]["data"] == "2026-10-25"
    assert ops["Operação Bravo"]["data"] == "2026-11-10"
    assert ops["Operação Charlie"]["data"] == "2026-11-22"
    assert resumo["operacoes"]["bravo"] == ops["Operação Bravo"]["id"]


def test_operacoes_no_mesmo_local_e_centro(repo):
    _semear(repo)
    for op in _operacoes_por_nome(repo).values():
        assert op["local"] == "Parque da Cidade"
        assert op["centro_lat"] == -15.7990
        assert op["centro_lon"] == -47.9070


def test_bravo_tem_cinco_inscritos_com_times_diferentes_da_alfa(repo):
    resumo = _semear(repo)
    alfa = servicos.listar_inscritos(repo, resumo["operacoes"]["alfa"])
    bravo = servicos.listar_inscritos(repo, resumo["operacoes"]["bravo"])
    assert len(bravo) == 5
    assert sorted(i["dispositivo"] for i in bravo) == [
        "MT-01", "MT-02", "MT-03", "MT-04", "MT-05"]
    time_alfa = {i["apelido"]: i["time"] for i in alfa}
    for inscrito in bravo:
        assert inscrito["time"] != time_alfa[inscrito["apelido"]]


def test_alfa_tem_times_e_classes_variados(repo):
    resumo = _semear(repo)
    alfa = servicos.listar_inscritos(repo, resumo["operacoes"]["alfa"])
    assert len(alfa) == 5
    assert len({i["time"] for i in alfa}) >= 3
    assert len({i["classe"] for i in alfa}) >= 3


def test_perfis_nao_duplicam(repo):
    resumo = _semear(repo)
    operadores = servicos.listar_operadores(repo)
    ids_por_apelido = {o["apelido"]: o["id"] for o in operadores}
    assert len(ids_por_apelido) == len(operadores) == 5
    for chave in ("alfa", "bravo"):
        for inscrito in servicos.listar_inscritos(repo, resumo["operacoes"][chave]):
            assert inscrito["operador_id"] == ids_por_apelido[inscrito["apelido"]]


def test_senhas_ficam_como_hash(repo):
    _semear(repo)
    for login, senha in (("organizador", SENHA_ORG), ("observador", SENHA_OBS)):
        usuario = repo.buscar_usuario_por_login(login)
        assert usuario["senha_hash"] != senha
        assert senha not in usuario["senha_hash"]
        assert check_password_hash(usuario["senha_hash"], senha)
