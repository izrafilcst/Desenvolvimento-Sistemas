"""Texto do Caderno da Aula 7, versão 2: da capa até a Ficha 5.

O texto da versão 1 (commit c7ab9e9) foi copiado literalmente. As mudanças
da versão 2 vêm dos documentos do repositório: o Procedimento e a Nota de
revisão de docs/dinamicas.md e o Pitch v2 do mesmo arquivo. Da Ficha 6 em
diante, o texto fica em caderno_conteudo_fichas.py.

Cada bloco de SECOES é um destes:
    ("titulo", texto)            ("subtitulo", texto)
    ("paragrafo", texto)         ("legenda", texto em itálico)
    ("tabela", cabecalho, linhas)  (cabecalho vazio: tabela sem cabeçalho)
    ("nota", texto em caixa)     ("lista", itens)
    ("codigo", texto)            ("quebra",)
"""

from __future__ import annotations

from caderno_conteudo_fichas import secoes_fichas

DATA_REVISAO = "01/11/2026"
AUTOR = "Rafael Alves de Sousa Costa"
TITULO = "Caderno da Aula 7 · MeshTracker Central · versão 2"

CAPA = {
    "disciplina": [
        "DISCIPLINA: DESENVOLVIMENTO DE SISTEMAS",
        "PROFESSOR: UENDER AMARAL",
        "TURMA UN · SEMESTRE 2026/2",
    ],
    "titulo": "DA IDEIA AO PROJETO",
    "projeto": "MESHTRACKER CENTRAL",
    "subtitulo": "Caderno de Dinâmicas e Modelos de Entrega · Aula 7",
    "versao": f"Versão 2 · revisado em {DATA_REVISAO}",
    "aluno": ["ALUNO: RAFAEL ALVES DE SOUSA COSTA", "RA: 22304563"],
    "local_data": "BRASÍLIA/ NOVEMBRO, 2026",
}

NAO_FEIRA = "Feira não realizada."
ROTULOS_CARTAO = (
    "Título provisório",
    "Usuário identificável",
    "Problema observado",
    "Consequência",
    "Como é resolvido hoje",
    "Solução imaginada",
    "Evidência ou pessoa a consultar",
    "Perguntas recebidas dos colegas",
)


def _cartao(*valores):
    """Cartão da Ficha 2: oito campos, na ordem de ROTULOS_CARTAO."""
    return ("tabela", [], [[r, v] for r, v in zip(ROTULOS_CARTAO, valores)])


INTRODUCAO = [
    ("titulo", "1. INTRODUÇÃO"),
    ("paragrafo",
     "Este caderno reúne o que fiz na Aula 7 de Desenvolvimento de Sistemas, "
     "“Da ideia ao projeto”. A proposta da aula é sair da vontade de usar uma "
     "tecnologia e chegar a um problema real, de uma pessoa real, com escopo "
     "pequeno e uma decisão que eu consiga defender. Para isso usamos o "
     "método 3I + 3D: investigar, interpretar, idealizar, decidir, delimitar "
     "e documentar."),
    ("paragrafo",
     "Meu projeto é o MeshTracker Central, um painel web para quem organiza "
     "operações de airsoft na Federação do Distrito Federal e entorno. Hoje "
     "eu desenvolvo duas coisas que se complementam: o operational-command, "
     "um sistema web para gerir operações, e o MeshTracker, um dispositivo "
     "com GPS e rádio LoRa que cria uma rede entre os jogadores sem depender "
     "de internet. A ideia é ligar os dois: o organizador cadastra o operador "
     "uma única vez, inscreve o operador em cada operação com time e classe e "
     "acompanha todos no mapa."),
    ("paragrafo",
     "Nem tudo da aula pôde ser feito. A Feira das três ideias, a Entrevista "
     "cruzada e o semáforo do pitch dependem dos colegas em sala e não foram "
     "realizados, e a leitura do CEUBOOK para fundamentar o ADR-001 também "
     "não foi feita. Onde isso acontece, deixei escrito no próprio campo o "
     "que não foi realizado, em vez de inventar respostas."),
    ("paragrafo",
     f"Esta é a versão 2 do caderno, revisada em {DATA_REVISAO}. Ao planejar "
     "os incrementos do Ciclo 2 (Aula 10), percebi que a primeira iteração "
     "que eu tinha prometido não cabia no prazo. Recortei o escopo, troquei a "
     "stack e registrei as decisões nos ADR-002 e ADR-003. O problema, o "
     "usuário e a escolha da ideia continuam os mesmos; o que mudou está na "
     "seção 5."),
    ("titulo", "2. OBJETIVOS"),
    ("paragrafo",
     "O objetivo da aula é terminar com seis entregas que qualquer pessoa "
     "consiga verificar: a proposta de uma página, a matriz de decisão com a "
     "escolha justificada, o escopo recortado em Essencial, Importante, "
     "Desejável e Fora, o pitch revisado, a fundamentação com a ficha de "
     "leitura e o ADR-001, e o repositório com README, estrutura de pastas e "
     "primeiro commit."),
    ("paragrafo",
     "O objetivo do meu projeto, na primeira iteração, que passou a ser o "
     "Incremento 1 (até 10/11), é fechar um fluxo pequeno de ponta a ponta: "
     "o organizador inscreve um operador já cadastrado numa operação, "
     "escolhendo time, classe e dispositivo e marcando o consentimento, e o "
     "inscrito aparece na lista da operação com time e classe. Se uma regra "
     "for violada, a mensagem aparece na mesma página. O mapa ao vivo, com "
     "operadores simulados, fica para o Incremento 2 (até 24/11)."),
]

PROCEDIMENTO = [
    ("titulo", "3. PROCEDIMENTO (MÉTODO 3I + 3D)"),
    ("paragrafo",
     "Segui a ordem do Caderno de Dinâmicas. O quadro abaixo mostra como "
     "apliquei os seis movimentos do método ao meu projeto."),
    ("tabela", ["Movimento", "Como apliquei"], [
        ["1. Investigar",
         "Meu contexto é o das operações de airsoft da Federação do DF e "
         "entorno, para quem desenvolvo o operational-command. Ao desenhar o "
         "sistema percebi que o operador teria de se cadastrar de novo a cada "
         "operação e que time e classe precisam ser tratados por operação. No "
         "firmware do MeshTracker, pelo que está desenhado, cada dispositivo "
         "só mostra os vizinhos que alcança e esquece quem some por 2 "
         "minutos, então ninguém tem a visão do conjunto. Não conversei com a "
         "federação sobre isso: é o que enxergo olhando para o meu próprio "
         "projeto."],
        ["2. Interpretar",
         "Organizadores de operações de airsoft da Federação do DF e entorno "
         "precisam inscrever operadores já conhecidos em cada nova operação e "
         "saber onde cada um está em campo porque, sem perfil permanente e sem "
         "visão geral, acabam recadastrando os operadores e acompanhando a "
         "operação às cegas."],
        ["3. Idealizar",
         "Uma aplicação web em que o organizador inscreve, em cada operação, "
         "operadores que já estão cadastrados (com time e classe) e os "
         "acompanha ao vivo no mapa, para não recadastrar ninguém e ter uma "
         "visão geral mesmo sem internet. Vou saber que funciona com testes "
         "automatizados das regras e com uma demonstração de 5 operadores "
         "simulados em 2 operações."],
        ["4. Decidir",
         "Comparei três ideias na matriz da Ficha 4. O MeshTracker Central fez "
         "15 pontos, o diário de obra digital 12 e o dimensionador solar 11."],
        ["5. Delimitar",
         f"O recorte de {DATA_REVISAO} divide o MVP em três incrementos: o 1 "
         "(até 10/11) fica com o cadastro permanente, a operação e a inscrição "
         "por operação; o 2 (até 24/11), com o simulador, os sinais só de "
         "inscritos, o estado do operador, o mapa ao vivo e o papel de "
         "observador; o 3 (até 08/12), com a API `/api/v1` documentada, com "
         "token, e o Guia de reprodução. Ficam de fora o MQTT, o gateway real, "
         "as ordens, os objetivos, a topologia da malha e a integração com o "
         "operational-command (ADR-002 e ADR-003)."],
        ["6. Documentar",
         "README, backlog, proposta de uma página, os ADR-001, ADR-002 e "
         "ADR-003, as histórias de usuário (Ficha 13) e as hipóteses e "
         "incrementos (Fichas 11 e 12)."],
    ]),
]

FICHAS_1_A_3 = [
    ("titulo", "4. RESULTADOS: FICHAS PREENCHIDAS"),
    ("subtitulo", "4.1 Ficha 1 · Classificação rápida"),
    ("legenda", "Classifiquei cada frase e justifiquei em poucas palavras."),
    ("tabela",
     ["Frase", "Problema", "Tema", "Solução", "Tecnologia", "Justificativa"], [
         ["Quero usar React.", "☐", "☐", "☐", "☒",
          "Nomeia uma ferramenta, não a necessidade de alguém."],
         ["Quero criar um sistema de laboratório.", "☐", "☒", "☐", "☐",
          "Indica uma área, sem dizer quem sofre nem qual é o problema."],
         ["Estudantes não sabem quais equipamentos estão disponíveis.",
          "☒", "☐", "☐", "☐",
          "Descreve uma pessoa e uma dificuldade concreta."],
         ["Uma aplicação para registrar a situação dos equipamentos.",
          "☐", "☐", "☒", "☐",
          "Propõe o que construir para resolver um problema."],
         ["Quero aplicar inteligência artificial.", "☐", "☐", "☐", "☒",
          "É um meio, não a necessidade de alguém: IA não é um problema."],
     ]),
    ("subtitulo", "4.2 Ficha 2 · Cartões das três ideias"),
    ("legenda",
     "A Feira das três ideias não foi realizada, então os cartões não têm "
     "perguntas dos colegas."),
    ("subtitulo", "Ideia 1"),
    _cartao(
        "MeshTracker Central",
        "Organizador de operações da Federação de Airsoft do Distrito Federal "
        "e entorno: quem monta a operação, inscreve os jogadores e acompanha o "
        "que acontece em campo.",
        "O operador teria de se cadastrar de novo a cada operação, e durante a "
        "operação ninguém tem uma visão geral de onde cada um está, porque "
        "cada dispositivo só enxerga os vizinhos que alcança por até 2 "
        "minutos. Isso vem do desenho do meu projeto e ainda não foi "
        "confirmado com a federação.",
        "O organizador perde tempo recadastrando gente que já conhece, pode "
        "demorar a perceber que um operador ficou sem contato e toma decisões "
        "sem dados.",
        "Não confirmei com a federação. Imagino que seja com fichas ou "
        "planilhas e rádio de voz.",
        "Um painel web ao vivo, alimentado pela rede LoRa do MeshTracker, com "
        "cadastro permanente do operador, inscrição por operação (time e "
        "classe) e, depois, ordens com confirmação.",
        "A própria federação, para quem desenvolvo o operational-command. "
        "Ainda não conversei com ninguém sobre este projeto em específico.",
        NAO_FEIRA),
    ("subtitulo", "Ideia 2"),
    _cartao(
        "Dimensionador solar fotovoltaico",
        "Estudante de engenharia ou instalador que dimensiona sistemas "
        "fotovoltaicos residenciais.",
        "Dimensionar módulos e inversor a partir do consumo e da irradiação "
        "exige cálculos manuais e planilhas fáceis de errar.",
        "Sistema sub ou superdimensionado e retrabalho.",
        "Imagino que com planilhas e calculadoras de fabricantes; não "
        "verifiquei.",
        "Uma aplicação web que calcula a potência, os módulos e o inversor a "
        "partir do consumo e da irradiação local e salva o projeto.",
        "Nenhuma pessoa definida.",
        NAO_FEIRA),
    ("subtitulo", "Ideia 3"),
    _cartao(
        "Diário de obra digital (RDO)",
        "Engenheiro residente ou mestre de obras.",
        "O registro diário em papel ou planilha é esquecido, alterado depois e "
        "difícil de auditar.",
        "Disputas e falta de rastro de auditoria.",
        "Imagino que com papel, planilhas e mensagens; não verifiquei.",
        "Uma aplicação web de registro diário que trava depois da assinatura e "
        "guarda o histórico.",
        "Nenhuma pessoa definida.",
        NAO_FEIRA),
    ("subtitulo", "4.3 Ficha 3 · Entrevista cruzada"),
    ("legenda",
     "A entrevista cruzada não foi realizada. As respostas abaixo são o que eu "
     "penso hoje sobre o meu próprio projeto, e não o resultado de uma "
     "conversa."),
    ("tabela", ["Pergunta", "O que penso hoje"], [
        ["Quem é o usuário?",
         "O organizador de operações da Federação de Airsoft do DF e "
         "entorno."],
        ["O que ele tenta fazer?",
         "Inscrever os operadores em cada operação, com time e classe, e "
         "acompanhar onde cada um está em campo."],
        ["O que dificulta essa atividade?",
         "O operador precisa ser cadastrado de novo a cada operação e não "
         "existe uma visão geral das posições."],
        ["Como ele resolve isso hoje?",
         "Não sei ao certo. Imagino fichas ou planilhas e rádio de voz."],
        ["Qual é a consequência do problema?",
         "Tempo perdido no recadastro e dificuldade para perceber que um "
         "operador ficou sem contato."],
        ["Qual seria a menor melhoria útil?",
         "Inscrever um operador já cadastrado em uma operação e vê-lo no "
         "mapa."],
        ["Como saberemos que a solução ajudou?",
         "Se o organizador conseguir inscrever o mesmo operador em uma segunda "
         "operação sem cadastrá-lo de novo e souber dizer, sem explicação, "
         "quem está sem sinal e há quanto tempo."],
    ]),
    ("subtitulo", "Síntese pós-entrevista"),
    ("tabela", [], [
        ["Uma dúvida descoberta", "Entrevista não realizada."],
        ["Uma suposição que precisa ser validada",
         "Suponho que o organizador realmente trabalhe sem internet e que o "
         "cadastro hoje seja refeito a cada operação. Não confirmei nenhuma "
         "das duas."],
        ["Enunciado revisado do problema",
         "Entrevista não realizada, então mantenho o enunciado original: "
         "organizadores de operações de airsoft da Federação do DF e entorno "
         "precisam inscrever operadores já conhecidos em cada nova operação e "
         "saber onde cada um está em campo porque, sem perfil permanente e sem "
         "visão geral, acabam recadastrando os operadores e acompanhando a "
         "operação às cegas."],
    ]),
]

FICHAS_4_E_5 = [
    ("subtitulo", "4.4 Ficha 4 · Matriz de decisão"),
    ("legenda",
     "Escala: 2 = atende claramente; 1 = atende em parte; 0 = ainda não "
     "atende. Fiz a pontuação sozinho, sem Feira nem entrevista; ela reflete "
     "só o meu julgamento. Ideia 1: MeshTracker Central. Ideia 2: "
     "dimensionador solar fotovoltaico. Ideia 3: diário de obra digital "
     "(RDO)."),
    ("tabela",
     ["Critério", "Ideia 1", "Ideia 2", "Ideia 3",
      "Observação sobre a ideia 1"], [
         ["Problema claro", "2", "1", "1",
          "Tenho usuário e consequência definidos, mas ainda sem confirmação "
          "da federação."],
         ["Usuário acessível", "2", "1", "1",
          "A federação é o público real do operational-command, embora eu "
          "ainda não tenha entrevistado ninguém."],
         ["Relevância", "2", "1", "2",
          "Sem uma central não há visão geral nem confirmação de ordens."],
         ["Viabilidade técnica", "2", "1", "2",
          "Já trabalho com a stack do operational-command, e a primeira "
          "iteração usa simulador, sem depender do firmware incompleto."],
         ["Escopo mínimo", "1", "2", "1",
          "O fluxo é um só, mas cresceu com a inscrição por operação; por "
          "isso tirei a trilha do essencial."],
         ["Testabilidade", "2", "2", "1",
          "A regra de duplicidade e os estados por tempo são fáceis de "
          "testar."],
         ["Aderência à disciplina", "2", "1", "2",
          "Tem contrato de API, modelo de dados, interface e regra de "
          "negócio."],
         ["Evolução em 3 iterações", "2", "2", "2",
          "Rastreamento, depois ordens, depois hardware real e autenticação "
          "das ordens."],
         ["**TOTAL**", "**15**", "**11**", "**12**", ""],
     ]),
    ("nota",
     f"**Nota de revisão ({DATA_REVISAO}):** As notas acima são as da Aula 7. "
     "Com o recorte, o escopo mínimo da Ideia 1 passaria a 2 e a viabilidade "
     "passa a se apoiar em Flask e SQLite em vez da stack do "
     "operational-command. A escolha não muda."),
    ("nota",
     "**Frase de decisão**\n"
     "Escolhi o projeto **MeshTracker Central** porque atende ao usuário "
     "**organizador de operações de airsoft da Federação do DF e entorno**, "
     "resolve **o recadastro dos operadores a cada operação e a falta de "
     "visão geral em campo** e permite entregar inicialmente **a inscrição "
     "por operação e o acompanhamento ao vivo de operadores simulados no "
     "mapa**."),
    ("subtitulo", "4.5 Ficha 5 · Pitch e semáforo"),
    ("tabela", [], [
        ["Pitch v1",
         "Para organizadores de operações de airsoft da Federação do DF e "
         "entorno, que recadastram os mesmos operadores a cada operação e não "
         "sabem onde cada um está em campo, propomos a Central MeshTracker, um "
         "painel web com perfil permanente do operador, inscrição por operação "
         "(time e classe) e mapa ao vivo. Na primeira iteração, entregaremos o "
         "fluxo de inscrever um operador já cadastrado e vê-lo no mapa, "
         "mudando de estado conforme o tempo sem sinal. Saberemos que funciona "
         "quando o organizador reinscrever o mesmo operador em uma segunda "
         "operação sem cadastrá-lo de novo e identificar, sem explicação, quem "
         "está sem sinal e há quanto tempo."],
        ["Feedback e pitch v2",
         "Semáforo não realizado; o pitch v2 é revisão própria após o "
         "recorte."],
        ["Pitch v2",
         "*(revisão própria após o recorte; o semáforo dos colegas não foi "
         "realizado)*\n"
         "Para organizadores de operações de airsoft da Federação do DF e "
         "entorno, que recadastram os mesmos operadores a cada operação e não "
         "sabem onde cada um está em campo, propomos o MeshTracker Central, um "
         "painel web com perfil permanente do operador, inscrição por operação "
         "e mapa ao vivo. No primeiro incremento, entregaremos o cadastro "
         "único do operador e a inscrição dele em cada operação, com time, "
         "classe e dispositivo. Saberemos que funciona quando o organizador "
         "inscrever 5 operadores já cadastrados numa segunda operação em até 3 "
         "minutos, sem redigitar dados, e, no segundo incremento, apontar no "
         "mapa quem está perdido e há quanto tempo em até 10 segundos."],
    ]),
]

SECOES = (INTRODUCAO + PROCEDIMENTO + FICHAS_1_A_3 + FICHAS_4_E_5
          + secoes_fichas(DATA_REVISAO))
