"""Regras de negócio R1 a R9 (docs/backlog.md). Sem SQL e sem Flask.

Cada função recebe o Repositorio e devolve um resultado ou levanta
ErroDeNegocio(codigo, mensagem). O "agora" é sempre um parâmetro
(datetime com fuso UTC), para os testes injetarem o relógio (R9).
Datas e horas são gravadas como texto ISO 8601: agora.isoformat().
"""

import re
from datetime import date, datetime
from math import atan2, cos, degrees, radians, sin

from werkzeug.security import check_password_hash, generate_password_hash

from repositorio import Conflito, Repositorio

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

def _exigir_texto(valor, maximo: int, mensagem: str) -> None:
    """Texto de 1 a `maximo` caracteres, sem espaços nas pontas; senão dados_invalidos."""
    if not isinstance(valor, str) or valor != valor.strip() or not 1 <= len(valor) <= maximo:
        raise ErroDeNegocio("dados_invalidos", mensagem)


def _aparar(valor):
    """Tira os espaços das pontas de um texto; qualquer outro valor passa como está."""
    return valor.strip() if isinstance(valor, str) else valor


def _exigir_time_e_classe(time: str, classe: str) -> None:
    if not isinstance(time, str) or time not in TIMES:
        raise ErroDeNegocio("dados_invalidos", "Escolha um dos times da lista.")
    if not isinstance(classe, str) or classe not in CLASSES:
        raise ErroDeNegocio("dados_invalidos", "Escolha uma das classes da lista.")


def _data_valida(data) -> bool:
    if not isinstance(data, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", data):
        return False
    try:
        date.fromisoformat(data)
    except ValueError:
        return False
    return True


def _coordenada(valor, limite: float) -> bool:
    numero = isinstance(valor, (int, float)) and not isinstance(valor, bool)
    return numero and -limite <= valor <= limite


def _centro_valido(lat, lon) -> tuple[float, float]:
    """CENTRO_PADRAO se nenhum foi informado; senão os dois, dentro dos limites."""
    if lat is None and lon is None:
        return CENTRO_PADRAO
    if not (_coordenada(lat, 90) and _coordenada(lon, 180)):
        raise ErroDeNegocio("dados_invalidos",
                            "A latitude vai de -90 a 90 e a longitude de -180 a 180.")
    return float(lat), float(lon)


def _erro_de_inscricao(repo: Repositorio, conflito: Conflito, operacao_id: int,
                       operador_id: int) -> ErroDeNegocio:
    """Traduz o Conflito do banco (R2, R3) na mensagem para o organizador.
    O SQLite acusa só uma restrição por vez; se o operador já está inscrito, R2 vence."""
    ja_inscrito = any(i["operador_id"] == operador_id
                      for i in repo.listar_inscritos(operacao_id))
    if conflito.restricao == "inscricao.operador" or ja_inscrito:
        return ErroDeNegocio("inscricao_duplicada",
                             "Este operador já está inscrito nesta operação.")
    if conflito.restricao == "inscricao.dispositivo":
        return ErroDeNegocio("dispositivo_em_uso",
                             "Este dispositivo já pertence a outra inscrição desta operação.")
    raise conflito


def normalizar_dispositivo(dispositivo: str) -> str:
    """Tira espaços das pontas e passa para maiúsculas ("mt-01 " vira "MT-01").
    Usada na inscrição e no recebimento de sinais, para R3 e R7 compararem igual."""
    return dispositivo.strip().upper()


# ------------------------------------------------------- Incremento 1: R1 a R6

def cadastrar_operador(repo: Repositorio, apelido: str, nome: str, agora: datetime) -> int:
    """US01. Cadastra o perfil permanente uma única vez e devolve o id.
    Apelido de 1 a 32 caracteres e nome de 1 a 100, sem espaços nas pontas
    (senão dados_invalidos). Apelido repetido, sem diferenciar maiúsculas:
    apelido_duplicado."""
    _exigir_texto(apelido, 32, "O apelido deve ter de 1 a 32 caracteres, sem espaços nas pontas.")
    _exigir_texto(nome, 100, "O nome deve ter de 1 a 100 caracteres, sem espaços nas pontas.")
    try:
        return repo.inserir_operador(apelido, nome, agora.isoformat())
    except Conflito as conflito:
        raise ErroDeNegocio("apelido_duplicado",
                            "Já existe um operador com este apelido.") from conflito


def listar_operadores(repo: Repositorio) -> list[dict]:
    """US01. Lista de {id, apelido, nome, criado_em} em ordem de apelido."""
    return repo.listar_operadores()


def criar_operacao(repo: Repositorio, nome: str, data: str, local: str,
                   centro_lat: float | None = None, centro_lon: float | None = None) -> int:
    """US02. Cria a operação como 'planejada' e devolve o id.
    `data` é AAAA-MM-DD válida; nome e local de 1 a 100 caracteres; sem centro,
    usa CENTRO_PADRAO; lat em [-90, 90] e lon em [-180, 180]. Senão dados_invalidos."""
    nome, local = _aparar(nome), _aparar(local)
    _exigir_texto(nome, 100, "O nome da operação deve ter de 1 a 100 caracteres.")
    _exigir_texto(local, 100, "O local da operação deve ter de 1 a 100 caracteres.")
    if not _data_valida(data):
        raise ErroDeNegocio("dados_invalidos", "A data deve estar no formato AAAA-MM-DD.")
    centro_lat, centro_lon = _centro_valido(centro_lat, centro_lon)
    return repo.inserir_operacao(nome, data, local, centro_lat, centro_lon)


def listar_operacoes(repo: Repositorio) -> list[dict]:
    """US02. {id, nome, data, local, situacao, centro_lat, centro_lon, inscritos}."""
    return repo.listar_operacoes()


def obter_operacao(repo: Repositorio, operacao_id: int) -> dict:
    """{id, nome, data, local, situacao, centro_lat, centro_lon}. Senão operacao_inexistente."""
    operacao = repo.buscar_operacao(operacao_id)
    if operacao is None:
        raise ErroDeNegocio("operacao_inexistente", "Esta operação não existe.")
    return operacao


def proxima_situacao(situacao: str) -> str | None:
    """R6. A única transição válida a partir de `situacao`, ou None se encerrada.
    A página mostra só o botão dessa transição (rótulo em ROTULO_TRANSICAO)."""
    return PROXIMA_SITUACAO.get(situacao)


def avancar_situacao(repo: Repositorio, operacao_id: int) -> str:
    """R6. Avança planejada -> em_curso -> encerrada e devolve a nova situação.
    Encerrada: transicao_invalida. Iniciar com outra já em curso: outra_em_curso.
    Operação que não existe: operacao_inexistente."""
    operacao = obter_operacao(repo, operacao_id)
    nova = proxima_situacao(operacao["situacao"])
    if nova is None:
        raise ErroDeNegocio("transicao_invalida", "Uma operação encerrada não avança mais.")
    try:
        repo.atualizar_situacao(operacao_id, nova)
    except Conflito as conflito:
        raise ErroDeNegocio("outra_em_curso",
                            "Já existe outra operação em curso. Encerre-a antes de iniciar esta."
                            ) from conflito
    return nova


def inscrever(repo: Repositorio, operacao_id: int, operador_id: int, time: str, classe: str,
              dispositivo: str, consentimento: bool) -> int:
    """US03. Inscreve um operador já cadastrado, sem novo cadastro (R1), e devolve o id.
    Ordem das checagens: operacao_inexistente, operacao_encerrada (R6),
    operador_inexistente, sem_consentimento (R5), dados_invalidos (time fora de
    TIMES, classe fora de CLASSES, dispositivo vazio ou com mais de 32 caracteres
    depois de normalizar_dispositivo), inscricao_duplicada (R2) e
    dispositivo_em_uso (R3). R2 e R3 vêm do Conflito do banco."""
    operacao = obter_operacao(repo, operacao_id)
    if operacao["situacao"] == "encerrada":
        raise ErroDeNegocio("operacao_encerrada",
                            "A operação está encerrada e não aceita inscrições.")
    if repo.buscar_operador(operador_id) is None:
        raise ErroDeNegocio("operador_inexistente", "Este operador não está cadastrado.")
    if not consentimento:
        raise ErroDeNegocio("sem_consentimento",
                            "A inscrição exige o consentimento de rastreamento.")
    dispositivo = normalizar_dispositivo(dispositivo)
    _exigir_time_e_classe(time, classe)
    _exigir_texto(dispositivo, 32, "O dispositivo deve ter de 1 a 32 caracteres.")
    try:
        return repo.inserir_inscricao(operacao_id, operador_id, time, classe,
                                      dispositivo, True)
    except Conflito as conflito:
        raise _erro_de_inscricao(repo, conflito, operacao_id, operador_id) from conflito


def alterar_inscricao(repo: Repositorio, inscricao_id: int, time: str, classe: str) -> None:
    """R4. Muda time e classe só na inscrição; o perfil do operador não muda.
    inscricao_inexistente, operacao_encerrada ou dados_invalidos."""
    inscricao = repo.buscar_inscricao(inscricao_id)
    if inscricao is None:
        raise ErroDeNegocio("inscricao_inexistente", "Esta inscrição não existe.")
    if obter_operacao(repo, inscricao["operacao_id"])["situacao"] == "encerrada":
        raise ErroDeNegocio("operacao_encerrada",
                            "A operação está encerrada e não aceita alterações.")
    _exigir_time_e_classe(time, classe)
    repo.atualizar_inscricao(inscricao_id, time, classe)


def listar_inscritos(repo: Repositorio, operacao_id: int) -> list[dict]:
    """US04. {id, operador_id, apelido, nome, time, cor, classe, dispositivo},
    em que `cor` vem de TIMES. operacao_inexistente se a operação não existe."""
    obter_operacao(repo, operacao_id)
    inscritos = repo.listar_inscritos(operacao_id)
    for inscrito in inscritos:
        inscrito["cor"] = TIMES[inscrito["time"]]
    return inscritos


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
    dispositivo = normalizar_dispositivo(dispositivo)
    operacao = repo.operacao_em_curso()
    if operacao is None:
        repo.inserir_descarte(None, dispositivo, "sem_operacao_em_curso", agora.isoformat())
        return "descartado"
    inscricao = repo.inscricao_por_dispositivo(operacao["id"], dispositivo)
    if inscricao is None:
        repo.inserir_descarte(operacao["id"], dispositivo, "sem_inscricao", agora.isoformat())
        return "descartado"
    try:
        repo.inserir_posicao(inscricao["id"], pacote, lat, lon, bateria, agora.isoformat())
    except Conflito:
        return "duplicado"
    return "gravado"


def estado_por_tempo(segundos: float | None, atrasado_s: int, perdido_s: int) -> str:
    """R9. None: sem_sinal; segundos <= atrasado_s: ativo;
    segundos <= perdido_s: atrasado; acima de perdido_s: perdido.
    Com 60/120: 60 s é ativo, 61 s atrasado, 120 s atrasado e 121 s perdido."""
    if segundos is None:
        return "sem_sinal"
    if segundos <= atrasado_s:
        return "ativo"
    return "atrasado" if segundos <= perdido_s else "perdido"


def calcular_rumo(lat1: float, lon1: float, lat2: float, lon2: float) -> float | None:
    """Rumo inicial do ponto 1 para o ponto 2, em graus [0, 360), 0 = norte,
    90 = leste, arredondado a 1 casa. None se os pontos são iguais."""
    if (lat1, lon1) == (lat2, lon2):
        return None
    fi1, fi2, delta = radians(lat1), radians(lat2), radians(lon2 - lon1)
    y = sin(delta) * cos(fi2)
    x = cos(fi1) * sin(fi2) - sin(fi1) * cos(fi2) * cos(delta)
    graus = round(degrees(atan2(y, x)) % 360, 1)
    return graus % 360    # 359,97 arredonda para 360,0, que volta a ser 0,0


def _segundos_desde(recebido_em: str | None, agora: datetime) -> int | None:
    """Parte inteira dos segundos entre `recebido_em` (ISO 8601) e `agora`; None sem sinal."""
    if recebido_em is None:
        return None
    recebido = datetime.fromisoformat(recebido_em)
    return max(0, int((agora - recebido).total_seconds()))


def _rumo_das_posicoes(posicoes: list[dict]) -> float | None:
    """Rumo do par mais recente de posições distintas (a mais nova primeiro na lista).
    Se o operador parou, a posição repetida é pulada e vale o último movimento."""
    if not posicoes:
        return None
    atual = posicoes[0]
    for anterior in posicoes[1:]:
        if (anterior["lat"], anterior["lon"]) != (atual["lat"], atual["lon"]):
            return calcular_rumo(anterior["lat"], anterior["lon"], atual["lat"], atual["lon"])
    return None


def _situacao_do_inscrito(repo: Repositorio, inscrito: dict, agora: datetime,
                          atrasado_s: int, perdido_s: int) -> dict:
    posicoes = repo.ultimas_posicoes(inscrito["id"], 10)
    ultima = posicoes[0] if posicoes else {}
    segundos = _segundos_desde(ultima.get("recebido_em"), agora)
    return {
        "inscricao_id": inscrito["id"], "apelido": inscrito["apelido"],
        "time": inscrito["time"], "cor": inscrito["cor"], "classe": inscrito["classe"],
        "dispositivo": inscrito["dispositivo"],
        "estado": estado_por_tempo(segundos, atrasado_s, perdido_s), "segundos": segundos,
        "lat": ultima.get("lat"), "lon": ultima.get("lon"), "bateria": ultima.get("bateria"),
        "rumo": _rumo_das_posicoes(posicoes),
    }


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
    operacao = obter_operacao(repo, operacao_id)
    inscritos = [_situacao_do_inscrito(repo, inscrito, agora, atrasado_s, perdido_s)
                 for inscrito in listar_inscritos(repo, operacao_id)]
    return {"operacao": operacao,
            "descartados": repo.contar_descartes(operacao_id),
            "inscritos": inscritos}


def situacao_em_curso(repo: Repositorio, agora: datetime, atrasado_s: int,
                      perdido_s: int) -> dict | None:
    """situacao_da_operacao da operação em curso, ou None se não há operação em curso."""
    operacao = repo.operacao_em_curso()
    if operacao is None:
        return None
    return situacao_da_operacao(repo, operacao["id"], agora, atrasado_s, perdido_s)


# ------------------------------------------------------ usuários (US07, R10)

def criar_usuario(repo: Repositorio, login: str, senha: str, papel: str) -> int:
    """US07. Grava o usuário com a senha em hash (werkzeug.security.generate_password_hash).
    login de 3 a 32 caracteres [a-z0-9_.-]; senha com pelo menos 8 caracteres
    (senão dados_invalidos); papel fora de PAPEIS: papel_invalido; login repetido:
    login_duplicado."""
    if not isinstance(login, str) or not re.fullmatch(r"[a-z0-9_.-]{3,32}", login):
        raise ErroDeNegocio("dados_invalidos",
                            "O login deve ter de 3 a 32 caracteres: a-z, 0-9, ponto, hífen ou _.")
    if not isinstance(senha, str) or len(senha) < 8:
        raise ErroDeNegocio("dados_invalidos", "A senha deve ter pelo menos 8 caracteres.")
    if papel not in PAPEIS:
        raise ErroDeNegocio("papel_invalido", "O papel deve ser organizador ou observador.")
    try:
        return repo.inserir_usuario(login, generate_password_hash(senha), papel)
    except Conflito as conflito:
        raise ErroDeNegocio("login_duplicado", "Já existe um usuário com este login."
                            ) from conflito


_HASH_FALSO: str | None = None


def _hash_falso() -> str:
    """Hash de uma senha que ninguém usa, gerado na primeira vez e guardado no módulo."""
    global _HASH_FALSO
    if _HASH_FALSO is None:
        _HASH_FALSO = generate_password_hash("senha-que-ninguem-usa")
    return _HASH_FALSO


def autenticar(repo: Repositorio, login: str, senha: str) -> dict | None:
    """US07. {id, login, papel} se login e senha conferem
    (werkzeug.security.check_password_hash), senão None."""
    if not isinstance(login, str) or not isinstance(senha, str):
        return None
    usuario = repo.buscar_usuario_por_login(login)
    # Sem usuário, confere contra um hash falso: o tempo não revela quais logins existem.
    hash_conferido = usuario["senha_hash"] if usuario else _hash_falso()
    senha_confere = check_password_hash(hash_conferido, senha)
    if usuario is None or not senha_confere:
        return None
    return {"id": usuario["id"], "login": usuario["login"], "papel": usuario["papel"]}
