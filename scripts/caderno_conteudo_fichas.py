"""Texto do Caderno da Aula 7, versão 2: da Ficha 6 até as referências.

Fontes: as tabelas E/I/D/F, o fluxo, as regras R1 a R6 e as dúvidas de
docs/backlog.md; a Ficha 8 de docs/proposta.md; o status do ADR-001 de
docs/adr/ADR-001-perfil-e-inscricao.md. As Fichas 7 e 9 são iguais às da
versão 1 (commit c7ab9e9), exceto o status do ADR-001.
"""

from __future__ import annotations

REPOSITORIO = "https://github.com/izrafilcst/Desenvolvimento-Sistemas"

# Regras R1 a R6, copiadas da tabela de regras de docs/backlog.md.
REGRAS_INCREMENTO_1 = (
    "R1: Inscrever um operador já cadastrado em uma nova operação não exige "
    "novo cadastro.\n"
    "R2: Um operador tem no máximo uma inscrição por operação.\n"
    "R3: Um dispositivo pertence a no máximo uma inscrição por operação.\n"
    "R4: Mudar time ou classe altera só a inscrição, nunca o perfil.\n"
    "R5: A inscrição exige consentimento de rastreamento.\n"
    "R6: A operação só avança planejada → em curso → encerrada. Só pode haver "
    "uma operação em curso por vez, e não há inscrição em operação encerrada."
)


def _ficha_6():
    return [
        ("subtitulo", "4.6 Ficha 6 · Escopo mínimo"),
        ("legenda",
         "E é essencial, I é importante (com o incremento em que entra), D é "
         "desejável e F fica fora."),
        ("tabela", ["Funcionalidade", "Classe", "Justificativa"], [
            ["Cadastro permanente do operador", "E",
             "Sem ele o recadastro continua; é a base de tudo."],
            ["Operação com situação e inscrição por operação (time, classe, "
             "dispositivo e consentimento)", "E",
             "É a ação real do organizador e fecha o fluxo do Incremento 1."],
            ["Simulador e recebimento de sinais só de inscritos, sem "
             "duplicata", "I (Inc 2)",
             "É a regra central do rastreamento, mas depende da inscrição "
             "pronta."],
            ["Estado do operador e mapa ao vivo com lista lateral",
             "I (Inc 2)",
             "É o que o organizador vê; vem logo depois do recebimento."],
            ["Papel de observador, só leitura", "I (Inc 2)",
             "Protege a operação de escritas indevidas."],
            ["API `/api/v1` documentada, com token do gateway", "I (Inc 3)",
             "Deixa o simulador trocável pelo gateway real sem mudar a "
             "regra."],
            ["Trilha dos últimos 10 pontos e exportação CSV", "D",
             "Só se sobrar tempo no Incremento 3."],
            ["MQTT, gateway real, ordens, objetivos, topologia da malha e "
             "integração com o operational-command", "F",
             "Fora do MVP: exigem hardware, infraestrutura ou outro sistema "
             "(ADR-002 e ADR-003)."],
        ]),
        ("subtitulo", "Fluxo completo da Iteração 1 (Incremento 1)"),
        ("legenda",
         "Usuário → interface → regra de negócio → persistência → resposta."),
        ("tabela", ["Etapa", "Como fica"], [
            ["Ação do usuário",
             "O organizador inscreve um operador já cadastrado numa operação, "
             "escolhendo time, classe e dispositivo e marcando o "
             "consentimento."],
            ["Tela ou rota",
             "`/operacoes/<id>`, com formulário de inscrição que envia para "
             "`POST /operacoes/<id>/inscricoes`."],
            ["Regra principal", REGRAS_INCREMENTO_1],
            ["Dado gravado ou consultado",
             "`operador`, `operacao` e `inscricao`, no SQLite."],
            ["Resposta apresentada",
             "O inscrito aparece na lista da operação com time e classe; se "
             "uma regra for violada, a mensagem aparece na mesma página."],
            ["Critério de demonstração",
             "Cadastrar 5 operadores, inscrevê-los na operação 1 e depois na "
             "operação 2, sem novo cadastro e com times diferentes; mostrar a "
             "recusa da inscrição duplicada, do dispositivo repetido e da "
             "inscrição sem consentimento; reiniciar o app e mostrar que os "
             "dados continuam lá."],
        ]),
    ]


def _ficha_7(data):
    return [
        ("subtitulo", "4.7 Ficha 7 · Leitura orientada e decisão"),
        ("legenda",
         "A leitura do CEUBOOK não foi realizada. Os campos que dependem dela "
         "estão registrados como tal."),
        ("tabela", [], [
            ["Autor", "CEUBOOK"],
            ["Obra", "Engenharia da Computação — Desenvolvimento de Sistemas"],
            ["Edição e ano", "Brasília: CEUB, 2024"],
            ["Capítulo ou seção", "Leitura não realizada."],
            ["Conceito identificado",
             "Leitura não realizada. A aula indica essa obra para decisões de "
             "modelo de dados."],
            ["Conceito com minhas palavras", "Leitura não realizada."],
            ["Decisão relacionada",
             "Separar o perfil permanente do operador da inscrição por "
             "operação (ADR-001)."],
            ["Alternativa considerada",
             "Cadastrar o operador dentro de cada operação, com time e classe "
             "no próprio registro."],
            ["Dúvida a investigar",
             "Qual identificador estável usar para o operador (por exemplo, um "
             "número de registro da federação, se existir) e se a persistência "
             "será relacional ou de documentos (a segunda parte foi resolvida "
             "em 01/11/2026 no ADR-002: banco relacional, SQLite)."],
            ["Frase de ligação",
             "Com base no CEUBOOK (2024), decidi separar o perfil permanente "
             "do operador da inscrição por operação porque o operador se "
             "cadastra uma única vez e tudo o que muda a cada operação fica "
             "registrado na inscrição. A alternativa de cadastrar o operador "
             "dentro de cada operação foi inicialmente descartada porque "
             "obrigaria o recadastro e duplicaria dados. Como não li o "
             "capítulo, essa fundamentação será completada depois da "
             "leitura."],
        ]),
        ("subtitulo",
         "ADR-001 · Perfil permanente do operador separado da inscrição por "
         "operação"),
        ("tabela", [], [
            ["Status", f"Aceito em {data} (proposto em 01/10/2026)."],
            ["Contexto",
             "Os operadores costumam participar de várias operações. Se o "
             "sistema guardasse tudo dentro de cada operação, a mesma pessoa "
             "se cadastraria de novo a cada vez. Time, classe e o dispositivo "
             "usado podem mudar de uma operação para outra, e a posição de "
             "alguém em campo é dado pessoal, então o consentimento e o "
             "rastreamento valem só para a operação em que a pessoa está "
             "inscrita."],
            ["Decisão",
             "O operador é um perfil permanente, cadastrado uma única vez. A "
             "inscrição liga o operador a uma operação e guarda o que vale só "
             "ali: time, classe, dispositivo e consentimento. As posições "
             "pertencem à inscrição e só são gravadas com a operação em "
             "curso. A escolha entre banco relacional e de documentos, que "
             "este ADR deixou em aberto, foi feita no ADR-002: banco "
             "relacional SQLite, com as regras R2 e R3 (no máximo uma "
             "inscrição por operador e por dispositivo em cada operação) "
             "garantidas por restrições de unicidade no próprio banco. Aqui "
             "trato só do modelo lógico."],
            ["Alternativas que descartei",
             "Cadastrar o operador dentro de cada operação, porque força o "
             "recadastro, duplica dados e impede ver o histórico. Guardar "
             "time, classe e dispositivo no perfil, porque esses dados podem "
             "mudar de uma operação para outra."],
            ["O que ganho e o que pago",
             "Ganho o fim do recadastro, o histórico do operador entre "
             "operações e regras de unicidade fáceis de testar. Pago com mais "
             "entidades e telas, a necessidade de um identificador estável e "
             "uma política de quanto tempo guardar as posições."],
            ["Referências",
             "CEUBOOK (2024), capítulo ainda não lido. PRIMO; MURARI; OLIVEIRA "
             "(2022), também indicada pela aula e ainda não consultada. O "
             "texto completo está em docs/adr/ADR-001-perfil-e-inscricao.md "
             "no repositório."],
        ]),
    ]


def _ficha_8(data):
    return [
        ("subtitulo", "4.8 Ficha 8 · Proposta de projeto em uma página"),
        ("tabela", [], [
            ["Revisão",
             f"Revisada em {data} após o recorte do escopo (ADR-002 e "
             "ADR-003)."],
            ["Nome provisório", "MeshTracker Central"],
            ["Aluno ou integrantes",
             "Rafael Alves de Sousa Costa (RA 22304563)"],
            ["Usuário principal",
             "Organizador de operações da Federação de Airsoft do Distrito "
             "Federal e entorno: a pessoa que monta a operação, inscreve os "
             "jogadores e acompanha o que acontece em campo. A federação é o "
             "público do operational-command, sistema que eu desenvolvo."],
            ["Problema observado",
             "Percebi, ao desenhar o operational-command, que o operador "
             "teria de se cadastrar de novo a cada operação, mesmo sendo a "
             "mesma pessoa. Além disso, pelo desenho do firmware do "
             "MeshTracker, cada dispositivo só enxerga os vizinhos que alcança "
             "e esquece quem some por 2 minutos, então ninguém tem uma visão "
             "geral de onde cada operador está. Ainda não confirmei isso com a "
             "federação: é o que enxergo olhando para o meu próprio projeto."],
            ["Como o problema é enfrentado atualmente",
             "Não confirmei com a federação. Imagino que o cadastro seja "
             "refeito a cada operação e que o acompanhamento em campo seja "
             "feito por rádio de voz."],
            ["Consequência do problema",
             "O organizador perde tempo recadastrando gente que já conhece, "
             "pode demorar a perceber que um operador ficou sem contato e as "
             "decisões são tomadas sem dados."],
            ["Proposta de solução",
             "Uma aplicação web em que o organizador mantém o perfil "
             "permanente de cada operador, inscreve o operador em cada "
             "operação com time e classe e o acompanha num mapa ao vivo com o "
             "estado de cada um (ativo, atrasado ou perdido). Nesta demo os "
             "sinais vêm de um simulador por HTTP, no mesmo contrato que um "
             "gateway real do MeshTracker poderia usar depois."],
            ["Escopo mínimo",
             "Resumo da tabela E/I/D/F do backlog, por incremento. Incremento "
             "1 (até 10/11), itens essenciais: cadastro permanente do operador "
             "e operação com situação e inscrição por operação (time, classe, "
             "dispositivo e consentimento). Incremento 2 (até 24/11), itens "
             "importantes: simulador e recebimento de sinais só de inscritos e "
             "sem duplicata, estado do operador e mapa ao vivo com lista "
             "lateral, e papel de observador só de leitura. Incremento 3 (até "
             "08/12), item importante: API `/api/v1` documentada, com token "
             "do gateway."],
            ["Fluxo da Iteração 1",
             "O organizador inscreve um operador já cadastrado numa operação, "
             "escolhendo time, classe e dispositivo e marcando o "
             "consentimento; o inscrito aparece na lista da operação e, se "
             "uma regra (R1 a R6) for violada, a mensagem aparece na mesma "
             "página."],
            ["Funcionalidades fora do escopo inicial",
             "Fora do MVP (linha F do backlog): MQTT, gateway real, ordens, "
             "objetivos, topologia da malha e integração com o "
             "operational-command, porque exigem hardware, infraestrutura ou "
             "outro sistema (ADR-002 e ADR-003). Desejável (linha D): trilha "
             "dos últimos 10 pontos e exportação CSV, só se sobrar tempo no "
             "Incremento 3."],
            ["Tecnologias inicialmente consideradas",
             "Python 3.12, Flask, SQLite, Jinja, Leaflet (servido pelo próprio "
             "app) e pytest (ADR-002). A stack MEVN com MQTT, da versão 1 "
             "desta proposta, foi descartada no recorte."],
            ["Risco principal",
             "Validar sozinho: sem conversar com a federação, posso estar "
             "resolvendo um problema que o organizador não sente. Mitigação: "
             "roteiros cronometrados no papel de organizador, com a limitação "
             "declarada, e a conversa com a federação mantida como a pendência "
             "principal."],
            ["Como a solução será validada",
             "Testes automatizados das regras R1 a R11, mais os roteiros "
             "cronometrados de H1 (até 3 min) e H2 (até 10 s), executados pelo "
             "autor no papel de organizador e gravados. A conversa com a "
             "federação ainda não aconteceu."],
            ["Referência bibliográfica inicial",
             "CEUBOOK. Engenharia da Computação — Desenvolvimento de Sistemas. "
             "Brasília: CEUB, 2024 (capítulo ainda não lido). SOMMERVILLE, "
             "Ian. *Engenharia de software*. Tradução: Luiz Cláudio Queiroz. "
             "Revisão técnica: Fábio Levy Siqueira. 10. ed. São Paulo: Pearson "
             "Education do Brasil, 2018."],
            ["Link do repositório", REPOSITORIO],
        ]),
    ]


def _ficha_9():
    return [
        ("subtitulo", "4.9 Ficha 9 · Laboratório do repositório"),
        ("legenda", "Comandos do roteiro da aula, com o nome do meu projeto."),
        ("subtitulo", "Parte 1 · Criar a pasta e os arquivos"),
        ("codigo",
         "cd C:\\projetos\n"
         "mkdir meshtracker-central\n"
         "cd meshtracker-central\n"
         "echo # meshtracker-central > README.md\n"
         "mkdir docs docs\\adr src tests\n"
         "dir"),
        ("tabela", [], [
            ["☒ O comando dir listou o README.md.",
             "☒ As pastas docs, src e tests aparecem na listagem."],
        ]),
        ("subtitulo", "Parte 2 · Versionar e publicar"),
        ("codigo",
         "git init\n"
         "git add .\n"
         "git status\n"
         "git commit -m \"docs: Proposta inicial\"\n"
         "git log --oneline\n"
         "git branch -M main\n"
         f"git remote add origin {REPOSITORIO}\n"
         "git push -u origin main"),
        ("tabela", [], [
            ["☒ git status listou os arquivos como novos.",
             "☒ git commit respondeu com a quantidade de arquivos alterados."],
            ["☒ git log --oneline mostrou um commit.",
             "☒ git push terminou sem mensagem de erro (depois de resolver o "
             "erro da Parte 3)."],
        ]),
        ("subtitulo", "Registros do laboratório"),
        ("tabela", [], [
            ["URL do repositório", REPOSITORIO],
            ["Código do primeiro commit (git log)",
             "604b85b (docs: Proposta inicial)"],
            ["Nome da branch", "main"],
            ["Colega que validou o link", "Não realizado."],
        ]),
        ("subtitulo", "Parte 3 · Erros encontrados e soluções aplicadas"),
        ("tabela", ["Mensagem do Git", "Causa", "Solução"], [
            ["! [rejected] main -> main (fetch first)",
             "O repositório criado no GitHub já tinha um commit inicial, só "
             "com o README, que eu não tinha na minha máquina.",
             "git fetch origin, depois git merge origin/main "
             "\u2011\u2011allow\u2011unrelated\u2011histories, resolver o "
             "conflito do README "
             "mantendo o do projeto e repetir o git push."],
            ["Arquivo ~$derno_...docx no commit",
             "O Word criou um arquivo temporário enquanto o caderno estava "
             "aberto e o git add . o incluiu.",
             "Tirar do índice com git rm --cached e ignorar os arquivos ~$* "
             "no .gitignore."],
            ["nothing to commit",
             "Pasta vazia ou nenhum arquivo adicionado.",
             "Criar o README.md, rodar git add . e conferir com git status."],
            ["'inicial' não é reconhecido",
             "Mensagem do commit quebrada em duas linhas.",
             "Repetir o commit com a mensagem em uma única linha."],
        ]),
    ]


def _ficha_10(data):
    return [
        ("subtitulo", "4.10 Ficha 10 · Checklist de entrega"),
        ("tabela", ["", "Item", "Situação"], [
            ["☒", "Problema e usuário identificados.",
             "Sim, sem confirmação da federação."],
            ["☒", "Matriz de decisão preenchida.", "Sim."],
            ["☒", "Escolha justificada por extenso.", "Sim."],
            ["☐", "Pitch revisado após o feedback.",
             "Parcial: v2 por revisão própria, semáforo não realizado."],
            ["☒", "Escopo mínimo classificado em E, I, D e F.",
             f"Sim, revisado em {data}."],
            ["☒", "Fluxo ponta a ponta definido.", "Sim."],
            ["☐", "Ficha de leitura concluída.",
             "Não: leitura do CEUBOOK ainda não registrada."],
            ["☒", "ADR-001 criado.", "Sim, aceito; mais ADR-002 e ADR-003."],
            ["☒", "README preenchido.", "Sim."],
            ["☒", "Primeiro commit publicado.", "Sim, 604b85b."],
            ["☐", "Link do repositório testado por um colega.",
             "Não realizado."],
            ["☒", "Proposta de uma página finalizada.", "Sim, revisada."],
        ]),
    ]


def _revisao_do_escopo(data):
    return [
        ("titulo", "5. REVISÃO DO ESCOPO"),
        ("paragrafo",
         "Ao montar os incrementos do Ciclo 2 na Aula 10 (Ficha 12), percebi "
         "que a primeira iteração da versão 1 não cabia no prazo: eram 9 dias "
         "até o Incremento 1, em 10/11, para um projeto que faço sozinho, e a "
         "stack prevista tinha quatro serviços e um build de front-end. Em "
         f"{data}, recortei o escopo em três incrementos (até 10/11, 24/11 e "
         "08/12), troquei a stack (ADR-002) e o contrato do gateway (ADR-003) "
         "e revisei o backlog, a proposta e o pitch. O problema, o usuário e "
         "a escolha da ideia não mudaram. A tabela abaixo resume o que mudou "
         "e onde cada mudança está registrada."),
        ("legenda", "Antes (v1) × Depois (v2) × Onde está registrado."),
        ("tabela",
         ["Aspecto", "Antes (v1)", "Depois (v2)", "Onde está registrado"], [
             ["Contrato do gateway", "MQTT com Mosquitto",
              "HTTP JSON em `POST /api/v1/sinais`", "ADR-003"],
             ["Stack", "Vue, Express, MongoDB, WebSocket e Docker",
              "Flask, SQLite, páginas no servidor e Leaflet local", "ADR-002"],
             ["Iteração 1", "Inscrição, recebimento de sinais e mapa",
              "Cadastro, operação e inscrição; o mapa vai para o Incremento 2",
              "Ficha 6"],
             ["Deduplicação", "Entre dois gateways",
              "Mesmo pacote do mesmo dispositivo (R8)", "backlog"],
             ["Ordens, objetivos e trilha", "Iteração 2",
              "Fora do MVP; trilha como desejável no Incremento 3", "Ficha 6"],
             ["Validação", "Conversa com a federação",
              "Roteiros cronometrados pelo autor, limitação declarada; a "
              "federação continua pendente", "Fichas 11 e 12 (Kit)"],
         ]),
    ]


def _conclusao(data):
    return [
        ("titulo", "6. CONCLUSÃO"),
        ("paragrafo",
         "Depois de passar o projeto pelo método, o MeshTracker Central ficou "
         "como a melhor das três ideias: fez 15 pontos de 16 na matriz, contra "
         "12 do diário de obra e 11 do dimensionador solar. Escolhi porque "
         "ele conversa com um usuário real, o organizador de operações da "
         "federação, e resolve duas dores concretas: o recadastro dos "
         "operadores a cada operação e a falta de uma visão geral em campo. "
         f"Na revisão de {data}, a escolha se manteve: o recorte mudou o "
         "tamanho da entrega, não o problema nem o usuário."),
        ("paragrafo",
         "O recorte veio do prazo. A primeira iteração da versão 1 prometia, "
         "com a stack MEVN, o contrato MQTT com um simulador, o recebimento "
         "dos sinais e o mapa ao vivo, e isso não cabia em 9 dias para quem "
         "faz o projeto sozinho. Agora o Incremento 1 (até 10/11) fica só com "
         "o cadastro permanente do operador, a operação e a inscrição por "
         "operação, com as regras R1 a R6 da Ficha 6; o simulador, o mapa ao "
         "vivo e o papel de observador ficam para o Incremento 2 (até 24/11), "
         "e a API documentada, com token, para o Incremento 3 (até 08/12). "
         "Troquei a stack por Flask e SQLite (ADR-002) e o MQTT por HTTP "
         "(ADR-003). A decisão do ADR-001, de separar o perfil permanente do "
         "operador da inscrição em cada operação, foi aceita e continua sendo "
         "a base do modelo."),
        ("paragrafo",
         "O ponto mais fraco continua sendo a validação. A Feira, a "
         "entrevista e o semáforo não foram realizados, e a federação ainda "
         "não foi ouvida. Quem vai validar as hipóteses sou eu, "
         "no papel de organizador, com roteiros cronometrados: inscrever 5 "
         "operadores já cadastrados numa segunda operação em até 3 minutos "
         "(H1) e apontar no mapa quem está perdido e há quanto tempo em até "
         "10 segundos (H2). Essa limitação está declarada em "
         "docs/hipoteses-e-incrementos.md (Fichas 11 e 12). A leitura do "
         "CEUBOOK para fundamentar o ADR-001 continua pendente. Os "
         "riscos que vejo são resolver um problema que o organizador não "
         "sente e o cuidado com a posição das pessoas, que é dado pessoal e "
         "exige consentimento."),
        ("subtitulo", "Dúvidas que ficaram"),
        ("lista", [
            "Como ter os tiles do mapa offline em campo, sem internet. O "
            "Leaflet fica dentro do projeto e os marcadores aparecem mesmo sem "
            "os tiles, mas o fundo do mapa depende de internet.",
            "Por quanto tempo guardar as posições. Posição de pessoa é dado "
            "pessoal (LGPD): além do consentimento na inscrição, preciso "
            "definir por quanto tempo guardar o que for gravado depois da "
            "operação.",
            "Se a federação tem um identificador próprio para cada operador e "
            "se times e classes são uma lista fixa dela ou livres a cada "
            "operação.",
            "Quando e como conversar com a federação para validar a H1 e a H2, "
            "que por enquanto só eu posso validar, no papel de organizador.",
        ]),
    ]


REFERENCIAS = [
    ("titulo", "7. REFERÊNCIAS BIBLIOGRÁFICAS"),
    ("paragrafo",
     "AMARAL, Uender. Aula 10 · Jornada do Conhecimento · Ciclo 2. "
     "Desenvolvimento de Sistemas, CEUB, 2026/2."),
    ("paragrafo",
     "AMARAL, Uender. Aula 7 · Da ideia ao projeto: descoberta, escolha, "
     "recorte e documentação do projeto do Ciclo 2. Desenvolvimento de "
     "Sistemas, Engenharia de Computação, Turma UN, CEUB, 2026/2."),
    ("paragrafo",
     "AMARAL, Uender. Caderno de Dinâmicas e Modelos de Entrega: Aula 7 · Da "
     "ideia ao projeto, v1.1. CEUB, 2026/2."),
    ("paragrafo",
     "CEUBOOK. Engenharia da Computação — Desenvolvimento de Sistemas. "
     "Brasília: CEUB, 2024."),
    ("paragrafo",
     "KUNCE, Darius; GOBY, Dominik. *Usar registros de decisão de arquitetura "
     "para agilizar a tomada de decisões técnicas para um projeto de "
     "desenvolvimento de software*. [S. l.]: Amazon Web Services, mar. 2022. "
     "(AWS Prescriptive Guidance). Disponível em: "
     "https://docs.aws.amazon.com/pt_br/prescriptive-guidance/latest/"
     "architectural-decision-records/. Acesso em: 1 nov. 2026."),
    ("paragrafo",
     "MeshTracker: dispositivo embarcado de rastreamento GPS com rede mesh "
     "LoRa 433 MHz. README do firmware. Projeto do autor."),
    ("paragrafo",
     "operational-command: aplicação MEVN para gestão de operações. README do "
     "projeto. Projeto do autor."),
    ("paragrafo",
     "PRIMO, A. L. G.; MURARI, M. L.; OLIVEIRA, L. R. A. de. Desenvolvimento "
     "de um sistema de informação web para quantificação da arborização "
     "urbana. Revista AIDIS de Ingeniería y Ciencias Ambientales, v. 15, n. "
     "1, p. 465, 2022."),
    ("paragrafo",
     "SOMMERVILLE, Ian. *Engenharia de software*. Tradução: Luiz Cláudio "
     "Queiroz. Revisão técnica: Fábio Levy Siqueira. 10. ed. São Paulo: "
     "Pearson Education do Brasil, 2018."),
]


def secoes_fichas(data: str) -> list[tuple]:
    """Blocos da Ficha 6 em diante, com a data da revisão aplicada."""
    return (_ficha_6() + _ficha_7(data) + _ficha_8(data) + _ficha_9()
            + _ficha_10(data) + _revisao_do_escopo(data) + _conclusao(data)
            + REFERENCIAS)
