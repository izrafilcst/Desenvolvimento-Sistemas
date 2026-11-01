#!/usr/bin/env python3
"""Preenche uma cópia do Kit da Aula 10 com o texto que já está nos documentos.

Os textos das Fichas 11 e 12 e da tabela de âncoras vêm de
docs/hipoteses-e-incrementos.md e foram copiados literalmente para as
constantes abaixo. A Ficha 13 (docs/historias.md) só é citada pelo caminho.

Uso:
    python scripts/preencher_kit.py [--modelo CAMINHO] [--destino CAMINHO]

O modelo nunca é alterado: o script grava sempre em outro arquivo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parents[1]
NOME_MODELO = (
    "Kit_Artefatos_Aula_10_Jornada_do_Conhecimento_Ciclo_2_CEUB_v1.2.xlsx"
)
MODELO_PADRAO = RAIZ.parent / NOME_MODELO
DESTINO_PADRAO = RAIZ / "docs" / "Kit_Aula10_MeshTracker_Central.xlsx"

DATA_REVISAO = "01/11/2026"

# --- 02_Book_Fichas: controle do Book (Fichas 1 a 20) -----------------------

LINHA_FICHA_1 = 5  # a Ficha n fica na linha 4 + n
FICHAS_SIM = 13  # Fichas 1 a 13
FICHAS_TOTAL = 20

CADERNO = f"docs/Caderno_Aula7_MeshTracker_Central.pdf (v2, {DATA_REVISAO})"

# Coluna F (Link / hash / observação), por ficha.
OBSERVACAO_BOOK = {
    1: CADERNO,
    2: CADERNO + "; Feira não realizada (dinâmica em sala)",
    3: CADERNO + "; entrevista não realizada",
    4: CADERNO,
    5: CADERNO + "; pitch v2 por revisão própria, semáforo não realizado",
    6: CADERNO,
    7: CADERNO + "; leitura do CEUBOOK ainda não registrada",
    8: CADERNO,
    9: "github.com/izrafilcst/Desenvolvimento-Sistemas, commit 604b85b",
    10: CADERNO + "; link não testado por colega",
    11: "docs/hipoteses-e-incrementos.md",
    12: "docs/hipoteses-e-incrementos.md",
    13: "docs/historias.md",
}

# --- 03_Ancoras_Decisoes: coluna F, na ordem das linhas 5 a 8 --------------

DECISOES_ANCORAS = [
    # Pressman e Maxim
    "Cada incremento termina em go/no-go registrado na Ficha 16, "
    "com critério definido antes.",
    # Sommerville
    "O recorte em 3 incrementos (2.3.2), a máquina de estados da operação "
    "e do operador (5.4.2) e as camadas rotas → serviços → repositório "
    "(6.3.1).",
    # Cohn
    "O backlog em histórias com critérios de aceitação e iterações de "
    "duas semanas.",
    # Gothelf e Seiden
    "As hipóteses H1 a H4 com sinal mensurável e a validação com o "
    "organizador antes de crescer o escopo.",
]

# --- 04_Ficha11_Hipoteses: "Minha equipe", linhas 12 a 15 -------------------
# (B, C, D, E, risco, incerteza, incremento)

HIPOTESES = [
    (  # H1
        "manter o perfil permanente do operador e inscrevê-lo por operação "
        "elimina o recadastro",
        "Organizador",
        "o organizador inscreve 5 operadores já cadastrados numa 2ª operação "
        "sem redigitar dados pessoais, em até 3 min",
        "Roteiro cronometrado no Incremento 1, executado pelo autor no papel "
        "de organizador, com gravação de tela",
        "Alto",
        3,
        1,
    ),
    (  # H2
        "ver cada operador no mapa com o estado (ativo, atrasado, perdido) "
        "faz o organizador perceber quem ficou sem contato",
        "Organizador",
        "no roteiro, quem está perdido e há quanto tempo é apontado em até "
        "10 s depois de abrir o mapa",
        "Roteiro cronometrado com 5 operadores simulados na Aula 15 "
        "(Ficha 18), executado pelo autor no papel de organizador",
        "Alto",
        3,
        2,
    ),
    (  # H3
        "aceitar só sinais de inscritos com consentimento e restringir o "
        "observador à leitura protege a posição de quem não deveria ser "
        "rastreado",
        "Organizador e operadores",
        "nenhum sinal de não inscrito vira posição e nenhuma escrita do "
        "observador passa, nos testes",
        "Testes automatizados",
        "Médio",
        2,
        2,
    ),
    (  # H4
        "expor a situação e o recebimento de sinais em `/api/v1` permite "
        "trocar o simulador pelo gateway real sem mudar a regra",
        "Organizador (e o futuro gateway)",
        "o simulador e um cliente `curl` usam só a API, sem tocar no banco",
        "Teste de API e reprodução pelo Guia",
        "Baixo",
        2,
        3,
    ),
]

RISCOS_VALIDOS = ("Alto", "Médio", "Baixo")
LINHA_H1 = 12

# --- 05_Ficha12_Incrementos: "Minha equipe", linhas 11 a 13 ----------------
# (C Entrega, D Hipóteses, E Critério de aceitação, F Go/no-go)

INCREMENTOS = [
    (  # Incremento 1
        "Cadastro do operador, operação com situação e inscrição por "
        "operação, persistidos",
        "H1",
        "R1 a R6 testadas; dados persistem após reiniciar; roteiro do "
        "Incremento 1 demonstrado (cadastrar 5 operadores, inscrevê-los na "
        "operação 1 e depois na 2, e mostrar a recusa da inscrição "
        "duplicada, do dispositivo repetido e da inscrição sem "
        "consentimento)",
        "Go se os testes estiverem verdes e o roteiro da H1 for cumprido em "
        "até 3 min, com a gravação como evidência",
    ),
    (  # Incremento 2
        "Simulador, sinais filtrados e sem duplicata, estado do operador, "
        "mapa ao vivo e papel de observador",
        "H2 · H3",
        "R7 a R10 testadas; roteiro do Incremento 2 demonstrado (5 inscritos "
        "simulados e um dispositivo não inscrito, marcadores que se movem "
        "sem recarregar, estados atrasado e perdido)",
        "Go se, no roteiro, o operador perdido for apontado em até 10 s e "
        "nenhuma escrita indevida passar nos testes",
    ),
    (  # Incremento 3
        "`/api/v1` documentada com token, Guia de reprodução e release v1.0",
        "H4",
        "Endpoints em `docs/api.md`; 401 sem token; tag `v1.0`",
        "Go para o Demo Day se o MVP for reproduzido do zero, num clone "
        "limpo e num venv novo, seguindo só o Guia",
    ),
]

LINHA_INCREMENTO_1 = 11

ALTURA_LINHA = 14.4  # altura de uma linha de texto no modelo


def _exigir_aba(wb, nome: str):
    if nome not in wb.sheetnames:
        raise ValueError(f"O modelo não tem a aba {nome!r}.")
    return wb[nome]


def _exigir_valor(ws, coordenada: str, esperado: str) -> None:
    atual = ws[coordenada].value
    if atual != esperado:
        raise ValueError(
            f"{ws.title}!{coordenada} deveria ser {esperado!r} no modelo, "
            f"mas é {atual!r}. O modelo mudou?"
        )


def _validar_dados() -> None:
    """Confere as constantes antes de tocar na planilha."""
    if sorted(OBSERVACAO_BOOK) != list(range(1, FICHAS_SIM + 1)):
        raise ValueError("OBSERVACAO_BOOK deve cobrir as Fichas 1 a 13.")
    if len(DECISOES_ANCORAS) != 4:
        raise ValueError("São 4 âncoras: Pressman, Sommerville, Cohn, Gothelf.")
    if len(HIPOTESES) != 4 or len(INCREMENTOS) != 3:
        raise ValueError("São 4 hipóteses e 3 incrementos.")
    for h, (b, c, d, e, risco, incerteza, incremento) in enumerate(
        HIPOTESES, start=1
    ):
        if risco not in RISCOS_VALIDOS:
            raise ValueError(f"H{h}: risco {risco!r} fora de {RISCOS_VALIDOS}.")
        if not all((b, c, d, e)):
            raise ValueError(f"H{h}: texto vazio.")
        for nome, valor, minimo, maximo in (
            ("incerteza", incerteza, 1, 3),
            ("incremento", incremento, 1, 3),
        ):
            if type(valor) is not int or not minimo <= valor <= maximo:
                raise ValueError(f"H{h}: {nome} deve ser inteiro de 1 a 3.")
    for n, campos in enumerate(INCREMENTOS, start=1):
        if not all(campos):
            raise ValueError(f"Incremento {n}: texto vazio.")


def _linhas_necessarias(texto: str, largura: float) -> int:
    """Estima quantas linhas o texto ocupa numa coluna com quebra automática."""
    por_linha = max(1, int(largura * 1.05))
    total = 0
    for trecho in str(texto).split("\n"):
        linhas, usado = 1, 0
        for palavra in trecho.split():
            tamanho = len(palavra)
            if usado and usado + 1 + tamanho > por_linha:
                linhas += 1
                usado = tamanho
            else:
                usado += tamanho + (1 if usado else 0)
        total += linhas
    return total


def _ajustar_altura(ws, linha: int, colunas: str) -> None:
    """Aumenta a altura da linha (nunca diminui) para o texto não ser cortado.

    O modelo traz alturas fixas pensadas para o exemplo do professor.
    """
    maximo = 1
    for letra in colunas:
        valor = ws[f"{letra}{linha}"].value
        if isinstance(valor, str) and not valor.startswith("="):
            largura = ws.column_dimensions[letra].width or 8.43
            maximo = max(maximo, _linhas_necessarias(valor, largura))
    altura = ALTURA_LINHA * maximo + 3
    atual = ws.row_dimensions[linha].height or ALTURA_LINHA
    if altura > atual:
        ws.row_dimensions[linha].height = altura


def _preencher_book(wb) -> None:
    ws = _exigir_aba(wb, "02_Book_Fichas")
    _exigir_valor(ws, "B5", "Aquecimento")
    _exigir_valor(ws, "B24", "Retrospectiva e pitch final")
    for ficha in range(1, FICHAS_TOTAL + 1):
        linha = LINHA_FICHA_1 + ficha - 1
        concluida = ficha <= FICHAS_SIM
        ws[f"E{linha}"] = "Sim" if concluida else "Não"
        if concluida:
            ws[f"F{linha}"] = OBSERVACAO_BOOK[ficha]
            _ajustar_altura(ws, linha, "F")


def _preencher_ancoras(wb) -> None:
    ws = _exigir_aba(wb, "03_Ancoras_Decisoes")
    _exigir_valor(ws, "A5", "PRESSMAN & MAXIM (2021)")
    _exigir_valor(ws, "A8", "GOTHELF & SEIDEN (2022)")
    for deslocamento, decisao in enumerate(DECISOES_ANCORAS):
        ws[f"F{5 + deslocamento}"] = decisao
        _ajustar_altura(ws, 5 + deslocamento, "F")


def _preencher_hipoteses(wb) -> None:
    ws = _exigir_aba(wb, "04_Ficha11_Hipoteses")
    _exigir_valor(ws, "A11", "Minha equipe")
    for deslocamento, (b, c, d, e, risco, incerteza, incremento) in enumerate(
        HIPOTESES
    ):
        linha = LINHA_H1 + deslocamento
        _exigir_valor(ws, f"A{linha}", f"H{deslocamento + 1}")
        ws[f"B{linha}"] = b
        ws[f"C{linha}"] = c
        ws[f"D{linha}"] = d
        ws[f"E{linha}"] = e
        ws[f"F{linha}"] = risco
        ws[f"G{linha}"] = incerteza
        # A coluna H guarda a fórmula de prioridade e não é tocada.
        ws[f"I{linha}"] = incremento
        _ajustar_altura(ws, linha, "BCDE")


def _preencher_incrementos(wb) -> None:
    ws = _exigir_aba(wb, "05_Ficha12_Incrementos")
    _exigir_valor(ws, "A10", "Minha equipe")
    for deslocamento, (entrega, hipoteses, criterio, go) in enumerate(
        INCREMENTOS
    ):
        linha = LINHA_INCREMENTO_1 + deslocamento
        _exigir_valor(ws, f"A{linha}", f"Incremento {deslocamento + 1}")
        ws[f"C{linha}"] = entrega
        ws[f"D{linha}"] = hipoteses
        ws[f"E{linha}"] = criterio
        ws[f"F{linha}"] = go
        _ajustar_altura(ws, linha, "CDEF")
    # A Definição de Pronto (E16:E21) fica em branco: é preenchida em cada
    # go/no-go.


def preencher(modelo: Path, destino: Path) -> None:
    """Grava em `destino` uma cópia preenchida de `modelo`."""
    modelo = Path(modelo).expanduser().resolve()
    destino = Path(destino).expanduser().resolve()
    if not modelo.is_file():
        raise FileNotFoundError(f"Modelo não encontrado: {modelo}")
    if destino == modelo:
        raise ValueError("O destino não pode ser o próprio modelo.")
    if not destino.parent.is_dir():
        raise FileNotFoundError(f"Pasta de destino inexistente: {destino.parent}")

    _validar_dados()
    wb = load_workbook(modelo)  # mantém as fórmulas
    _preencher_book(wb)
    _preencher_ancoras(wb)
    _preencher_hipoteses(wb)
    _preencher_incrementos(wb)
    wb.calculation.fullCalcOnLoad = True  # o Excel recalcula ao abrir
    wb.save(destino)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preenche o Kit da Aula 10 do MeshTracker Central."
    )
    parser.add_argument(
        "--modelo",
        type=Path,
        default=MODELO_PADRAO,
        help=f"planilha modelo (padrão: {MODELO_PADRAO})",
    )
    parser.add_argument(
        "--destino",
        type=Path,
        default=DESTINO_PADRAO,
        help=f"planilha gerada (padrão: {DESTINO_PADRAO})",
    )
    args = parser.parse_args(argv)
    try:
        preencher(args.modelo, args.destino)
    except (OSError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    print(f"Kit gravado em {args.destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
