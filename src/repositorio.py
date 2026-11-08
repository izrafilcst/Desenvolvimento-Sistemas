"""Todo o SQL do sistema. Única camada que conhece o SQLite (ADR-002).

Contrato: cada método devolve dict (ou lista de dict), nunca sqlite3.Row.
Cada escrita faz commit (use `with self.conn:`). Toda consulta usa
parâmetros `?`, nunca SQL montado com f-string ou concatenação.

Quando uma restrição UNIQUE do schema.sql é violada, o método levanta
Conflito com o nome da restrição (veja RESTRICOES), e não sqlite3.IntegrityError.
"""

import sqlite3

# Nomes que Conflito.restricao pode ter.
RESTRICOES = (
    "operador.apelido",      # apelido único
    "operacao.em_curso",     # R6: uma operação em curso por vez
    "inscricao.operador",    # R2: UNIQUE (operador_id, operacao_id)
    "inscricao.dispositivo", # R3: UNIQUE (operacao_id, dispositivo)
    "posicao.pacote",        # R8: UNIQUE (inscricao_id, pacote)
    "usuario.login",         # login único
)


class Conflito(Exception):
    """Violação de uma restrição de unicidade do banco."""

    def __init__(self, restricao: str):
        super().__init__(restricao)
        self.restricao = restricao


class Repositorio:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---------------------------------------------------------------- operador

    def inserir_operador(self, apelido: str, nome: str, criado_em: str) -> int:
        """Grava o perfil permanente e devolve o id. Conflito("operador.apelido") se repetido."""
        raise NotImplementedError

    def listar_operadores(self) -> list[dict]:
        """Operadores em ordem de apelido: {id, apelido, nome, criado_em}."""
        raise NotImplementedError

    def buscar_operador(self, operador_id: int) -> dict | None:
        """{id, apelido, nome, criado_em} ou None."""
        raise NotImplementedError

    # ---------------------------------------------------------------- operacao

    def inserir_operacao(self, nome: str, data: str, local: str,
                         centro_lat: float, centro_lon: float) -> int:
        """Grava a operação como 'planejada' e devolve o id."""
        raise NotImplementedError

    def listar_operacoes(self) -> list[dict]:
        """Operações da mais recente para a mais antiga (data, depois id):
        {id, nome, data, local, situacao, centro_lat, centro_lon, inscritos}
        em que `inscritos` é a contagem de inscrições."""
        raise NotImplementedError

    def buscar_operacao(self, operacao_id: int) -> dict | None:
        """{id, nome, data, local, situacao, centro_lat, centro_lon} ou None."""
        raise NotImplementedError

    def operacao_em_curso(self) -> dict | None:
        """A operação com situacao = 'em_curso' (no máximo uma, R6) ou None."""
        raise NotImplementedError

    def atualizar_situacao(self, operacao_id: int, situacao: str) -> None:
        """Troca a situação. Conflito("operacao.em_curso") se já houver outra em curso."""
        raise NotImplementedError

    # --------------------------------------------------------------- inscricao

    def inserir_inscricao(self, operacao_id: int, operador_id: int, time: str,
                          classe: str, dispositivo: str, consentimento: bool) -> int:
        """Grava a inscrição e devolve o id.
        Conflito("inscricao.operador") viola R2; Conflito("inscricao.dispositivo") viola R3."""
        raise NotImplementedError

    def buscar_inscricao(self, inscricao_id: int) -> dict | None:
        """{id, operador_id, operacao_id, time, classe, dispositivo, consentimento} ou None."""
        raise NotImplementedError

    def atualizar_inscricao(self, inscricao_id: int, time: str, classe: str) -> None:
        """Muda time e classe só na inscrição (R4); o operador não é tocado."""
        raise NotImplementedError

    def listar_inscritos(self, operacao_id: int) -> list[dict]:
        """Inscritos da operação em ordem de apelido:
        {id (da inscrição), operador_id, apelido, nome, time, classe, dispositivo}."""
        raise NotImplementedError

    def inscricao_por_dispositivo(self, operacao_id: int, dispositivo: str) -> dict | None:
        """A inscrição do dispositivo nessa operação (como buscar_inscricao) ou None."""
        raise NotImplementedError

    # ----------------------------------------------------- posicao e descarte

    def inserir_posicao(self, inscricao_id: int, pacote: int, lat: float, lon: float,
                        bateria: float, recebido_em: str) -> int:
        """Grava a posição e devolve o id. Conflito("posicao.pacote") se o pacote já existe (R8)."""
        raise NotImplementedError

    def ultimas_posicoes(self, inscricao_id: int, limite: int = 10) -> list[dict]:
        """As últimas posições por ordem de chegada (id), a mais recente primeiro:
        {id, pacote, lat, lon, bateria, recebido_em}."""
        raise NotImplementedError

    def contar_posicoes(self, inscricao_id: int) -> int:
        raise NotImplementedError

    def inserir_descarte(self, operacao_id: int | None, dispositivo: str, motivo: str,
                         recebido_em: str) -> int:
        """Registra só a origem e o motivo (R7). operacao_id é None sem operação em curso."""
        raise NotImplementedError

    def contar_descartes(self, operacao_id: int) -> int:
        """Descartes registrados com esse operacao_id."""
        raise NotImplementedError

    # ----------------------------------------------------------------- usuario

    def inserir_usuario(self, login: str, senha_hash: str, papel: str) -> int:
        """Grava o usuário e devolve o id. Conflito("usuario.login") se o login já existe."""
        raise NotImplementedError

    def buscar_usuario_por_login(self, login: str) -> dict | None:
        """{id, login, senha_hash, papel} ou None."""
        raise NotImplementedError

    def buscar_usuario_por_id(self, usuario_id: int) -> dict | None:
        """{id, login, senha_hash, papel} ou None."""
        raise NotImplementedError
