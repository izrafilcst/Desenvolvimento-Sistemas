"""Identidade visual da fase 2 (DESIGN.md): o que dá para conferir sem navegador.

Cobre o contrato entre templates, CSS e JS: tema no <head> sem script inline, seletor fora de
formulário, fontes servidas pelo próprio app, cores de estado iguais às do DESIGN.md, contraste,
Regra do Vermelho Único, Regra do Plano, texto de 16 px e a digitação só no título.
O que só o olho vê (estouro, sobreposição) fica nos prints de docs/design/telas.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

import db
import servicos

RAIZ = Path(__file__).resolve().parent.parent
STATIC = RAIZ / "src" / "static"
APP_CSS = (STATIC / "css" / "app.css").read_text(encoding="utf-8")
MAPA_CSS = (STATIC / "css" / "mapa.css").read_text(encoding="utf-8")
MAPA_JS = (STATIC / "js" / "mapa.js").read_text(encoding="utf-8")
TEMA_JS = (STATIC / "js" / "tema.js").read_text(encoding="utf-8")
DESIGN = (RAIZ / "DESIGN.md").read_text(encoding="utf-8")
ESTADOS = ("ativo", "atrasado", "perdido", "sem-sinal")


# ------------------------------------------------------------------ apoio

@pytest.fixture
def operacao(app):
    """Operação em curso com um inscrito, para as páginas que precisam de id."""
    with app.app_context():
        repo = db.get_repo()
        id_ = servicos.criar_operacao(repo, "Operação Teste", "2026-11-10", "Parque")
        operador = servicos.cadastrar_operador(repo, "op1", "Operador 1", app.config["RELOGIO"]())
        servicos.inscrever(repo, id_, operador, "Azul", "Fuzileiro", "MT-01", True)
        servicos.avancar_situacao(repo, id_)
    return id_


def paginas_logadas(operacao_id: int) -> list[str]:
    return ["/operadores", "/operacoes", f"/operacoes/{operacao_id}", f"/operacoes/{operacao_id}/mapa"]


def html(resposta) -> str:
    return resposta.get_data(as_text=True)


class Seletor(HTMLParser):
    """Anota o seletor de tema e os botões dele, e se estão dentro de algum <form>."""

    def __init__(self):
        super().__init__()
        self.em_form = 0
        self.grupo = None
        self.botoes = []
        self.acoes = []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == "form":
            self.em_form += 1
            self.acoes.append(atributos.get("action"))
        if atributos.get("id") == "seletor-tema":
            self.grupo = {"escondido": "hidden" in atributos, "papel": atributos.get("role"), "em_form": self.em_form > 0}
        if tag == "button" and "data-tema" in atributos:
            self.botoes.append({"tema": atributos["data-tema"], "tipo": atributos.get("type"),
                                "pressionado": atributos.get("aria-pressed"), "em_form": self.em_form > 0})

    def handle_endtag(self, tag):
        if tag == "form":
            self.em_form -= 1


def sem_comentarios_js(codigo: str) -> str:
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", codigo, flags=re.S)


def regras_css(css: str) -> list[tuple[str, str]]:
    """Pares (seletor, corpo) de cada bloco, inclusive os de dentro de @media."""
    limpo = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [(seletor.strip(), corpo) for seletor, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", limpo)]


def declaracoes(corpo: str) -> list[tuple[str, str]]:
    pares = (parte.split(":", 1) for parte in corpo.split(";") if ":" in parte)
    return [(nome.strip(), valor.strip()) for nome, valor in pares]


def cores_do_design() -> dict[str, str]:
    bloco = DESIGN.split("colors:")[1].split("typography:")[0]
    return dict(re.findall(r'^\s+([\w-]+): "(#[0-9a-fA-F]{6})"', bloco, re.M))


def token_css(nome: str) -> str:
    return re.search(rf"--{re.escape(nome)}:\s*(#[0-9a-fA-F]{{6}})\s*;", APP_CSS).group(1).lower()


def par_claro_escuro(nome: str) -> tuple[str, str]:
    achado = re.search(rf"--{re.escape(nome)}:\s*light-dark\(\s*(#[0-9a-fA-F]{{6}}),\s*(#[0-9a-fA-F]{{6}})\s*\)", APP_CSS)
    return achado.group(1).lower(), achado.group(2).lower()


def luminancia(cor: str) -> float:
    canais = [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineares = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lineares[0] + 0.7152 * lineares[1] + 0.0722 * lineares[2]


def contraste(a: str, b: str) -> float:
    claro, escuro = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


# ------------------------------------------------------------------- tema

def test_tema_js_vem_no_head_e_nenhuma_pagina_tem_script_inline(client, org_client, operacao):
    paginas = [html(client.get("/login"))] + [html(org_client.get(url)) for url in paginas_logadas(operacao)]
    for pagina in paginas:
        cabeca = re.search(r"<head>(.*?)</head>", pagina, re.S).group(1)
        assert re.search(r'<script src="/static/js/tema\.js"></script>', cabeca)     # sem defer: aplica antes de pintar
        assert "tema.js" not in pagina.split("</head>")[1]
        assert not re.search(r"<script(?![^>]*\bsrc=)", pagina)                      # a CSP não aceita script inline
        assert not re.search(r"\son[a-z]+\s*=", pagina)


def test_seletor_de_tema_do_observador_fica_fora_de_formularios(obs_client, operacao):
    for url in paginas_logadas(operacao):
        leitor = Seletor()
        leitor.feed(html(obs_client.get(url)))
        assert leitor.grupo == {"escondido": True, "papel": "group", "em_form": False}, url     # sem JS, fica escondido
        assert [b["tema"] for b in leitor.botoes] == ["sistema", "claro", "escuro"], url
        assert all(b["tipo"] == "button" and not b["em_form"] for b in leitor.botoes), url
        assert all(b["pressionado"] in ("true", "false") for b in leitor.botoes), url
        assert leitor.acoes == ["/logout"], url                                      # só o Sair, nenhuma escrita


def test_seletor_de_tema_tambem_aparece_no_login(client):
    leitor = Seletor()
    leitor.feed(html(client.get("/login")))
    assert [b["tema"] for b in leitor.botoes] == ["sistema", "claro", "escuro"]
    assert leitor.acoes == ["/login"] and not leitor.grupo["em_form"]


def test_so_a_pagina_do_mapa_leva_a_classe_pagina_mapa_no_body(org_client, operacao):
    for url in paginas_logadas(operacao):
        classe = re.search(r'<body class="([^"]*)"', html(org_client.get(url))).group(1)
        assert ("pagina-mapa" in classe.split()) == url.endswith("/mapa"), url


def test_tema_js_guarda_a_escolha_no_localstorage_dentro_de_try_catch():
    codigo = sem_comentarios_js(TEMA_JS)
    assert "data-tema" in codigo and "meshtracker-tema" in codigo
    assert codigo.count("localStorage") == 2 and codigo.count("try {") >= 2 and codigo.count("catch") >= 2
    assert not re.search(r"\.(innerHTML|outerHTML)\b|insertAdjacentHTML|document\.write|eval\(", codigo)


def test_css_do_tema_tem_modo_sistema_claro_escuro_e_mapa_sempre_escuro_no_sistema():
    assert 'color-scheme: light dark;' in APP_CSS                                    # modo Sistema pelo CSS
    assert re.search(r':root\[data-tema="claro"\]\s*\{\s*color-scheme: light;', APP_CSS)
    assert re.search(r':root\[data-tema="escuro"\],\s*:root:not\(\[data-tema="claro"\]\):has\(\.pagina-mapa\)\s*\{\s*color-scheme: dark;', APP_CSS)
    assert re.search(r':root\[data-tema="claro"\] \.mapa \.leaflet-tile-pane\s*\{\s*filter: grayscale\(1\) contrast\(0\.92\) brightness\(1\.04\)', MAPA_CSS)
    assert "invert(1) brightness(0.78) contrast(1.15)" in MAPA_CSS                  # o escuro é o padrão do mapa


def test_valores_claro_e_escuro_dos_tokens_sao_os_do_design():
    cores = cores_do_design()
    pares = {"chao": ("chao", "escuro-chao"), "superficie": ("superficie", "escuro-superficie"),
             "superficie-2": ("superficie-2", "escuro-superficie-2"), "tinta": ("tinta", "escuro-tinta"),
             "tinta-2": ("tinta-2", "escuro-tinta-2"), "vermelho-texto": ("vermelho", "escuro-vermelho-texto"),
             "mapa-liso": (None, None)}
    for token, (claro, escuro) in pares.items():
        if claro:
            assert par_claro_escuro(token) == (cores[claro].lower(), cores[escuro].lower()), token
    assert par_claro_escuro("mapa-liso") == ("#d9d9d4", "#1a1c1c")


# ---------------------------------------------------------- cores e estados

def test_cores_de_estado_do_css_sao_as_da_tabela_do_design():
    cores = cores_do_design()
    for estado in ESTADOS:
        assert token_css(estado) == cores[f"estado-{estado}"].lower(), estado
    for estado in ESTADOS:      # texto sobre a cor, como no DESIGN (selo-*): branco, e tinta no atrasado
        achado = re.search(rf'selo-{estado}:\s*\n\s+backgroundColor: "\{{colors\.estado-{estado}\}}"\s*\n\s+textColor: "([^"]+)"', DESIGN)
        texto = achado.group(1)
        esperado = cores[texto[8:-1]] if texto.startswith("{colors.") else texto
        assert token_css(f"{estado}-tx") == esperado.lower(), estado


def test_moldura_do_css_e_a_do_design_nos_dois_temas():
    cores = cores_do_design()
    assert token_css("moldura") == cores["moldura"].lower()
    assert token_css("moldura-tinta") == cores["moldura-tinta"].lower()
    assert token_css("moldura-tinta-2") == cores["moldura-tinta-2"].lower()


def test_cores_dos_times_do_design_sao_as_de_servicos_times():
    cores = cores_do_design()
    for nome, cor in servicos.TIMES.items():
        assert cores[f"time-{nome.lower()}"].lower() == cor.lower(), nome


def test_mapa_js_nao_repete_cor_de_estado_nem_de_tema():
    codigo = sem_comentarios_js(MAPA_JS)
    achadas = {cor.lower() for cor in re.findall(r"#[0-9a-fA-F]{6}\b", codigo)}
    assert achadas == {token_css("sem-sinal")}      # só a cor padrão do time (corSegura); o resto vem do CSS


def test_contraste_de_texto_e_de_estado_passa_de_4_5_para_1():
    for indice in (0, 1):       # claro, escuro
        fundos = [par_claro_escuro(n)[indice] for n in ("chao", "superficie", "superficie-2")]
        textos = [par_claro_escuro(n)[indice] for n in ("tinta", "tinta-2")]
        assert all(contraste(t, f) >= 4.5 for t in textos for f in fundos), indice
        assert contraste(par_claro_escuro("vermelho-texto")[indice], par_claro_escuro("superficie")[indice]) >= 4.5
    for estado in ESTADOS:
        assert contraste(token_css(f"{estado}-tx"), token_css(estado)) >= 4.5, estado
    assert contraste(token_css("moldura-tinta"), token_css("moldura")) >= 4.5
    assert contraste(token_css("moldura-tinta-2"), token_css("moldura")) >= 4.5


# ---------------------------------------------------------------- regras

def test_vermelho_so_em_perdido_recusa_e_bateria_baixa():
    for seletor, corpo in regras_css(APP_CSS) + regras_css(MAPA_CSS):
        usa = re.search(r"var\(--(perdido|perdido-tx|vermelho-texto|vermelho-fundo)\)", corpo)
        if usa:
            assert re.search(r"perdido|erro|bateria-baixa", seletor), (seletor, usa.group(0))


def test_regra_do_plano_sem_sombra_desfoque_nem_canto_arredondado():
    for seletor, corpo in regras_css(APP_CSS) + regras_css(MAPA_CSS):
        for nome, valor in declaracoes(corpo):
            if nome == "box-shadow" and ":-webkit-autofill" not in seletor:
                assert valor == "none", (seletor, valor)
            if nome == "border-radius":
                assert valor.replace(" !important", "") in ("0", "50%"), (seletor, valor)
            assert not re.search(r"blur\(|drop-shadow", valor), (seletor, nome)
    assert "blur(" not in sem_comentarios_js(MAPA_JS)


def test_nenhum_texto_abaixo_de_16_px_alem_da_atribuicao_do_openstreetmap():
    menores = []
    for seletor, corpo in regras_css(APP_CSS) + regras_css(MAPA_CSS):
        for nome, valor in declaracoes(corpo):
            if nome not in ("font", "font-size"):
                continue
            tamanho = next((t.split("/")[0] for t in valor.split() if re.fullmatch(r"[\d.]+(rem|px)(/[\d.]+)?", t)), None)
            if tamanho:
                pixels = float(tamanho[:-3]) * 16 if tamanho.endswith("rem") else float(tamanho[:-2])
                if pixels < 16:
                    menores.append(seletor)
    assert menores == [".mapa .leaflet-control-attribution"]


def test_digitacao_so_no_titulo_e_desligada_com_movimento_reduzido():
    assert re.findall(r"@keyframes (\w+)", APP_CSS + MAPA_CSS) == ["digitar"]
    assert "animation" not in MAPA_CSS
    assert re.search(r"animation: digitar 450ms steps\(16, end\)", APP_CSS)
    assert "@keyframes digitar { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0); } }" in APP_CSS
    reduzido = APP_CSS.split("@media (prefers-reduced-motion: reduce)")[1]
    assert "h1 { animation: none; }" in reduzido
    animados = [s for s, corpo in regras_css(APP_CSS) if "animation:" in corpo]
    assert animados == ["h1", "h1"]                     # o título e o desligamento


def test_fontes_vem_do_proprio_app_e_nao_do_google():
    for css in (APP_CSS, MAPA_CSS):
        assert "googleapis" not in css and "gstatic" not in css and "http" not in css.replace("https://tile", "")
    assert "font-family: 'Archivo'" in APP_CSS and "font-family: 'Chivo Mono'" in APP_CSS
    assert "../vendor/fonts/archivo-latin.woff2" in APP_CSS and "../vendor/fonts/chivo-mono-latin.woff2" in APP_CSS


def test_fontes_e_arquivos_estaticos_sao_servidos_com_200(client):
    for caminho in ("vendor/fonts/archivo-latin.woff2", "vendor/fonts/chivo-mono-latin.woff2"):
        resposta = client.get(f"/static/{caminho}")
        assert resposta.status_code == 200 and resposta.get_data()[:4] == b"wOF2", caminho
    for caminho in ("css/app.css", "css/mapa.css", "js/tema.js", "js/mapa.js"):
        assert client.get(f"/static/{caminho}").status_code == 200, caminho


def test_origem_registra_as_duas_fontes_com_hash_e_licenca():
    origem = (STATIC / "vendor" / "ORIGEM.md").read_text(encoding="utf-8")
    for arquivo in ("archivo-latin.woff2", "chivo-mono-latin.woff2"):
        linha = next(parte for parte in origem.splitlines() if f"fonts/{arquivo}" in parte)
        assert "SIL OFL 1.1" in linha and re.search(r"\b[0-9a-f]{64}\b", linha)


# ------------------------------------------------------------ mensagens

def test_recusa_vira_p_mensagem_erro_com_role_alert_e_status_400(org_client):
    resposta = org_client.post("/operadores", data={"apelido": "", "nome": ""})
    assert resposta.status_code == 400
    assert re.search(r'<p class="mensagem mensagem-erro" role="alert">[^<]+</p>', html(resposta))


def test_feito_vira_p_mensagem_sucesso_com_role_status(org_client):
    resposta = org_client.post("/operadores", data={"apelido": "Zé", "nome": "José"}, follow_redirects=True)
    assert re.search(r'<p class="mensagem mensagem-sucesso" role="status">Operador cadastrado\.</p>', html(resposta))


def test_etiquetas_recusa_feito_e_aviso_vem_do_css_com_as_cores_do_selo():
    etiquetas = {"mensagem-erro": ("Recusa", "--perdido"), "mensagem-sucesso": ("Feito", "--ativo"),
                 "mensagem-aviso": ("Aviso", "--atrasado")}
    for classe, (texto, cor) in etiquetas.items():
        corpo = dict(regras_css(APP_CSS))[f".{classe}::before"]
        assert f'content: "{texto}"' in corpo and f"background: var({cor})" in corpo, classe


# ------------------------------------------------------------------ mapa

def test_mapa_mantem_os_ids_que_o_js_usa_e_a_faixa_de_dossie(org_client, operacao):
    pagina = html(org_client.get(f"/operacoes/{operacao}/mapa"))
    usados = set(re.findall(r"getElementById\('([\w-]+)'\)", MAPA_JS)) | {f"n-{e}" for e in ("perdido", "atrasado", "ativo", "sem_sinal")}
    assert {"atualizacao", "descartados", "aviso", "lista", "mapa-pagina", "n-inscritos"} <= usados
    for id_ in usados | {"mapa"}:
        assert f'id="{id_}"' in pagina, id_
    assert 'id="atualizacao" aria-live="polite"' in pagina
    assert re.search(r'<p id="aviso" class="mensagem mensagem-aviso" role="alert" hidden>', pagina)
    for rotulo in ("Perdidos", "Atrasados", "Ativos", "Sem sinal", "Descartados", "Inscritos"):
        assert f"<dt>{rotulo}</dt>" in pagina


def test_mapa_js_so_escreve_texto_por_textcontent_e_mantem_o_comportamento():
    codigo = sem_comentarios_js(MAPA_JS)
    for proibido in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
        assert proibido not in codigo, proibido
    assert "textContent" in codigo and "corSegura(" in codigo
    assert "INTERVALO_MS = 3000" in codigo and "setInterval(atualizar, INTERVALO_MS)" in codigo
    assert "L.control.scale({ imperial: false" in codigo
    assert "https://tile.openstreetmap.org/{z}/{x}/{y}.png" in MAPA_JS          # mesmo provedor, sem trocar


def test_marcador_do_perdido_leva_colchetes_de_alvo_e_rotulo_com_o_tempo():
    codigo = sem_comentarios_js(MAPA_JS)
    assert "' alvo'" in codigo and "perdido há " in codigo
    assert re.search(r"\.mk\.estado-perdido\s*\{[^}]*--alvo-braco: 12px; --alvo-traco: 3px", MAPA_CSS)
    corpo = dict(regras_css(APP_CSS))[".alvo::after"]
    assert corpo.count("linear-gradient") == 8              # quatro cantos em L, só gradiente, sem imagem


# ------------------------------------------------------- correções do Gate 2

def itens_atuais(pagina: str) -> list[str]:
    return re.findall(r'<a href="[^"]*" aria-current="page">([^<]+)</a>', pagina)


def test_menu_marca_o_item_atual_pelo_caminho_inclusive_na_pagina_de_recusa(app, org_client, operacao):
    with app.app_context():
        inscricao = servicos.listar_inscritos(db.get_repo(), operacao)[0]["id"]
    for url in ("/operadores", "/operacoes", f"/operacoes/{operacao}", f"/operacoes/{operacao}/mapa"):
        esperado = ["Operadores"] if url == "/operadores" else ["Operações"]
        assert itens_atuais(html(org_client.get(url))) == esperado, url
    recusas = [("/operadores", {"apelido": "", "nome": ""}, ["Operadores"]),
               ("/operacoes", {"nome": ""}, ["Operações"]),
               (f"/operacoes/{operacao}/inscricoes", {"operador_id": "0"}, ["Operações"]),
               (f"/inscricoes/{inscricao}", {"time": "Roxo", "classe": "Médico"}, ["Operações"])]
    for url, dados, esperado in recusas:
        resposta = org_client.post(url, data=dados)
        assert resposta.status_code == 400, url                   # a página volta com a recusa
        assert itens_atuais(html(resposta)) == esperado, url


def test_menu_decide_o_item_atual_pelo_caminho_e_nao_pelo_endpoint():
    base = (RAIZ / "src" / "templates" / "base.html").read_text(encoding="utf-8")
    assert "request.endpoint" not in base
    assert "caminho.startswith('/operadores')" in base
    assert "caminho.startswith('/operacoes') or caminho.startswith('/inscricoes')" in base


def test_rotulo_do_perdido_tem_duas_partes_e_nunca_sai_do_quadro():
    codigo = sem_comentarios_js(MAPA_JS)
    for parte in ("'mk-nome'", "'mk-sep'", "'mk-tempo'", "manterRotuloNoQuadro", "getBoundingClientRect"):
        assert parte in codigo, parte
    assert "ajustarRotulos();" in codigo and "mapa.on('move zoom resize'" in codigo
    celular = MAPA_CSS.split("@media (max-width: 719px)")[1]
    assert ".mk-tempo { display: block; }" in celular            # duas linhas: apelido e "perdido há X"
    assert ".mk-sep { display: none; }" in celular
    assert ".mk-apelido { width: max-content; max-width: 15rem; white-space: normal; }" in celular


def test_rotulo_que_cobriria_o_anel_vai_para_baixo_do_marcador_dentro_do_quadro():
    codigo = sem_comentarios_js(MAPA_JS)
    for parte in ("deslocamentoDoRotulo", "limitesDoQuadro", "anel.bottom + 14", "anel.top - 14"):
        assert parte in codigo, parte


def test_moldura_nao_quebra_o_login_e_vira_duas_linhas_abaixo_de_1024_px():
    base = next(corpo for seletor, corpo in regras_css(APP_CSS) if seletor == ".sessao-quem")     # a regra de fora das @media
    assert "white-space: nowrap" in base
    assert "@media (max-width: 1023px)" in APP_CSS and "@media (min-width: 1024px) and (max-width: 1279px)" in APP_CSS
    abaixo = APP_CSS.split("@media (max-width: 1023px)")[1].split("@media (max-width: 719px)")[0]
    assert ".moldura { flex-wrap: wrap;" in abaixo and ".moldura-menu { order: 3; flex: 1 0 100%;" in abaixo


def test_lista_do_mapa_deixa_o_cabecalho_e_o_apelido_quebrarem_em_vez_de_rolar():
    regras = dict(regras_css(MAPA_CSS))
    assert "white-space: normal" in regras[".lista-operadores thead th"]
    assert "overflow-wrap: anywhere" in regras[".lista-operadores tbody th"]
