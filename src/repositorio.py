"""Todo o SQL do sistema. Única camada que conhece o SQLite (ADR-002).

Contrato: cada método devolve dict (ou lista de dict), nunca sqlite3.Row.
Cada escrita faz commit (use `with self.conn:`). Toda consulta usa
parâmetros `?`, nunca SQL montado com f-string ou concatenação.

Quando uma restrição UNIQUE do schema.sql é violada, o método levanta
Conflito com o nome da restrição (veja RESTRICOES), e não sqlite3.IntegrityError.
"""

import sqlite3
from contextlib import contextmanager

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


# Trechos da mensagem do SQLite (UNIQUE constraint failed: tabela.coluna, ...) -> restrição.
_UNIQUES = (
    ("operador.apelido", "operador.apelido"),
    ("operacao.situacao", "operacao.em_curso"),
    ("inscricao.operador_id", "inscricao.operador"),
    ("inscricao.dispositivo", "inscricao.dispositivo"),
    ("posicao.pacote", "posicao.pacote"),
    ("usuario.login", "usuario.login"),
)


def _traduzir(erro: sqlite3.IntegrityError) -> Exception:
    """Conflito para uma violação de UNIQUE conhecida; qualquer outra sobe como está."""
    mensagem = str(erro)
    if mensagem.startswith("UNIQUE constraint failed"):
        for trecho, restricao in _UNIQUES:
            if trecho in mensagem:
                return Conflito(restricao)
    return erro


_SQL_INSCRICAO = (
    "SELECT id, operador_id, operacao_id, time, classe, dispositivo, consentimento"
    " FROM inscricao")


def _com_consentimento_bool(inscricao: dict | None) -> dict | None:
    if inscricao is not None:
        inscricao["consentimento"] = bool(inscricao["consentimento"])
    return inscricao


def _como_dict(cursor: sqlite3.Cursor, linha) -> dict:
    return dict(zip([coluna[0] for coluna in cursor.description], linha))


class Repositorio:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ------------------------------------------------------------------- apoio

    def _todos(self, sql: str, parametros: tuple = ()) -> list[dict]:
        cursor = self.conn.execute(sql, parametros)
        return [_como_dict(cursor, linha) for linha in cursor.fetchall()]

    def _um(self, sql: str, parametros: tuple = ()) -> dict | None:
        cursor = self.conn.execute(sql, parametros)
        linha = cursor.fetchone()
        return None if linha is None else _como_dict(cursor, linha)

    @contextmanager
    def _escrita(self):
        """Transação que faz commit no fim e traduz IntegrityError de UNIQUE em Conflito."""
        try:
            with self.conn:
                yield
        except sqlite3.IntegrityError as erro:
            traduzido = _traduzir(erro)
            if traduzido is erro:
                raise
            raise traduzido from erro

    def _inserir(self, sql: str, parametros: tuple) -> int:
        with self._escrita():
            return self.conn.execute(sql, parametros).lastrowid

    # ---------------------------------------------------------------- operador

    def inserir_operador(self, apelido: str, nome: str, criado_em: str) -> int:
        """Grava o perfil permanente e devolve o id. Conflito("operador.apelido") se repetido."""
        return self._inserir(
            "INSERT INTO operador (apelido, nome, criado_em) VALUES (?, ?, ?)",
            (apelido, nome, criado_em))

    def listar_operadores(self) -> list[dict]:
        """Operadores em ordem de apelido: {id, apelido, nome, criado_em}."""
        return self._todos(
            "SELECT id, apelido, nome, criado_em FROM operador ORDER BY apelido, id")

    def buscar_operador(self, operador_id: int) -> dict | None:
        """{id, apelido, nome, criado_em} ou None."""
        return self._um(
            "SELECT id, apelido, nome, criado_em FROM operador WHERE id = ?", (operador_id,))

    # ---------------------------------------------------------------- operacao

    def inserir_operacao(self, nome: str, data: str, local: str,
                         centro_lat: float, centro_lon: float) -> int:
        """Grava a operação como 'planejada' e devolve o id."""
        return self._inserir(
            "INSERT INTO operacao (nome, data, local, centro_lat, centro_lon)"
            " VALUES (?, ?, ?, ?, ?)",
            (nome, data, local, centro_lat, centro_lon))

    def listar_operacoes(self) -> list[dict]:
        """Operações da mais recente para a mais antiga (data, depois id):
        {id, nome, data, local, situacao, centro_lat, centro_lon, inscritos}
        em que `inscritos` é a contagem de inscrições."""
        return self._todos(
            "SELECT o.id, o.nome, o.data, o.local, o.situacao, o.centro_lat, o.centro_lon,"
            " (SELECT COUNT(*) FROM inscricao i WHERE i.operacao_id = o.id) AS inscritos"
            " FROM operacao o ORDER BY o.data DESC, o.id DESC")

    def buscar_operacao(self, operacao_id: int) -> dict | None:
        """{id, nome, data, local, situacao, centro_lat, centro_lon} ou None."""
        return self._um(
            "SELECT id, nome, data, local, situacao, centro_lat, centro_lon"
            " FROM operacao WHERE id = ?", (operacao_id,))

    def operacao_em_curso(self) -> dict | None:
        """A operação com situacao = 'em_curso' (no máximo uma, R6) ou None."""
        return self._um(
            "SELECT id, nome, data, local, situacao, centro_lat, centro_lon"
            " FROM operacao WHERE situacao = 'em_curso'")

    def atualizar_situacao(self, operacao_id: int, situacao: str) -> None:
        """Troca a situação. Conflito("operacao.em_curso") se já houver outra em curso."""
        with self._escrita():
            self.conn.execute(
                "UPDATE operacao SET situacao = ? WHERE id = ?", (situacao, operacao_id))

    # --------------------------------------------------------------- inscricao

    def inserir_inscricao(self, operacao_id: int, operador_id: int, time: str,
                          classe: str, dispositivo: str, consentimento: bool) -> int:
        """Grava a inscrição e devolve o id.
        Conflito("inscricao.operador") viola R2; Conflito("inscricao.dispositivo") viola R3."""
        return self._inserir(
            "INSERT INTO inscricao (operador_id, operacao_id, time, classe, dispositivo,"
            " consentimento) VALUES (?, ?, ?, ?, ?, ?)",
            (operador_id, operacao_id, time, classe, dispositivo, int(consentimento)))

    def buscar_inscricao(self, inscricao_id: int) -> dict | None:
        """{id, operador_id, operacao_id, time, classe, dispositivo, consentimento} ou None."""
        inscricao = self._um(_SQL_INSCRICAO + " WHERE id = ?", (inscricao_id,))
        return _com_consentimento_bool(inscricao)

    def atualizar_inscricao(self, inscricao_id: int, time: str, classe: str) -> None:
        """Muda time e classe só na inscrição (R4); o operador não é tocado."""
        with self._escrita():
            self.conn.execute(
                "UPDATE inscricao SET time = ?, classe = ? WHERE id = ?",
                (time, classe, inscricao_id))

    def listar_inscritos(self, operacao_id: int) -> list[dict]:
        """Inscritos da operação em ordem de apelido:
        {id (da inscrição), operador_id, apelido, nome, time, classe, dispositivo}."""
        return self._todos(
            "SELECT i.id, i.operador_id, o.apelido, o.nome, i.time, i.classe, i.dispositivo"
            " FROM inscricao i JOIN operador o ON o.id = i.operador_id"
            " WHERE i.operacao_id = ? ORDER BY o.apelido, i.id", (operacao_id,))

    def inscricao_por_dispositivo(self, operacao_id: int, dispositivo: str) -> dict | None:
        """A inscrição do dispositivo nessa operação (como buscar_inscricao) ou None."""
        inscricao = self._um(
            _SQL_INSCRICAO + " WHERE operacao_id = ? AND dispositivo = ?",
            (operacao_id, dispositivo))
        return _com_consentimento_bool(inscricao)

    # ----------------------------------------------------- posicao e descarte

    def inserir_posicao(self, inscricao_id: int, pacote: int, lat: float, lon: float,
                        bateria: float, recebido_em: str) -> int:
        """Grava a posição e devolve o id. Conflito("posicao.pacote") se o pacote já existe (R8)."""
        return self._inserir(
            "INSERT INTO posicao (inscricao_id, pacote, lat, lon, bateria, recebido_em)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (inscricao_id, pacote, lat, lon, bateria, recebido_em))

    def ultimas_posicoes(self, inscricao_id: int, limite: int = 10) -> list[dict]:
        """As últimas posições por ordem de chegada (id), a mais recente primeiro:
        {id, pacote, lat, lon, bateria, recebido_em}."""
        return self._todos(
            "SELECT id, pacote, lat, lon, bateria, recebido_em FROM posicao"
            " WHERE inscricao_id = ? ORDER BY id DESC LIMIT ?", (inscricao_id, limite))

    def contar_posicoes(self, inscricao_id: int) -> int:
        linha = self.conn.execute(
            "SELECT COUNT(*) FROM posicao WHERE inscricao_id = ?", (inscricao_id,)).fetchone()
        return linha[0]

    def inserir_descarte(self, operacao_id: int | None, dispositivo: str, motivo: str,
                         recebido_em: str) -> int:
        """Registra só a origem e o motivo (R7). operacao_id é None sem operação em curso."""
        return self._inserir(
            "INSERT INTO descarte (operacao_id, dispositivo, motivo, recebido_em)"
            " VALUES (?, ?, ?, ?)", (operacao_id, dispositivo, motivo, recebido_em))

    def contar_descartes(self, operacao_id: int) -> int:
        """Descartes registrados com esse operacao_id."""
        linha = self.conn.execute(
            "SELECT COUNT(*) FROM descarte WHERE operacao_id = ?", (operacao_id,)).fetchone()
        return linha[0]

    # ----------------------------------------------------------------- usuario

    def inserir_usuario(self, login: str, senha_hash: str, papel: str) -> int:
        """Grava o usuário e devolve o id. Conflito("usuario.login") se o login já existe."""
        return self._inserir(
            "INSERT INTO usuario (login, senha_hash, papel) VALUES (?, ?, ?)",
            (login, senha_hash, papel))

    def buscar_usuario_por_login(self, login: str) -> dict | None:
        """{id, login, senha_hash, papel} ou None."""
        return self._um(
            "SELECT id, login, senha_hash, papel FROM usuario WHERE login = ?", (login,))

    def buscar_usuario_por_id(self, usuario_id: int) -> dict | None:
        """{id, login, senha_hash, papel} ou None."""
        return self._um(
            "SELECT id, login, senha_hash, papel FROM usuario WHERE id = ?", (usuario_id,))
