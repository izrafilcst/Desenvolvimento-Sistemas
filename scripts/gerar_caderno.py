#!/usr/bin/env python3
"""Gera o Caderno da Aula 7 (versão 2) em .docx e o converte para PDF.

O .docx da versão 1, feito no Word, não está mais disponível. Este script
recria o layout com python-docx. O texto fica em caderno_conteudo.py e
caderno_conteudo_fichas.py; aqui ficam só o layout e a conversão.

Uso:
    python scripts/gerar_caderno.py

Gera docs/Caderno_Aula7_MeshTracker_Central.docx (fora do git) e o PDF ao
lado dele, convertido pelo LibreOffice (soffice).

Marcação aceita nos textos: **negrito**, *itálico*, `código` e \\n para
quebra de linha. Em tabelas de duas colunas, a primeira coluna é de rótulos
(negrito, fundo cinza), a não ser que comece com ☐ ou ☒.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

PASTA_SCRIPTS = Path(__file__).resolve().parent
if str(PASTA_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PASTA_SCRIPTS))

from caderno_conteudo import AUTOR, CAPA, SECOES, TITULO  # noqa: E402

RAIZ = PASTA_SCRIPTS.parent
LOGO = PASTA_SCRIPTS / "assets" / "logo_ceub.png"
DOCX_PADRAO = RAIZ / "docs" / "Caderno_Aula7_MeshTracker_Central.docx"

CABECALHO = (
    "Faculdade de Tecnologia e Ciências Sociais Aplicada – FATECS",
    "Curso de Engenharia de Computação",
)

# A4, margens de 3 cm (superior e esquerda) e 2 cm (inferior e direita).
MARGEM_SUP, MARGEM_ESQ, MARGEM_INF, MARGEM_DIR = 3.0, 3.0, 2.0, 2.0
LARGURA_UTIL = 21.0 - MARGEM_ESQ - MARGEM_DIR  # 16 cm
LARGURA_LOGO = 4.5
# Como na versão 1, o logo encosta na borda de cima da página: as linhas
# magenta do desenho saem pela borda superior da imagem.
DISTANCIA_CABECALHO = 0.0
RECUO_CABECALHO = 34  # pt até a primeira linha da FATECS

FONTE = "Arial"
FONTE_CABECALHO = "Calibri"
FONTE_CAIXAS = "DejaVu Sans"  # ☐ e ☒ não existem no Arial
FONTE_CODIGO = "Consolas"
CAIXAS = "☐☒"

CINZA_CABECALHO = "D9D9D9"
CINZA_NOTA = "F2F2F2"
COR_BORDA = "808080"
COR_LEGENDA = RGBColor(0x59, 0x59, 0x59)

ESQUERDA = WD_ALIGN_PARAGRAPH.LEFT
CENTRO = WD_ALIGN_PARAGRAPH.CENTER
DIREITA = WD_ALIGN_PARAGRAPH.RIGHT
JUSTIFICADO = WD_ALIGN_PARAGRAPH.JUSTIFY

# Estimativa da largura do texto em Arial 10, para dividir as colunas.
CM_POR_CARACTERE = 0.185
FOLGA_CELULA = 0.45
MINIMO_COLUNA = 1.0
MINIMO_ROTULO = 4.2
MAXIMO_CENTRALIZADO = 10  # colunas só com textos curtos ficam centralizadas

MARCAS = re.compile(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*|`[^`]+`|[☐☒]|\n)")


# --- Texto ------------------------------------------------------------------

def _fonte(run, nome=FONTE, tamanho=None, negrito=None, italico=None):
    """Aplica a fonte nos quatro atributos de w:rFonts."""
    rfonts = run._element.get_or_add_rPr().get_or_add_rFonts()
    for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(atributo), nome)
    if tamanho:
        run.font.size = Pt(tamanho)
    if negrito is not None:
        run.bold = negrito
    if italico is not None:
        run.italic = italico


def _escrever(par, texto, tamanho, negrito=False, italico=False):
    """Escreve o texto no parágrafo, interpretando a marcação simples."""
    for pedaco in MARCAS.split(texto):
        if not pedaco:
            continue
        if pedaco == "\n":
            par.add_run().add_break()
            continue
        nome, b, i, t = FONTE, negrito, italico, tamanho
        if len(pedaco) > 4 and pedaco.startswith("**") and pedaco.endswith("**"):
            pedaco, b = pedaco[2:-2], True
        elif len(pedaco) > 2 and pedaco.startswith("`"):
            pedaco, nome, t = pedaco[1:-1], FONTE_CODIGO, tamanho - 1
        elif pedaco in CAIXAS:
            nome = FONTE_CAIXAS
        elif len(pedaco) > 2 and pedaco.startswith("*") and pedaco.endswith("*"):
            pedaco, i = pedaco[1:-1], True
        _fonte(par.add_run(pedaco), nome, t, b, i)


def _sem_marcas(texto):
    return texto.replace("**", "").replace("`", "")


def _formatar(par, alinhamento=ESQUERDA, entrelinha=1.0, antes=0.0,
              depois=0.0, recuo=0.0, esquerda=0.0, juntar=False):
    """Formata o parágrafo; espaços em pontos e recuos em cm."""
    pf = par.paragraph_format
    pf.alignment = alinhamento
    pf.line_spacing = entrelinha
    pf.space_before = Pt(antes)
    pf.space_after = Pt(depois)
    pf.first_line_indent = Cm(recuo)
    pf.left_indent = Cm(esquerda)
    pf.keep_with_next = juntar
    pf.widow_control = True


# --- Tabelas ----------------------------------------------------------------

def _twips(cm):
    return str(int(round(cm * 567)))


def _elemento(tag, **atributos):
    el = OxmlElement(tag)
    for nome, valor in atributos.items():
        el.set(qn(f"w:{nome}"), str(valor))
    return el


def _sombrear(celula, cor):
    celula._tc.get_or_add_tcPr().append(
        _elemento("w:shd", val="clear", color="auto", fill=cor))


def _preparar_tabela(tabela, larguras, cor_borda=COR_BORDA, margem=100,
                     vertical=28):
    """Largura fixa por coluna, bordas finas e margens internas."""
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabela.autofit = False
    tblPr = tabela._tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    tblW.set(qn("w:type"), "dxa")
    tblW.set(qn("w:w"), _twips(sum(larguras)))
    if cor_borda:
        bordas = OxmlElement("w:tblBorders")
        for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
            bordas.append(_elemento(f"w:{lado}", val="single", sz=4,
                                    space=0, color=cor_borda))
        tblPr.insert_element_before(bordas, "w:shd", "w:tblLayout",
                                    "w:tblCellMar", "w:tblLook")
    margens = OxmlElement("w:tblCellMar")
    for lado, valor in (("top", vertical), ("left", margem),
                        ("bottom", vertical), ("right", margem)):
        margens.append(_elemento(f"w:{lado}", w=valor, type="dxa"))
    tblPr.insert_element_before(margens, "w:tblLook")
    for coluna, largura in zip(tabela._tbl.tblGrid.findall(qn("w:gridCol")),
                               larguras):
        coluna.set(qn("w:w"), _twips(largura))


def _larguras(cabecalho, linhas, rotulos):
    """Divide os 16 cm entre as colunas, como o layout automático do HTML:
    cada coluna tem um mínimo (a palavra mais longa) e um máximo (a linha
    mais longa), e a sobra é repartida na proporção da diferença."""
    minimos, maximos = [], []
    for j in range(len(linhas[0])):
        textos = [_sem_marcas(linha[j]) for linha in linhas]
        palavra = max((len(p) for t in textos for p in t.split()), default=1)
        trecho = max((len(p) for t in textos for p in t.split("\n")), default=1)
        if cabecalho:
            titulo = _sem_marcas(cabecalho[j])
            curto = len(titulo) if len(titulo) <= 12 else max(
                len(p) for p in titulo.split())
            palavra = max(palavra, curto * 1.2)  # negrito é mais largo
            trecho = max(trecho, len(titulo) * 1.2)
        piso = MINIMO_ROTULO if rotulos and j == 0 else MINIMO_COLUNA
        minimo = max(palavra * CM_POR_CARACTERE + FOLGA_CELULA, piso)
        minimos.append(minimo)
        maximos.append(max(trecho * CM_POR_CARACTERE + FOLGA_CELULA, minimo))
    soma_min, soma_max = sum(minimos), sum(maximos)
    if soma_max <= LARGURA_UTIL:
        return [m * LARGURA_UTIL / soma_max for m in maximos]
    if soma_min >= LARGURA_UTIL:
        return [m * LARGURA_UTIL / soma_min for m in minimos]
    fator = (LARGURA_UTIL - soma_min) / (soma_max - soma_min)
    return [a + (b - a) * fator for a, b in zip(minimos, maximos)]


def _caixa(doc, escrever, cor=CINZA_NOTA, borda="BFBFBF"):
    """Caixa de uma célula com fundo cinza (nota ou código)."""
    tabela = doc.add_table(rows=1, cols=1)
    _preparar_tabela(tabela, [LARGURA_UTIL], cor_borda=borda, margem=140)
    tabela.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    celula = tabela.rows[0].cells[0]
    celula.width = Cm(LARGURA_UTIL)
    _sombrear(celula, cor)
    escrever(celula)
    return tabela


# --- Documento --------------------------------------------------------------

class _Caderno:
    """Monta o documento bloco a bloco."""

    def __init__(self):
        self.doc = Document()
        self.quebrar = False  # a próxima página começa no próximo bloco
        self.referencias = False
        self._configurar()

    def _configurar(self):
        normal = self.doc.styles["Normal"]
        normal.font.size = Pt(12)
        rpr = normal.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(atributo), FONTE)
        rpr.append(_elemento("w:lang", val="pt-BR", eastAsia="pt-BR",
                             bidi="ar-SA"))
        secao = self.doc.sections[0]
        secao.page_width, secao.page_height = Cm(21.0), Cm(29.7)
        secao.top_margin, secao.left_margin = Cm(MARGEM_SUP), Cm(MARGEM_ESQ)
        secao.bottom_margin = Cm(MARGEM_INF)
        secao.right_margin = Cm(MARGEM_DIR)
        secao.header_distance = Cm(DISTANCIA_CABECALHO)
        secao.footer_distance = Cm(1.25)
        self._cabecalho(secao)
        propriedades = self.doc.core_properties
        propriedades.title = TITULO
        propriedades.author = propriedades.last_modified_by = AUTOR
        propriedades.comments = propriedades.subject = ""
        propriedades.keywords = propriedades.category = ""
        propriedades.language = "pt-BR"
        propriedades.created = propriedades.modified = datetime.now()

    def _cabecalho(self, secao):
        """Textos da FATECS à esquerda e logo à direita, em todas as páginas."""
        cabecalho = secao.header
        esquerda = LARGURA_UTIL - LARGURA_LOGO
        tabela = cabecalho.add_table(1, 2, Cm(LARGURA_UTIL))
        _preparar_tabela(tabela, [esquerda, LARGURA_LOGO], cor_borda=None,
                         margem=0, vertical=0)
        tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
        vazio = cabecalho.paragraphs[0]
        vazio._p.addprevious(tabela._tbl)
        _formatar(vazio, entrelinha=Pt(1))
        texto, logo = tabela.rows[0].cells
        texto.width, logo.width = Cm(esquerda), Cm(LARGURA_LOGO)
        texto.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        for n, linha in enumerate(CABECALHO):
            par = texto.paragraphs[0] if n == 0 else texto.add_paragraph()
            _formatar(par, antes=RECUO_CABECALHO if n == 0 else 0,
                      depois=10 if n == 0 else 0)
            _fonte(par.add_run(linha), FONTE_CABECALHO, 9)
        par = logo.paragraphs[0]
        _formatar(par, DIREITA)
        par.add_run().add_picture(str(LOGO), width=Cm(LARGURA_LOGO))

    def _paragrafo(self):
        par = self.doc.add_paragraph()
        if self.quebrar:
            par.paragraph_format.page_break_before = True
            self.quebrar = False
        return par

    def _espaco(self, pontos=6):
        """Parágrafo pequeno depois de cada tabela (e entre duas tabelas)."""
        par = self.doc.add_paragraph()
        _formatar(par, entrelinha=Pt(pontos))
        par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY

    def _quebra_na_tabela(self, tabela):
        if self.quebrar:
            primeira = tabela.rows[0].cells[0].paragraphs[0]
            primeira.paragraph_format.page_break_before = True
            self.quebrar = False

    def capa(self):
        def linha(texto, tamanho=12, negrito=False, italico=False,
                  alinhar=CENTRO, antes=0.0):
            par = self.doc.add_paragraph()
            _formatar(par, alinhar, 1.5, antes=antes)
            _escrever(par, texto, tamanho, negrito, italico)

        for n, texto in enumerate(CAPA["disciplina"]):
            linha(texto, antes=40 if n == 0 else 0)
        linha(CAPA["titulo"], 16, negrito=True, antes=150)
        linha(CAPA["projeto"], 13, negrito=True)
        linha(CAPA["subtitulo"], 11, italico=True)
        linha(CAPA["versao"], 11, antes=6)
        for n, texto in enumerate(CAPA["aluno"]):
            linha(texto, alinhar=ESQUERDA, antes=110 if n == 0 else 6)
        linha(CAPA["local_data"], antes=150)  # pé da capa, como na versão 1
        self.quebrar = True

    def titulo(self, texto):
        self.referencias = "REFERÊNCIAS" in texto
        par = self._paragrafo()
        _formatar(par, antes=12, depois=6, juntar=True)
        _escrever(par, texto.upper(), 14, negrito=True)

    def subtitulo(self, texto):
        par = self._paragrafo()
        _formatar(par, antes=10, depois=4, juntar=True)
        _escrever(par, texto, 12, negrito=True)

    def paragrafo(self, texto):
        par = self._paragrafo()
        if self.referencias:  # ABNT: alinhadas à esquerda, espaço simples
            _formatar(par, entrelinha=1.0, depois=8)
        else:
            _formatar(par, JUSTIFICADO, 1.5, recuo=1.25)
        _escrever(par, texto, 12)

    def legenda(self, texto):
        par = self._paragrafo()
        _formatar(par, JUSTIFICADO, depois=4, juntar=True)
        _escrever(par, texto, 10, italico=True)
        for run in par.runs:
            run.font.color.rgb = COR_LEGENDA

    def lista(self, itens):
        for n, item in enumerate(itens, 1):
            par = self._paragrafo()
            _formatar(par, JUSTIFICADO, 1.15, depois=4, esquerda=0.63)
            _escrever(par, f"{n}. {item}", 12)

    def nota(self, texto):
        def escrever(celula):
            # Um parágrafo por linha: a quebra de linha num texto justificado
            # espalharia as palavras da linha anterior.
            for n, linha in enumerate(texto.split("\n")):
                par = celula.paragraphs[0] if n == 0 else celula.add_paragraph()
                _formatar(par, JUSTIFICADO, 1.15, antes=2 if n == 0 else 0,
                          depois=2)
                _escrever(par, linha, 11)
        self._quebra_na_tabela(_caixa(self.doc, escrever))
        self._espaco(8)

    def codigo(self, texto):
        def escrever(celula):
            par = celula.paragraphs[0]
            _formatar(par, antes=2, depois=2)
            for n, linha in enumerate(texto.split("\n")):
                if n:
                    par.add_run().add_break()
                _fonte(par.add_run(linha), FONTE_CODIGO, 9.5)
        self._quebra_na_tabela(_caixa(self.doc, escrever))
        self._espaco(8)

    def tabela(self, cabecalho, linhas):
        colunas = len(linhas[0])
        rotulos = colunas == 2 and not any(l[0][:1] in CAIXAS for l in linhas)
        larguras = _larguras(cabecalho, linhas, rotulos)
        centradas = {
            j for j in range(colunas)
            if not (rotulos and j == 0) and all(
                len(_sem_marcas(l[j])) <= MAXIMO_CENTRALIZADO for l in linhas)
        }
        tabela = self.doc.add_table(rows=0, cols=colunas)
        _preparar_tabela(tabela, larguras)
        if cabecalho:
            self._linha(tabela, cabecalho, larguras, centradas, cabecalho=True)
        for linha in linhas:
            self._linha(tabela, linha, larguras, centradas, rotulos=rotulos)
        if cabecalho:  # o cabeçalho não fica sozinho no pé da página
            for celula in tabela.rows[0].cells:
                celula.paragraphs[0].paragraph_format.keep_with_next = True
        self._quebra_na_tabela(tabela)
        self._espaco(8)

    @staticmethod
    def _linha(tabela, textos, larguras, centradas, cabecalho=False,
               rotulos=False):
        linha = tabela.add_row()
        trPr = linha._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if cabecalho:
            trPr.append(OxmlElement("w:tblHeader"))  # repete na outra página
        for j, (celula, texto) in enumerate(zip(linha.cells, textos)):
            celula.width = Cm(larguras[j])
            rotulo = rotulos and j == 0
            if cabecalho:
                _sombrear(celula, CINZA_CABECALHO)
            elif rotulo:
                _sombrear(celula, CINZA_NOTA)
            par = celula.paragraphs[0]
            _formatar(par, CENTRO if j in centradas else ESQUERDA,
                      antes=1, depois=1)
            _escrever(par, texto, 10, negrito=cabecalho or rotulo)

    def quebra(self):
        self.quebrar = True


def gerar_docx(destino: Path) -> Path:
    """Monta o Caderno a partir de SECOES e grava o .docx em destino."""
    caderno = _Caderno()
    caderno.capa()
    for bloco in SECOES:
        tipo, argumentos = bloco[0], bloco[1:]
        metodo = getattr(caderno, tipo, None)
        if metodo is None or tipo.startswith("_") or tipo == "capa":
            raise ValueError(f"Tipo de bloco desconhecido: {tipo!r}")
        metodo(*argumentos)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    caderno.doc.save(destino)
    return destino


def converter_pdf(docx: Path, pasta: Path) -> Path:
    """Converte o .docx em PDF com o LibreOffice e devolve o caminho do PDF."""
    soffice = shutil.which("soffice")
    if soffice is None:
        raise RuntimeError(
            "O comando 'soffice' não foi encontrado. Instale o LibreOffice "
            "(por exemplo, 'sudo apt install libreoffice-writer') e rode o "
            "script de novo; o .docx já foi gerado em " + str(docx))
    docx, pasta = Path(docx).resolve(), Path(pasta).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporaria:
        # Perfil próprio, para funcionar mesmo com o LibreOffice aberto.
        perfil = Path(temporaria, "perfil").as_uri()
        saida = Path(temporaria, "saida")
        resultado = subprocess.run(
            [soffice, f"-env:UserInstallation={perfil}", "--headless",
             "--convert-to", "pdf", "--outdir", str(saida), str(docx)],
            capture_output=True, text=True, check=False)
        gerado = saida / (docx.stem + ".pdf")
        if resultado.returncode != 0 or not gerado.exists():
            raise RuntimeError(
                "O LibreOffice não gerou o PDF. Se a mensagem abaixo for "
                "'source file could not be loaded', confira se o Writer está "
                "instalado (pacote libreoffice-writer).\n" + resultado.stdout
                + resultado.stderr)
        destino = pasta / gerado.name
        shutil.move(str(gerado), destino)
    return destino


def main() -> int:
    docx = gerar_docx(DOCX_PADRAO)
    print(f"DOCX: {docx}")
    try:
        pdf = converter_pdf(docx, docx.parent)
    except RuntimeError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    print(f"PDF:  {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
