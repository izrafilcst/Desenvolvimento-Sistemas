"""Regras de negócio R1 a R9 (docs/backlog.md). Sem SQL e sem Flask.

Cada função recebe o Repositorio e devolve um resultado ou levanta
ErroDeNegocio(codigo, mensagem). O "agora" é sempre um parâmetro
(datetime com fuso UTC), para os testes injetarem o relógio (R9).
Datas e horas são gravadas como texto ISO 8601: agora.isoformat().
"""

from datetime import datetime

from repositorio import Conflito, Repositorio  # noqa: F401  (Conflito é usado na implementação)

# Listas fixas do backlog. Trocá-las não mexe no modelo.
TIMES = {
    "Azul": "#1f6feb",
    "Vermelho": "#d1242f",
    "Verde": "#1a7f37",
    "Amarelo": "#d4a72c",
}
CLASSES = ("Fuzileiro", "Suporte", "Atirador designado", "Médico")
SITUACOES = ("planejada", "em_curso", "encerrada")
PROXIMA_SITUACAO = {"planejada": "em_curso", "em_curso": "encerrada"}   # R6
ROTULO_TRANSICAO = {"em_curso": "Iniciar operação", "encerrada": "Encerrar operação"}
PAPEIS = ("organizador", "observador")
ESTADOS = ("sem_sinal", "ativo", "atrasado", "perdido")                 # R9
CENTRO_PADRAO = (-15.7939, -47.8828)  # Brasília, quando a operação não informa o centro

# Códigos de ErroDeNegocio. As rotas mostram a mensagem; a API devolve o código.
CODIGOS = (
    "dados_invalidos",        # campo vazio, longo demais, data, time ou classe fora da lista
    "apelido_duplicado",      # US01
    "operador_inexistente",
    "operacao_inexistente",
    "inscricao_inexistente",
    "inscricao_duplicada",    # R2
    "dispositivo_em_uso",     # R3
    "sem_consentimento",      # R5
    "transicao_invalida",     # R6: encerrada não avança
    "outra_em_curso",         # R6: já há operação em curso
    "operacao_encerrada",     # R6: não há inscrição (nem alteração) em operação encerrada
    "login_duplicado",
    "papel_invalido",
)


class ErroDeNegocio(Exception):
    """Violação de regra. `codigo` está em CODIGOS; `mensagem` é para o usuário, em português."""

    def __init__(self, codigo: str, mensagem: str):
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem


# ------------------------------------------------------------------ apoio

def normalizar_dispositivo(dispositivo: str) -> str:
    """Tira espaços das pontas e passa para maiúsculas ("mt-01 " vira "MT-01").
    Usada na inscrição e no recebimento de sinais, para R3 e R7 compararem igual."""
    raise NotImplementedError


# ------------------------------------------------------- Incremento 1: R1 a R6

def cadastrar_operador(repo: Repositorio, apelido: str, nome: str, agora: datetime) -> int:
    """US01. Cadastra o perfil permanente uma única vez e devolve o id.
    Apelido de 1 a 32 caracteres e nome de 1 a 100, sem espaços nas pontas
    (senão dados_invalidos). Apelido repetido, sem diferenciar maiúsculas:
    apelido_duplicado."""
    raise NotImplementedError


def listar_operadores(repo: Repositorio) -> list[dict]:
    """US01. Lista de {id, apelido, nome, criado_em} em ordem de apelido."""
    raise NotImplementedError


def criar_operacao(repo: Repositorio, nome: str, data: str, local: str,
                   centro_lat: float | None = None, centro_lon: float | None = None) -> int:
    """US02. Cria a operação como 'planejada' e devolve o id.
    `data` é AAAA-MM-DD válida; nome e local de 1 a 100 caracteres; sem centro,
    usa CENTRO_PADRAO; lat em [-90, 90] e lon em [-180, 180]. Senão dados_invalidos."""
    raise NotImplementedError


def listar_operacoes(repo: Repositorio) -> list[dict]:
    """US02. {id, nome, data, local, situacao, centro_lat, centro_lon, inscritos}."""
    raise NotImplementedError


def obter_operacao(repo: Repositorio, operacao_id: int) -> dict:
    """{id, nome, data, local, situacao, centro_lat, centro_lon}. Senão operacao_inexistente."""
    raise NotImplementedError


def proxima_situacao(situacao: str) -> str | None:
    """R6. A única transição válida a partir de `situacao`, ou None se encerrada.
    A página mostra só o botão dessa transição (rótulo em ROTULO_TRANSICAO)."""
    raise NotImplementedError


def avancar_situacao(repo: Repositorio, operacao_id: int) -> str:
    """R6. Avança planejada -> em_curso -> encerrada e devolve a nova situação.
    Encerrada: transicao_invalida. Iniciar com outra já em curso: outra_em_curso.
    Operação que não existe: operacao_inexistente."""
    raise NotImplementedError


def inscrever(repo: Repositorio, operacao_id: int, operador_id: int, time: str, classe: str,
              dispositivo: str, consentimento: bool) -> int:
    """US03. Inscreve um operador já cadastrado, sem novo cadastro (R1), e devolve o id.
    Ordem das checagens: operacao_inexistente, operacao_encerrada (R6),
    operador_inexistente, sem_consentimento (R5), dados_invalidos (time fora de
    TIMES, classe fora de CLASSES, dispositivo vazio ou com mais de 32 caracteres
    depois de normalizar_dispositivo), inscricao_duplicada (R2) e
    dispositivo_em_uso (R3). R2 e R3 vêm do Conflito do banco."""
    raise NotImplementedError


def alterar_inscricao(repo: Repositorio, inscricao_id: int, time: str, classe: str) -> None:
    """R4. Muda time e classe só na inscrição; o perfil do operador não muda.
    inscricao_inexistente, operacao_encerrada ou dados_invalidos."""
    raise NotImplementedError


def listar_inscritos(repo: Repositorio, operacao_id: int) -> list[dict]:
    """US04. {id, operador_id, apelido, nome, time, cor, classe, dispositivo},
    em que `cor` vem de TIMES. operacao_inexistente se a operação não existe."""
    raise NotImplementedError


# ------------------------------------------------------- Incremento 2: R7 a R9

def receber_sinal(repo: Repositorio, dispositivo: str, pacote: int, lat: float, lon: float,
                  bateria: float, agora: datetime) -> str:
    """US05. Devolve "gravado", "duplicado" ou "descartado". O formato já foi
    validado na API; aqui o dispositivo passa por normalizar_dispositivo.
    R7: sem operação em curso, descarte com motivo 'sem_operacao_em_curso' e
    operacao_id None; dispositivo sem inscrição na operação em curso, descarte
    com motivo 'sem_inscricao'. O descarte nunca vira posição.
    R8: o mesmo pacote do mesmo dispositivo na operação vale uma vez só
    (Conflito "posicao.pacote" vira "duplicado", sem posição nova)."""
    raise NotImplementedError


def estado_por_tempo(segundos: float | None, atrasado_s: int, perdido_s: int) -> str:
    """R9. None: sem_sinal; segundos <= atrasado_s: ativo;
    segundos <= perdido_s: atrasado; acima de perdido_s: perdido.
    Com 60/120: 60 s é ativo, 61 s atrasado, 120 s atrasado e 121 s perdido."""
    raise NotImplementedError


def calcular_rumo(lat1: float, lon1: float, lat2: float, lon2: float) -> float | None:
    """Rumo inicial do ponto 1 para o ponto 2, em graus [0, 360), 0 = norte,
    90 = leste, arredondado a 1 casa. None se os pontos são iguais."""
    raise NotImplementedError


def situacao_da_operacao(repo: Repositorio, operacao_id: int, agora: datetime,
                         atrasado_s: int, perdido_s: int) -> dict:
    """US06. Situação ao vivo de uma operação (operacao_inexistente se não existe):

    {"operacao": {id, nome, data, local, situacao, centro_lat, centro_lon},
     "descartados": int,
     "inscritos": [{"inscricao_id", "apelido", "time", "cor", "classe",
                    "dispositivo", "estado", "segundos", "lat", "lon",
                    "bateria", "rumo"}]}

    Por inscrito: `segundos` é int (parte inteira de agora - recebido_em da
    última posição) ou None; `estado` vem de estado_por_tempo; lat, lon e
    bateria são os da última posição (ou None); `rumo` sai de calcular_rumo
    sobre o par mais recente de posições distintas entre as 10 últimas
    (ultimas_posicoes), e é None se não houver par distinto."""
    raise NotImplementedError


def situacao_em_curso(repo: Repositorio, agora: datetime, atrasado_s: int,
                      perdido_s: int) -> dict | None:
    """situacao_da_operacao da operação em curso, ou None se não há operação em curso."""
    raise NotImplementedError


# ------------------------------------------------------ usuários (US07, R10)

def criar_usuario(repo: Repositorio, login: str, senha: str, papel: str) -> int:
    """US07. Grava o usuário com a senha em hash (werkzeug.security.generate_password_hash).
    login de 3 a 32 caracteres [a-z0-9_.-]; senha com pelo menos 8 caracteres
    (senão dados_invalidos); papel fora de PAPEIS: papel_invalido; login repetido:
    login_duplicado."""
    raise NotImplementedError


def autenticar(repo: Repositorio, login: str, senha: str) -> dict | None:
    """US07. {id, login, papel} se login e senha conferem
    (werkzeug.security.check_password_hash), senão None."""
    raise NotImplementedError
