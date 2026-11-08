"""Simulador de operadores do MeshTracker Central (mocks da demo, ADR-003).

    python src/simulador.py --url http://127.0.0.1:5000 --token <token>

Sem --token, lê a variável MESHTRACKER_TOKEN. Lê o centro da operação em curso
em GET /api/v1/situacao e, a cada tick (--intervalo, 2 s), manda um sinal por
dispositivo para POST /api/v1/sinais. Os operadores andam com rumo e velocidade
aleatórios dentro de 300 m do centro. Na versão real os sinais virão de um app de
celular ou de um gateway MQTT falando este mesmo contrato HTTP.

Só biblioteca padrão. A lógica fica em funções puras (mover, deve_reenviar, ...)
para testar sem rede; rodar() recebe a função que envia.
"""

import argparse
import http.client
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, replace
from urllib.parse import urlparse

RAIO_M = 300.0                    # os operadores ficam a até 300 m do centro
METROS_POR_GRAU = 111_320.0       # metros por grau de latitude (aproximação)
DESVIO_RUMO = 30.0                # rumo += gauss(0, 30) a cada tick
VELOCIDADE_M_S = (0.5, 2.5)       # velocidade uniforme, em m/s
PROBABILIDADE_PARADO = 0.1        # chance de o operador ficar parado no tick
PROBABILIDADE_REENVIO = 0.1       # chance de reenviar o pacote anterior (R8)
BATERIA_INICIAL = (70.0, 100.0)
DESCARGA_POR_TICK = (0.0, 0.05)   # pontos de bateria perdidos por tick
DISPOSITIVOS_PADRAO = ["MT-01", "MT-02", "MT-03", "MT-04", "MT-05", "MT-99"]  # MT-99 não é inscrito (R7)


class ErroDeUso(Exception):
    """Problema que o usuário resolve (sem operação em curso, token errado...)."""


@dataclass(frozen=True)
class Operador:
    dispositivo: str
    x: float          # metros a leste do centro
    y: float          # metros ao norte do centro
    rumo: float       # graus, 0 = norte, 90 = leste
    bateria: float    # 0 a 100
    pacote: int       # número do último pacote gerado
    ultimo: dict | None = None   # último sinal gerado, para o reenvio


@dataclass(frozen=True)
class Configuracao:
    url: str
    token: str
    dispositivos: list
    centro: tuple                # (lat, lon)
    intervalo: float = 2.0
    parar: str | None = None
    apos: float = 20.0
    ticks: int = 0               # 0 = até Ctrl+C
    pacote_inicial: int = 1


# --------------------------------------------------------- lógica pura

def rumo_para_o_centro(x: float, y: float) -> float:
    """Rumo (graus, 0 = norte) de (x, y) até o centro."""
    return math.degrees(math.atan2(-x, -y)) % 360


def novo_operador(dispositivo: str, rng: random.Random, pacote_inicial: int = 1,
                  raio: float = RAIO_M) -> Operador:
    """Operador numa posição aleatória na metade interna do raio, com bateria cheia o bastante."""
    distancia = raio * 0.5 * math.sqrt(rng.random())
    angulo = rng.uniform(0, 2 * math.pi)
    return Operador(dispositivo, distancia * math.cos(angulo), distancia * math.sin(angulo),
                    rng.uniform(0, 360), rng.uniform(*BATERIA_INICIAL), pacote_inicial - 1)


def mover(op: Operador, rng: random.Random, dt: float = 2.0, raio: float = RAIO_M) -> Operador:
    """Um tick de movimento: o rumo gira gauss(0, 30), a velocidade sai de 0,5 a 2,5 m/s
    e em ~10% dos ticks o operador fica parado. Se o passo sairia do raio, o operador
    vira para o centro e anda nessa direção, então nunca passa da borda."""
    rumo = (op.rumo + rng.gauss(0, DESVIO_RUMO)) % 360
    parado = rng.random() < PROBABILIDADE_PARADO
    passo = rng.uniform(*VELOCIDADE_M_S) * dt
    if parado:
        return replace(op, rumo=rumo)
    x, y = _andar(op.x, op.y, rumo, passo)
    if math.hypot(x, y) > raio:
        rumo = rumo_para_o_centro(op.x, op.y)
        x, y = _andar(op.x, op.y, rumo, passo)
    return replace(op, x=x, y=y, rumo=rumo)


def _andar(x: float, y: float, rumo: float, distancia: float) -> tuple:
    radianos = math.radians(rumo)
    return x + distancia * math.sin(radianos), y + distancia * math.cos(radianos)


def descarregar(bateria: float, rng: random.Random) -> float:
    """A bateria cai devagar e nunca passa de 0."""
    return max(0.0, bateria - rng.uniform(*DESCARGA_POR_TICK))


def deve_reenviar(rng: random.Random, probabilidade: float = PROBABILIDADE_REENVIO) -> bool:
    """R8: com probabilidade 0,1 o sinal anterior é reenviado junto com o novo."""
    return rng.random() < probabilidade


def para_lat_lon(centro: tuple, x: float, y: float) -> tuple:
    """Converte metros a partir do centro em (lat, lon)."""
    lat = centro[0] + y / METROS_POR_GRAU
    lon = centro[1] + x / (METROS_POR_GRAU * math.cos(math.radians(centro[0])))
    return lat, lon


def montar_sinal(op: Operador, centro: tuple) -> dict:
    """Corpo de POST /api/v1/sinais para a situação atual do operador."""
    lat, lon = para_lat_lon(centro, op.x, op.y)
    return {"dispositivo": op.dispositivo, "pacote": op.pacote,
            "lat": round(lat, 6), "lon": round(lon, 6), "bateria": round(op.bateria, 1)}


def ainda_enviando(dispositivo: str, parar: str | None, apos: float, decorrido: float) -> bool:
    """--parar MT-03 --apos 20: o dispositivo some depois de `apos` segundos."""
    return not (parar is not None and dispositivo == parar and decorrido >= apos)


def passo(op: Operador, rng: random.Random, centro: tuple, dt: float) -> tuple:
    """Um tick de um dispositivo. Devolve (operador novo, sinais a enviar): o sinal
    novo e, às vezes, o anterior de novo."""
    op = mover(op, rng, dt)
    op = replace(op, bateria=descarregar(op.bateria, rng), pacote=op.pacote + 1)
    reenviar = deve_reenviar(rng)
    sinal = montar_sinal(op, centro)
    sinais = [sinal] + ([op.ultimo] if reenviar and op.ultimo else [])
    return replace(op, ultimo=sinal), sinais


def descrever(status: int | None, corpo: dict) -> str:
    """O que a linha mostra depois da seta: '201 gravado', '400 Campo ...', 'erro de rede ...'."""
    if status is None:
        return str(corpo.get("erro", "erro de rede"))
    detalhe = corpo.get("status") or corpo.get("erro") or ""
    return f"{status} {detalhe}".strip()


def formatar_linha(hora: str, sinal: dict, status: int | None, corpo: dict) -> str:
    return f"{hora} {sinal['dispositivo']} pacote {sinal['pacote']} -> {descrever(status, corpo)}"


# ------------------------------------------------------------------ rede

def _como_json(bruto: bytes) -> dict:
    try:
        dados = json.loads(bruto.decode("utf-8"))
    except ValueError:
        return {}
    return dados if isinstance(dados, dict) else {}


def chamar(metodo: str, url: str, token: str, corpo: dict | None = None,
           timeout: float = 5.0) -> tuple:
    """Uma requisição HTTP. Devolve (status, json); (None, {"erro": ...}) se a rede falhou."""
    dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
    cabecalhos = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        pedido = urllib.request.Request(url, data=dados, method=metodo, headers=cabecalhos)
        with urllib.request.urlopen(pedido, timeout=timeout) as resposta:
            return resposta.status, _como_json(resposta.read())
    except urllib.error.HTTPError as erro:
        return erro.code, _como_json(erro.read())
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as erro:
        return None, {"erro": f"erro de rede: {getattr(erro, 'reason', erro)}"}


def enviar_sinal(url: str, token: str, sinal: dict) -> tuple:
    return chamar("POST", f"{url}/api/v1/sinais", token, sinal)


def obter_centro(url: str, token: str) -> tuple:
    """(lat, lon) do centro da operação em curso, lido de GET /api/v1/situacao."""
    status, corpo = chamar("GET", f"{url}/api/v1/situacao", token)
    if status is None:
        raise ErroDeUso(f"Não consegui falar com {url}: {corpo['erro']}")
    if status == 401:
        raise ErroDeUso("O servidor recusou o token (401). Confira --token ou MESHTRACKER_TOKEN.")
    if status == 404 and corpo.get("codigo") == "sem_operacao_em_curso":
        raise ErroDeUso("Não há operação em curso. Inicie uma operação no sistema e rode de novo.")
    operacao = corpo.get("operacao") if status == 200 else None
    if not isinstance(operacao, dict):
        raise ErroDeUso(f"Resposta inesperada do servidor ({descrever(status, corpo)}).")
    return operacao["centro_lat"], operacao["centro_lon"]


# ---------------------------------------------------------------- execução

def tick(estados: dict, rng: random.Random, cfg: Configuracao, decorrido: float,
         enviar, escrever, mudos: set) -> None:
    """Um tick de todos os dispositivos: move, envia e escreve uma linha por envio."""
    for dispositivo in cfg.dispositivos:
        estados[dispositivo], sinais = passo(estados[dispositivo], rng, cfg.centro, cfg.intervalo)
        if not ainda_enviando(dispositivo, cfg.parar, cfg.apos, decorrido):
            if dispositivo not in mudos:
                mudos.add(dispositivo)
                escrever(f"{time.strftime('%H:%M:%S')} {dispositivo} parou de enviar (--parar)")
            continue
        for sinal in sinais:
            status, corpo = enviar(cfg.url, cfg.token, sinal)
            escrever(formatar_linha(time.strftime("%H:%M:%S"), sinal, status, corpo))


def rodar(cfg: Configuracao, rng: random.Random, enviar=enviar_sinal, dormir=time.sleep,
          agora=time.monotonic, escrever=lambda texto: print(texto, flush=True)) -> None:
    """Repete tick() a cada cfg.intervalo, por cfg.ticks vezes (0 = sem fim)."""
    estados = {d: novo_operador(d, rng, cfg.pacote_inicial) for d in cfg.dispositivos}
    inicio, mudos, feitos = agora(), set(), 0
    while cfg.ticks == 0 or feitos < cfg.ticks:
        comeco = agora()
        tick(estados, rng, cfg, comeco - inicio, enviar, escrever, mudos)
        feitos += 1
        if cfg.ticks == 0 or feitos < cfg.ticks:
            dormir(max(0.0, cfg.intervalo - (agora() - comeco)))


# --------------------------------------------------------------- terminal

def ler_argumentos(argv: list | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Simula operadores enviando sinais ao MeshTracker Central.")
    ap.add_argument("--url", default="http://127.0.0.1:5000", help="endereço do servidor")
    ap.add_argument("--token", help="token do gateway (padrão: variável MESHTRACKER_TOKEN)")
    ap.add_argument("--dispositivos", nargs="+", default=DISPOSITIVOS_PADRAO,
                    help="dispositivos, separados por espaço ou vírgula (padrão: MT-01 a MT-05 e MT-99)")
    ap.add_argument("--intervalo", type=float, default=2.0, help="segundos entre ticks (padrão 2)")
    ap.add_argument("--parar", help="dispositivo que para de enviar, ex.: MT-03")
    ap.add_argument("--apos", type=float, default=20.0, help="segundos até --parar agir (padrão 20)")
    ap.add_argument("--semente", type=int, help="semente para repetir o mesmo percurso")
    ap.add_argument("--ticks", type=int, default=0, help="para depois de N ticks (padrão: só com Ctrl+C)")
    ap.add_argument("--pacote-inicial", type=int,
                    help="primeiro número de pacote (padrão: a hora atual, para um recomeço não repetir pacotes)")
    return ap.parse_args(argv)


def _dispositivos(brutos: list) -> list:
    """Normaliza como o servidor (tira espaços, maiúsculas) e tira repetidos, mantendo a ordem."""
    nomes = [parte.strip().upper() for bruto in brutos for parte in bruto.split(",")]
    return list(dict.fromkeys(nome for nome in nomes if nome))


def montar_configuracao(args: argparse.Namespace, token: str) -> Configuracao:
    url = args.url.rstrip("/")
    if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
        raise ErroDeUso("--url precisa começar com http:// ou https://")
    if args.intervalo <= 0 or args.apos < 0 or args.ticks < 0:
        raise ErroDeUso("--intervalo precisa ser maior que zero; --apos e --ticks, zero ou mais.")
    dispositivos = _dispositivos(args.dispositivos)
    if not dispositivos:
        raise ErroDeUso("--dispositivos precisa ter ao menos um dispositivo.")
    parar = args.parar.strip().upper() if args.parar else None
    pacote = args.pacote_inicial if args.pacote_inicial is not None else int(time.time())
    return Configuracao(url, token, dispositivos, obter_centro(url, token), args.intervalo,
                        parar, args.apos, args.ticks, max(pacote, 0))


def main(argv: list | None = None) -> int:
    args = ler_argumentos(argv)
    token = args.token or os.environ.get("MESHTRACKER_TOKEN")
    try:
        if not token:
            raise ErroDeUso("Informe o token com --token ou na variável MESHTRACKER_TOKEN.")
        cfg = montar_configuracao(args, token)
        print(f"Centro em {cfg.centro[0]:.5f}, {cfg.centro[1]:.5f}; dispositivos: "
              f"{', '.join(cfg.dispositivos)}. Ctrl+C para parar.", flush=True)
        rodar(cfg, random.Random(args.semente))
    except ErroDeUso as erro:
        print(erro, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Simulador encerrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
