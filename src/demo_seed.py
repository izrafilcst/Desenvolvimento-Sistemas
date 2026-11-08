"""Dados da demo de 10/11: cinco operadores e três operações.

    python src/demo_seed.py

Só chama servicos.py (nunca SQL). Se o banco já tem operadores, não mexe
em nada e sai com código 1.

Senhas: MESHTRACKER_SENHA_ORGANIZADOR e MESHTRACKER_SENHA_OBSERVADOR, se
estiverem definidas. Senão, são geradas e impressas uma única vez no fim.
"""

import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
import db  # noqa: E402
import servicos  # noqa: E402
from repositorio import Repositorio  # noqa: E402

CENTRO = (-15.7990, -47.9070)   # Parque da Cidade, Brasília
LOCAL = "Parque da Cidade"

OPERADORES = [
    ("Falcão", "Marina Souza"),
    ("Lobo", "Carlos Lima"),
    ("Coruja", "Beatriz Alves"),
    ("Raposa", "Rafael Mota"),
    ("Pantera", "Helena Dias"),
]

# (apelido, time, classe, dispositivo)
INSCRITOS_ALFA = [
    ("Falcão", "Azul", "Fuzileiro", "MT-01"),
    ("Lobo", "Vermelho", "Suporte", "MT-02"),
    ("Coruja", "Verde", "Atirador designado", "MT-03"),
    ("Raposa", "Amarelo", "Médico", "MT-04"),
    ("Pantera", "Verde", "Fuzileiro", "MT-05"),
]

# Mesmos operadores, outros times (a Bravo é a operação que o simulador alimenta).
INSCRITOS_BRAVO = [
    ("Falcão", "Vermelho", "Médico", "MT-01"),
    ("Lobo", "Verde", "Fuzileiro", "MT-02"),
    ("Coruja", "Amarelo", "Suporte", "MT-03"),
    ("Raposa", "Azul", "Atirador designado", "MT-04"),
    ("Pantera", "Amarelo", "Fuzileiro", "MT-05"),
]


def _operacao(repo, nome: str, data: str, operadores: dict, inscricoes: list) -> int:
    """Cria a operação planejada e inscreve os operadores pelo apelido."""
    operacao_id = servicos.criar_operacao(repo, nome, data, LOCAL, *CENTRO)
    for apelido, time, classe, dispositivo in inscricoes:
        servicos.inscrever(repo, operacao_id, operadores[apelido], time, classe,
                           dispositivo, True)
    return operacao_id


def semear(repo, agora, senha_organizador: str, senha_observador: str) -> dict:
    """Grava a demo pelo servicos.py. Devolve ids e contagens para quem chamou.

    Alfa termina encerrada, Bravo fica em curso (o simulador a alimenta),
    Charlie fica planejada e sem inscritos (demonstração ao vivo).
    """
    operadores = {}
    for apelido, nome in OPERADORES:
        operadores[apelido] = servicos.cadastrar_operador(repo, apelido, nome, agora)

    servicos.criar_usuario(repo, "organizador", senha_organizador, "organizador")
    servicos.criar_usuario(repo, "observador", senha_observador, "observador")

    alfa = _operacao(repo, "Operação Alfa", "2026-10-25", operadores, INSCRITOS_ALFA)
    servicos.avancar_situacao(repo, alfa)   # planejada -> em_curso
    servicos.avancar_situacao(repo, alfa)   # em_curso -> encerrada

    bravo = _operacao(repo, "Operação Bravo", "2026-11-10", operadores, INSCRITOS_BRAVO)
    servicos.avancar_situacao(repo, bravo)  # planejada -> em_curso

    charlie = servicos.criar_operacao(repo, "Operação Charlie", "2026-11-22", LOCAL, *CENTRO)

    return {
        "operadores": len(operadores),
        "usuarios": ["organizador", "observador"],
        "operacoes": {"alfa": alfa, "bravo": bravo, "charlie": charlie},
    }


def _senha(nome_da_variavel: str, papel: str, geradas: list) -> str:
    """Senha da variável de ambiente; se ausente, gera uma e guarda para imprimir."""
    senha = os.environ.get(nome_da_variavel)
    if senha:
        return senha
    senha = secrets.token_urlsafe(9)
    geradas.append((papel, senha))
    return senha


def main() -> int:
    conn = db.conectar(config.carregar()["DATABASE"])
    try:
        db.criar_banco(conn)
        repo = Repositorio(conn)
        if servicos.listar_operadores(repo):
            print("O banco já tem dados. Apague instance/meshtracker.db para recomeçar.")
            return 1

        geradas: list = []
        senha_org = _senha("MESHTRACKER_SENHA_ORGANIZADOR", "organizador", geradas)
        senha_obs = _senha("MESHTRACKER_SENHA_OBSERVADOR", "observador", geradas)
        if len(senha_org) < 8 or len(senha_obs) < 8:
            print("As senhas de MESHTRACKER_SENHA_* precisam ter pelo menos 8 caracteres.")
            return 1

        resumo = semear(repo, config.agora_utc(), senha_org, senha_obs)
    except servicos.ErroDeNegocio as erro:
        print(erro.mensagem)
        return 1
    finally:
        conn.close()

    print(f"Demo gravada: {resumo['operadores']} operadores, "
          f"{len(resumo['operacoes'])} operações (Alfa encerrada, Bravo em curso, "
          "Charlie planejada).")
    print("Usuários: organizador (papel organizador) e observador (papel observador).")
    if geradas:
        print("")
        print("Senhas geradas. Anote agora: elas não serão mostradas de novo.")
        for papel, senha in geradas:
            print(f"  {papel}: {senha}")
    print("")
    print("Próximos passos:")
    print("  1. Exporte MESHTRACKER_TOKEN e suba o app: python src/app.py")
    print("  2. Em outro terminal, com o mesmo MESHTRACKER_TOKEN, rode o simulador:")
    print("     python src/simulador.py --url http://127.0.0.1:5000 --parar MT-03 --apos 20")
    return 0


if __name__ == "__main__":
    sys.exit(main())
