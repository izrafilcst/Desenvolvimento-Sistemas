# Roteiro do Demo Day: 10 minutos

Terça, 15/12/2026, Aula 19 (Demo Day). Rafael Alves de Sousa Costa apresenta o MeshTracker Central. Código: a tag `v1.0`, planejada para 08/12 `[conferir no ensaio: a tag existe e o app roda dela; senão, o ramo que estiver integrado]`. Escrito em 08/11/2026, antes do ensaio. O `roteiro-5min.md` (Aula 14) não muda.

Como ler este arquivo: igual ao `roteiro-5min.md`. As linhas que começam com `>` são o que eu digo em voz alta, e só elas contam para os 10 minutos. O que está em negrito é o que eu clico ou mostro. Cada fala tem logo abaixo a *Fonte*. Os números vêm dos arquivos citados e são conferidos no ensaio. Onde o resultado ainda não existe, há um marcador `[conferir no ensaio: ...]`; todos estão reunidos em "Marcadores para o ensaio". Nenhuma fala afirma validação com a federação de airsoft: ela não aconteceu e não tem data (`PRODUCT.md`, seção Users). Quem executou os roteiros fui eu, no papel de organizador (`docs/hipoteses-e-incrementos.md`, "Quem valida").

## Resumo em uma tabela

| Tempo | Bloco | Slides | Mostra | Fonte |
|---|---|---|---|---|
| 0:00–1:00 | 1. Motivo | 1, 2 | o problema, o usuário, a ligação com o operational-command e com o dispositivo MeshTracker | `README.md`, `docs/proposta.md` |
| 1:00–1:55 | 2. Hipóteses e recorte | 3, 4 | H1 a H4 com o sinal mensurável; o que ficou fora e por quê | `docs/hipoteses-e-incrementos.md`, `docs/backlog.md` |
| 1:55–4:05 | 3. Os três ADRs | 5, 6, 7 | contexto, decisão, alternativa descartada, onde aparece na demo e nos testes | `docs/adr/ADR-001`, `ADR-002`, `ADR-003`; `docs/api.md` |
| 4:05–5:15 | 4a. Demo H1 | 8 (2 passos) | inscrever os 5 na Charlie; três recusas | ADR-001, R1 a R5 em `docs/backlog.md`, `docs/evidencias/funcional.md` |
| 5:15–6:30 | 4b. Demo H2 | 9 (2 passos) | mapa da Bravo; a faixa; a Coruja perdida; MT-99 descartado | R7 a R9, ADR-003, `DESIGN.md`, `docs/evidencias/funcional.md` |
| 6:30–7:10 | 4c. Demo H3 e H4 | 10 (2 passos) | observador só lê (403); curl 401, 201 e 200 | R10 e R11, `docs/api.md`, `docs/evidencias/curl-401-201.txt` |
| 7:10–8:25 | 5. Qualidade | 11, 12, 13 | testes por regra; revisão S-1 a S-5; reprodução pelo Guia | `tests/`, `docs/evidencias/seguranca.md`, `docs/guia-de-reproducao.md` |
| 8:25–8:55 | 6. O que mudou desde a Aula 14 | 14 | antes e depois da identidade das telas | `docs/evidencias/*.png`, `docs/evidencias/v1/`, `DESIGN.md` |
| 8:55–10:00 | 7. Limites e próximos passos | 15, 16 | a federação como pendência principal; sinais simulados; LGPD; app de celular e gateway MQTT | `PRODUCT.md`, `docs/backlog.md`, `docs/api.md` |
| depois dos 10:00 | Perguntas (à parte) | 17 | pistas dos arquivos | ver "Perguntas prováveis" |

## Lista de slides (contrato do deck)

São 17 slides. As falas (linhas `>`) de cada slide vão nas notas dele; nos slides de demo, as de cada passo vão nas notas do passo. Regras do deck, vindas da crítica anterior e de `PRODUCT.md` (Accessibility & Inclusion) e `DESIGN.md`:

- O número em destaque é a **meta** (3 min, 10 s) ou a **regra testada** (R9 e seus testes). O tempo de script (554 ms, 94 ms) nunca vai em destaque: fica numa linha de apoio, no mesmo corpo do texto.
- Vermelho só para recusa (R2, R3, R5, 401, 403) e perda (o perdido). Cores de estado e de time são as do `DESIGN.md`, e o estado sempre tem o texto ao lado.
- Corpo de pelo menos 26 px no palco de 1920. Nada de texto secundário em miniatura: o que precisa ser lido vai em corpo de leitura.
- Slide de **demo em dois passos**: no passo 1, antes da troca de aba, aparecem a hipótese, a meta e o que olhar; no passo 2, na volta, aparece o resultado.
- Nenhum slide afirma validação com a federação.

1. **MeshTracker Central** (bloco 1; não é demo)
   - Conteúdo mínimo: título; "Painel do organizador de operações de airsoft do DF"; os dois problemas (o operador teria de se cadastrar de novo a cada operação; cada dispositivo esquece quem some por 2 minutos, e ninguém vê o conjunto); "Sinais simulados. Problema ainda não confirmado com a federação."; rodapé com autor, Desenvolvimento de Sistemas, CEUB e Demo Day, 15/12/2026.
2. **A central que faltava** (bloco 1; não é demo)
   - Conteúdo mínimo: três caixas ligadas: operational-command (gere as operações), MeshTracker Central (inscreve e mostra no mapa) e dispositivo MeshTracker (GPS e rádio LoRa de 433 MHz). Uma linha: "Nesta demo: sem integração com o operational-command, sem dispositivo; sinais simulados." Uma linha: "Por que agora: os dois projetos já existem; o MVP cabe em três incrementos, até 08/12."
3. **Quatro hipóteses** (bloco 2; não é demo)
   - Conteúdo mínimo: tabela H1 a H4 com o sinal mensurável. Destaque numérico: **3 min** (H1) e **10 s** (H2). H3: nenhum sinal de não inscrito vira posição; nenhuma escrita do observador passa. H4: o simulador e o curl usam só a API.
4. **O recorte** (bloco 2; não é demo)
   - Conteúdo mínimo: duas colunas. Dentro: Incremento 1 (cadastro, operação, inscrição), 2 (simulador, sinais filtrados, estado, mapa, observador) e 3 (API com token, Guia, v1.0). Fora: MQTT, gateway real, ordens, objetivos, topologia da malha, integração com o operational-command; o motivo, "exigem hardware, infraestrutura ou outro sistema". Uma linha de desejável: trilha dos últimos 10 pontos e exportação CSV, só se sobrar tempo `[conferir no ensaio: ficaram de fora ou entraram]`.
5. **ADR-001: perfil permanente, inscrição por operação** (bloco 3; não é demo)
   - Conteúdo mínimo: quatro linhas. Contexto: o operador joga várias operações; time, classe e dispositivo mudam; a posição é dado pessoal e o consentimento vale por operação. Decisão: o perfil é permanente e a inscrição guarda o que muda. Descartei: cadastrar o operador dentro de cada operação. Na demo e nos testes: inscrever os 5 sem recadastro (H1); regras R1 a R5; R2 e R3 como UNIQUE no banco.
6. **ADR-002: Flask e SQLite** (bloco 3; não é demo)
   - Conteúdo mínimo: quatro linhas. Contexto: Vue, Express, MongoDB e Docker eram quatro serviços e um build de front-end para 9 dias, trabalhando sozinho. Decisão: Flask e SQLite, três comandos, camadas rotas → serviços → repositório. Descartei: MEVN e Flask com MongoDB. Na demo e nos testes: a recusa de duplicado vem do banco (R2 e R3); a regra roda em `servicos.py` sem servidor. Preço: sem WebSocket, o mapa consulta a cada 3 s.
7. **ADR-003: HTTP no lugar de MQTT** (bloco 3; não é demo)
   - Conteúdo mínimo: quatro linhas. Contexto: sem hardware nem gateway real no MVP, mas simulador, descarte e mapa precisam de um contrato. Decisão: `POST /api/v1/sinais` com JSON; os códigos 401, 202, 200 e 201. Descartei: MQTT com Mosquitto (broker, TLS, permissões por tópico); volta com o gateway real. Na demo e nos testes: o terminal da demo (H4); regras R7, R8 e R11. Vermelho só no 401.
8. **H1: inscrever sem recadastrar** (bloco 4a; **demo em dois passos**)
   - Passo 1 (antes da troca de aba): hipótese H1; meta em destaque, **3 min** ("os 5 já cadastrados entram na Operação Charlie em até 3 min"); o que olhar: "O formulário não pede nome. E as três recusas."
   - Passo 2 (na volta): resultado "5 inscritos, nenhum cadastro refeito"; três recusas com o código da regra em destaque, **R2** operador repetido e **R3** dispositivo repetido (os dois com "UNIQUE no banco") e **R5** sem consentimento; uma linha "ADR-001: o perfil é permanente"; apoio em corpo de leitura: "Por script: 554 ms. Mede o fluxo, não uma pessoa." `[conferir no ensaio: tempo cronometrado do ensaio, que passa a ser o apoio]`; print da Charlie com os 5 inscritos (`docs/evidencias/v1/`, ou `docs/evidencias/02-inscricao-charlie.png` enquanto não houver).
9. **H2: quem está perdido, e há quanto tempo** (bloco 4b; **demo em dois passos**)
   - Passo 1: hipótese H2; meta em destaque, **10 s**; o que olhar: "A faixa de contagem acima do mapa. A Coruja (MT-03) com colchetes. O MT-99 só no contador de descartados."
   - Passo 2: resultado: a régua da R9 com os quatro estados (sem sinal: nunca recebeu; ativo: até 60 s; atrasado: 60 a 120 s; perdido: acima de 120 s) nas cores do `DESIGN.md`; limites testados em 59, 60, 61, 119, 120 e 121 s; destaque na regra testada, **R9: 39 testes** `[conferir no ensaio: contagem]`; dois pares, 202 (R7: o MT-99, não inscrito, só conta como descartado) e 200 (R8: pacote repetido não grava de novo); apoio: "Por script: mediana de 94 ms. Mede o fluxo, não uma pessoa."; print do mapa com a Coruja perdida (`docs/evidencias/v1/`, ou `07-mapa-perdido.png` enquanto não houver).
10. **H3 e H4: acesso e API** (bloco 4c; **demo em dois passos**)
    - Passo 1: hipóteses H3 e H4 com o sinal de cada uma; o que olhar: "No navegador, o observador: só lista e mapa, sem formulários. No terminal, os códigos da API."
    - Passo 2: tabela de códigos com a regra ao lado: **403** observador (R10) e **401** sem token (R11), em vermelho, porque são recusas; **201** com token, gravado; **200** o mesmo pacote, duplicado (R8). Uma linha: "O contrato que o simulador usa e que um gateway real usaria (ADR-003)." Print do observador (`docs/evidencias/v1/`, ou `08-observador.png` enquanto não houver).
11. **Testes por regra** (bloco 5; não é demo)
    - Conteúdo mínimo: número em destaque, o total de testes das regras R1 a R11 (474 em 08/11/2026) `[conferir no ensaio: total e segurança]`, com "66 de segurança" ao lado, em corpo de leitura; barras de R1 a R11 com o nome da regra (R9, "estado por tempo", é a mais alta); a nota "contagem pelo nome do teste, no mínimo".
12. **Revisão de segurança: S-1 a S-5** (bloco 5; não é demo)
    - Conteúdo mínimo: tabela com id, achado em poucas palavras e destino, todos de severidade Baixa e sem vermelho: S-1 corpo sem limite, corrigido (64 KB, 413); S-2 JSON aninhado dava 500, corrigido (400); S-3 tempo do login revelava usuário, corrigido; S-4 o simulador seguia redirecionamento levando o token, corrigido; S-5 token em `--token`, aceito (o Guia recomenda a variável de ambiente). Rodapé: bandit sem achado alto; pip-audit sem vulnerabilidade conhecida `[conferir no ensaio: rodar de novo]`.
13. **Reprodução pelo Guia** (bloco 5; não é demo)
    - Conteúdo mínimo: a cadeia "clone limpo → venv novo → só o Guia". O estado: "Feita em 08/11, num clone limpo e com as telas da Aula 14: 382 testes passaram. A refazer com as telas novas antes da v1.0 (até 05/12)." `[conferir no ensaio: data, commit, testes e passos que travaram na reprodução com as telas novas; troque a segunda frase pelo resultado]`.
14. **O que mudou desde a Aula 14** (bloco 6; não é demo)
    - Conteúdo mínimo: duas colunas de mesmo tamanho, "Aula 14 (10/11)" e "Agora". Esquerda: `docs/evidencias/07-mapa-perdido.png`. Direita: print equivalente em `docs/evidencias/v1/` `[conferir no ensaio: a pasta ainda está vazia]`. Três marcas legendadas na direita: moldura preta; faixa com a contagem por estado; perdido com colchetes e "perdido há X". Uma linha: "Os botões têm os mesmos nomes."
15. **Limites** (bloco 7; não é demo)
    - Conteúdo mínimo: em destaque, a pendência principal: "Validação com a federação: ainda não aconteceu e não tem data." Abaixo, três linhas: validado só pelo autor, no papel de organizador; sinais simulados e tempos de script; prazo de guarda das posições (LGPD) por definir. Sem vermelho.
16. **Próximos passos** (bloco 7; não é demo)
    - Conteúdo mínimo: app de celular e gateway MeshTracker por MQTT, enviando ao mesmo contrato HTTP (`docs/api.md`, "Fontes de sinal"), com a legenda "nada disso está pronto"; conversar com a federação (sem data); definir o prazo de guarda das posições; tiles offline do mapa (dúvida em aberto 1).
17. **Obrigado. Perguntas?** (depois dos 10 minutos; não é demo)
    - Conteúdo mínimo: quatro pistas: Código (tag `v1.0` `[conferir no ensaio]`), API (`docs/api.md`), Para reproduzir (`docs/guia-de-reproducao.md`), Evidências (`docs/evidencias/`).

## Texto falado

### Bloco 1: Motivo (0:00–1:00)

**Mostre o slide 1.**

> Este é o MeshTracker Central, um painel web para o organizador de operações de airsoft do Distrito Federal.

*Fonte:* `docs/proposta.md` (Usuário principal, Proposta de solução); `README.md`.

> Vi dois problemas nos meus próprios projetos. O operador teria de se cadastrar de novo a cada operação. E cada dispositivo só enxerga os vizinhos e esquece quem some por 2 minutos, então ninguém vê o conjunto.

*Fonte:* `docs/proposta.md` (Problema observado); `README.md` ("Por que este projeto existe"); `docs/adr/ADR-001-perfil-e-inscricao.md` (Contexto).

> Não confirmei isso com a federação.

*Fonte:* `docs/proposta.md` ("Ainda não confirmei com a federação"; Risco principal); `README.md`.

**Avance para o slide 2.**

> Eu desenvolvo o operational-command, que gere as operações, e o MeshTracker, um dispositivo com GPS e rádio LoRa. Faltava ligar os dois. Por que agora: os dois já existem, e o MVP do Ciclo 2 cabe em três incrementos.

*Fonte:* `README.md` ("Por que este projeto existe"; "Em que ponto está"; "Projetos relacionados"); `PRODUCT.md` (Positioning).

> Nesta demo, a ligação é só o desenho: não integro o operational-command, não uso o dispositivo, e os sinais são simulados.

*Fonte:* `README.md` ("Projetos relacionados": a demo é independente); `docs/adr/ADR-002-stack-flask-sqlite.md` (Contexto); `docs/adr/ADR-003-gateway-por-http.md` (Contexto: sem hardware nem gateway real no MVP).

### Bloco 2: Hipóteses e recorte (1:00–1:55)

**Mostre o slide 3.**

> São quatro hipóteses, cada uma com um sinal que dá para medir: duas são tempos e duas são testes. H1: inscrever cinco operadores já cadastrados numa segunda operação, sem redigitar dados, em até 3 minutos. H2: apontar quem está perdido, e há quanto tempo, em até 10 segundos depois de abrir o mapa.

*Fonte:* `docs/hipoteses-e-incrementos.md` (Ficha 11, coluna "Saberemos quando", H1 e H2).

> H3: nenhum sinal de quem não está inscrito vira posição, e nenhuma escrita do observador passa. H4: o simulador e o curl usam só a API, sem tocar no banco.

*Fonte:* `docs/hipoteses-e-incrementos.md` (Ficha 11, H3 e H4).

**Avance para o slide 4.**

> O recorte: ficou dentro o que cabe em três incrementos. Ficou fora o que exige hardware, infraestrutura ou outro sistema: MQTT, gateway real, ordens, objetivos, topologia da malha e integração com o operational-command.

*Fonte:* `README.md` ("O que entra em cada incremento"; "O que fica de fora"); `docs/backlog.md` (Funcionalidades, linhas E, I e F); `docs/hipoteses-e-incrementos.md` (Ficha 12).

### Bloco 3: Os três ADRs (1:55–4:05)

**Mostre o slide 5.**

> ADR-001, o modelo de dados. O mesmo operador joga várias operações, e time, classe e dispositivo mudam de uma para outra. A posição em campo é dado pessoal, e o consentimento vale por operação.

*Fonte:* `docs/adr/ADR-001-perfil-e-inscricao.md` (Contexto).

> Decidi que o perfil do operador é permanente e a inscrição guarda o que muda. Descartei cadastrar o operador dentro de cada operação, porque obriga o recadastro.

*Fonte:* `docs/adr/ADR-001-perfil-e-inscricao.md` (Decisão; Alternativas que descartei).

> Na demo, inscrevo os cinco sem recadastro. Nos testes, são as regras R1 a R5; a R2 e a R3 são UNIQUE no banco.

*Fonte:* R1 a R5 em `docs/backlog.md`; `docs/adr/ADR-002-stack-flask-sqlite.md` (Decisão: unicidade no banco); `tests/test_servicos.py` (`test_r2_o_banco_recusa_a_inscricao_repetida_pelo_unique`, `test_r3_o_banco_recusa_o_dispositivo_repetido_pelo_unique`).

**Avance para o slide 6.**

> ADR-002, a stack. A proposta da Aula 7 tinha Vue, Express, MongoDB e Docker: quatro serviços e um build de front-end para nove dias, e eu trabalho sozinho.

*Fonte:* `docs/adr/ADR-002-stack-flask-sqlite.md` (Contexto; Alternativas que descartei).

> Decidi por Flask e SQLite: instalar, testar e rodar em três comandos. O código vai de rotas a serviços a repositório, e a regra fica em `servicos.py`, testável sem servidor. Descartei o MEVN e o Flask com MongoDB.

*Fonte:* `docs/adr/ADR-002-stack-flask-sqlite.md` (Decisão; Alternativas); `README.md` (Estrutura).

> O preço: sem WebSocket, o mapa consulta a cada 3 segundos. Na demo, o banco recusa o duplicado. Nos testes, as regras rodam direto nos serviços.

*Fonte:* `docs/adr/ADR-002-stack-flask-sqlite.md` (Consequências); `src/schema.sql` (UNIQUE de R2 e R3).

**Avance para o slide 7.**

> ADR-003, o contrato do sinal. Sem hardware nem gateway no MVP, o simulador, o descarte e o mapa ainda dependem de um contrato. Qual é o menor que leva o sinal até a regra e ao mapa?

*Fonte:* `docs/adr/ADR-003-gateway-por-http.md` (Contexto).

> Decidi por HTTP com JSON. O simulador e o curl falam o mesmo contrato: 401 sem token, 202 descartado, 200 duplicado, 201 gravado. Descartei o MQTT, que traria broker, TLS e permissões por tópico, e volta com o gateway real.

*Fonte:* `docs/adr/ADR-003-gateway-por-http.md` (Decisão; Alternativas); `docs/api.md` (POST /api/v1/sinais); `docs/evidencias/curl-401-201.txt`.

> Na demo, vocês veem esses códigos no terminal. Nos testes, são as regras R7, R8 e R11.

*Fonte:* R7, R8 e R11 em `docs/backlog.md`; `tests/test_api.py` e `tests/test_servicos_inc2.py` (testes `test_r7_`, `test_r8_` e `test_r11_`).

### Bloco 4: Demo ao vivo (4:05–7:10)

#### 4a. H1: inscrever sem recadastrar (4:05–5:15)

**Mostre o slide 8, passo 1.**

> Hipótese 1: inscrever sem recadastrar. A meta é cinco operadores já cadastrados na Operação Charlie em até 3 minutos. Olhem o formulário, que não pede nome, e as três recusas.

*Fonte:* H1 em `docs/hipoteses-e-incrementos.md` (Ficha 11); o formulário não pede nome (`docs/evidencias/funcional.md`, seção 2, `02-inscricao-charlie.png`).

**Troque para a aba da Operação Charlie** (organizador, Planejada, sem inscritos). Não clique em "Iniciar operação".

> Esta é a Charlie, vazia. Os cinco operadores já estão cadastrados. Inscrever pede só time, classe, dispositivo e consentimento.

*Fonte:* `docs/adr/ADR-001-perfil-e-inscricao.md` (Decisão); R1 em `docs/backlog.md`; `src/demo_seed.py` (Charlie planejada e sem inscritos).

**Inscreva o Falcão** (Azul, Fuzileiro, MT-01, consentimento marcado, "Inscrever"). Depois, as três recusas, uma a uma. A cola está em "Preparação".

**Recusa 1.** Falcão de novo.

> Primeira recusa: o Falcão de novo. Regra R2.

*Fonte:* R2 em `docs/backlog.md`; mensagem "Este operador já está inscrito nesta operação." (`docs/evidencias/funcional.md`, seção 2, `03-recusa-duplicada.png`).

**Recusa 2.** Lobo com o dispositivo MT-01, consentimento marcado.

> Segunda: o Lobo com o dispositivo do Falcão. Regra R3.

*Fonte:* R3 em `docs/backlog.md`; `04-recusa-dispositivo.png`.

**Recusa 3.** Lobo com MT-02, consentimento desmarcado.

> Terceira: o Lobo sem consentimento. Regra R5.

*Fonte:* R5 em `docs/backlog.md`; mensagem "A inscrição exige o consentimento de rastreamento." (`05-recusa-consentimento.png`).

**Inscreva o Lobo (MT-02), a Coruja, a Raposa e a Pantera**, pelo teclado, em silêncio. Mostre a lista com 5 inscritos. **Volte aos slides e avance o slide 8 para o passo 2.**

> Cinco inscritos, nenhum cadastro refeito. Por script, o fluxo levou 554 milissegundos. Isso mede o sistema, não uma pessoa.

*Fonte:* `docs/evidencias/funcional.md` (seção 3, H1: 554 ms, com a ressalva de que a medição é automatizada); meta de 3 min em H1, `docs/hipoteses-e-incrementos.md`. `[conferir no ensaio: tempo cronometrado de H1 (31 ações e 3 recusas) e, se as telas novas mudarem o fluxo, a medição por script refeita; troque a fala pelo tempo medido]`

#### 4b. H2: quem está perdido (5:15–6:30)

**Mostre o slide 9, passo 1.**

> Hipótese 2: apontar quem está perdido, e há quanto tempo, em até 10 segundos depois de abrir o mapa. Olhem a faixa de contagem acima do mapa e o marcador com colchetes.

*Fonte:* H2 em `docs/hipoteses-e-incrementos.md`; faixa de dossiê e marcador do perdido em `DESIGN.md` (Components).

**Troque para a aba do mapa da Bravo** (já aberta, setas em movimento).

> Esta é a Operação Bravo, em curso. O simulador envia cinco dispositivos por HTTP, e o mapa consulta a API a cada 3 segundos.

*Fonte:* `docs/adr/ADR-003-gateway-por-http.md` (Decisão); `docs/adr/ADR-002-stack-flask-sqlite.md` (Consequências); `docs/historias.md` (US06).

**Aponte a faixa e o marcador da Coruja** (perdido, com colchetes e "perdido há ...").

> A faixa mostra um perdido: a Coruja, o MT-03, que o simulador parou de propósito. O rótulo diz há quanto tempo, e a lista põe os perdidos primeiro.

*Fonte:* R9 em `docs/backlog.md`; `DESIGN.md` (Faixa de dossiê; Marcador do mapa: "Coruja · perdido há 2 min 10 s"); `docs/evidencias/funcional.md` (seção 3: a lista põe perdidos e atrasados à frente); `docs/guia-de-reproducao.md` (passo 8: `--parar MT-03 --apos 20`). `[conferir no ensaio: a faixa mostra 1 perdido e 4 ativos, e o rótulo "perdido há X" aparece no marcador]`

**Aponte o contador "Sinais descartados".**

> O contador de descartados vem do MT-99, que não está inscrito: o sistema responde 202, descarta e só conta. É a regra R7. Pacote repetido responde 200 e não grava de novo: regra R8.

*Fonte:* R7 e R8 em `docs/backlog.md` (a tabela `descarte` guarda só origem e motivo); `docs/api.md` (POST /api/v1/sinais); `docs/historias.md` (US05); `docs/evidencias/curl-401-201.txt` (seções 3 e 4).

**Volte aos slides e avance o slide 9 para o passo 2.**

> Perdido é mais de 120 segundos sem sinal; atrasado, de 60 a 120. A regra do tempo, a R9, tem 39 testes, e eles injetam o relógio: 59, 60, 61, 119, 120 e 121 segundos.

*Fonte:* R9 em `docs/backlog.md` ("o 'agora' é injetável nos testes"); `docs/evidencias/funcional.md` (seção 1: `relogio.avancar`, `test_funcional_limites_exatos_dos_estados`); contagem de `test_r9_` (39 em 08/11/2026). `[conferir no ensaio: contagem de test_r9_]`

> Por script, a mediana foi 94 milissegundos: mede o fluxo, não uma pessoa.

*Fonte:* `docs/evidencias/funcional.md` (seção 3, H2: mediana de 94 ms, com a ressalva). `[conferir no ensaio: tempo humano de H2 com cronômetro, meta 10 s]`

#### 4c. H3 e H4: acesso e API (6:30–7:10)

**Mostre o slide 10, passo 1.**

> Hipóteses 3 e 4. No navegador, o observador: só lista e mapa, sem formulários. No terminal, os códigos da API.

*Fonte:* H3 e H4 em `docs/hipoteses-e-incrementos.md`; R10 em `docs/backlog.md`.

**Troque para a aba anônima** (observador, na Operação Bravo). **No terminal da demo, rode:** `python -m pytest tests/test_funcional.py -q -k observador_recebe_403` (menos de 1 s).

> A tela não tem formulário, então o 403 aparece no teste: toda escrita do observador é recusada. Passou.

*Fonte:* R10 em `docs/backlog.md`; `test_funcional_observador_recebe_403_em_toda_escrita` e as três escritas por `fetch` que deram 403 (`docs/evidencias/funcional.md`, seções 1 e 2, `08-observador.png`).

**No mesmo terminal, rode o curl 1 (sem token) e o curl 2 (com token); depois repita o curl 2** (seta para cima e Enter). **Volte aos slides e avance o slide 10 para o passo 2.**

> Sem token, 401. Com token, 201. O mesmo sinal de novo, 200, duplicado. É o contrato que o simulador usa e que um gateway real usaria.

*Fonte:* R11 em `docs/backlog.md`; `docs/api.md` (POST /api/v1/sinais: 401, 201 e 200); H4 em `docs/hipoteses-e-incrementos.md`; `docs/adr/ADR-003-gateway-por-http.md`; `docs/evidencias/curl-401-201.txt`.

### Bloco 5: Qualidade (7:10–8:25)

**Mostre o slide 11.**

> Qualidade. Cada regra, de R1 a R11, tem testes com o nome dela: de 4 na R5 a 39 na R9, a do tempo. A suíte inteira tem 474 testes, 66 deles de segurança. O número vem do pytest.

*Fonte:* contagem por prefixo do nome do teste (`test_r5_`: 4; `test_r9_`: 39), e total e segurança do `pytest --collect-only`, conferidos em 08/11/2026 (474 e 66). Como contar, no ensaio: ver "Preparação". `[conferir no ensaio: total, segurança e por regra; se o número for outro, troque na fala e no slide 11]`

**Avance para o slide 12.**

> Fiz também uma revisão de segurança: cinco achados, todos de severidade baixa. Quatro foram corrigidos: corpo sem limite, JSON aninhado que dava 500, tempo do login que revelava quem existe, e o simulador que seguia redirecionamento levando o token.

*Fonte:* `docs/evidencias/seguranca.md` (Achados S-1 a S-4, com o destino de cada um).

> O quinto, o token na linha de comando, aceitei: o Guia manda usar a variável de ambiente. O bandit e o pip-audit não apontaram nada alto nem vulnerabilidade conhecida.

*Fonte:* `docs/evidencias/seguranca.md` (S-5; seções bandit e pip-audit); `docs/guia-de-reproducao.md` (passo 8). `[conferir no ensaio: rodar de novo bandit, pip-audit e tests/test_seguranca.py, e atualizar os achados se houver novos]`

**Avance para o slide 13.**

> A reprodução pelo Guia, num clone limpo, é o critério do Incremento 3. Fiz uma em 8 de novembro, com as telas da Aula 14: 382 testes passaram, e o passo 11 travou no PowerShell. Refaço com as telas novas antes da v1.0, até 5 de dezembro.

*Fonte:* `docs/hipoteses-e-incrementos.md` (Ficha 12, Incremento 3: "reproduzido do zero, num clone limpo e num venv novo, seguindo só o Guia"); `docs/evidencias/funcional.md` (seção 4: clone do ramo `demo/mvp-10-11` no commit `c3998dc`, venv novo, só o Guia; 382 testes passaram; passos 2 e 11 com problema). A data de 05/12 é o prazo planejado pelo autor. `[conferir no ensaio: data, commit, testes e passos que travaram na reprodução com as telas novas; troque a última frase da fala por "Refiz em [data], no commit [hash]: [N] testes passaram e travei em [passos]"]`

### Bloco 6: O que mudou desde a Aula 14 (8:25–8:55)

**Mostre o slide 14.**

> O que mudou desde a Aula 14 foi a identidade das telas. À esquerda, o que mostrei em novembro. À direita, a versão atual: moldura preta, uma faixa com a contagem por estado acima do mapa, e o perdido com colchetes e o rótulo "perdido há", com o tempo. Os botões têm os mesmos nomes.

*Fonte:* antes: `docs/evidencias/06-mapa-ativos.png` e `07-mapa-perdido.png`; depois: `docs/evidencias/v1/` `[conferir no ensaio: a pasta está vazia; ponha os prints novos e confirme que o slide mostra os mesmos dois estados]`; identidade em `DESIGN.md` (Moldura e menu; Faixa de dossiê; Marcador do mapa); nomes dos botões em `src/servicos.py` (`ROTULO_TRANSICAO`) e `src/templates/operacao.html`.

### Bloco 7: Limites e próximos passos (8:55–10:00)

**Mostre o slide 15.**

> Os limites. A pendência principal é a validação com a federação: ainda não aconteceu e não tem data. Quem executou os roteiros fui eu, no papel de organizador, então os tempos medem o fluxo, não a primeira impressão de um organizador real.

*Fonte:* `PRODUCT.md` (Users: ninguém da federação validou até 08/11/2026 e não há data); `docs/hipoteses-e-incrementos.md` ("Quem valida"); `docs/backlog.md` (Dúvida em aberto 4). `[conferir no ensaio: a situação da federação continua a de 08/11/2026; só mude a fala se você avisar que mudou]`

> Os sinais são simulados. Falta definir por quanto tempo guardar as posições, porque posição de pessoa é dado pessoal, pela LGPD. E o fundo do mapa precisa de internet.

*Fonte:* `docs/api.md` (Fontes de sinal); `docs/backlog.md` (Dúvidas em aberto 1 e 2).

**Avance para o slide 16.**

> Os próximos passos. Um app de celular, ou um gateway MeshTracker que recebe os sinais por MQTT, enviando ao mesmo contrato HTTP. Nada disso está pronto, e não testei com dispositivo real. A hipótese 4 diz que trocar a fonte não muda a regra.

*Fonte:* `docs/api.md` (Fontes de sinal); `docs/adr/ADR-003-gateway-por-http.md` (Consequências); H4 em `docs/hipoteses-e-incrementos.md`.

> E conversar com a federação, que é o que falta para saber se o problema é real. Obrigado.

*Fonte:* `docs/proposta.md` (Risco principal); `docs/backlog.md` (Dúvida em aberto 4).

**Mostre o slide 17.**

## Palavras faladas

Contagem das linhas `>` de cada bloco, em 08/11/2026. A régua é 130 palavras por minuto: 1.173 palavras são 9 min 1 s de fala, e os 59 s que sobram dos 10 minutos são a folga para os cliques e a troca de aba. Para contar de novo, na raiz do repositório:

```bash
awk '/^## /{if(b)print n"\t"b; b=""; n=0} /^### Bloco/{if(b)print n"\t"b; b=$0; n=0} /^> /{sub(/^> /,""); n+=NF} END{if(b)print n"\t"b}' docs/apresentacao/roteiro-demo-day.md
```

| Bloco | Palavras | Tempo do bloco | Fala por minuto |
|---|---|---|---|
| 1. Motivo | 121 | 60 s | 121 |
| 2. Hipóteses e recorte | 116 | 55 s | 126 |
| 3. Os três ADRs | 271 | 130 s | 125 |
| 4. Demo ao vivo (H1, H2, H3 e H4) | 323 | 185 s | 105 |
| 5. Qualidade | 154 | 75 s | 123 |
| 6. O que mudou desde a Aula 14 | 55 | 30 s | 110 |
| 7. Limites e próximos passos | 133 | 65 s | 123 |
| **Total** | **1.173** | **10 min** | **117** |

Se mudar uma fala, conte de novo. O bloco 4 tem a maior folga (cerca de 40 s) porque são 31 ações de inscrição e três recusas; o tempo humano disso só se sabe no ensaio.

## Se o tempo apertar

| Marca | Se passou do tempo | Corte |
|---|---|---|
| 1:55 | Ainda no recorte | Leia só H1 e H2; H3 e H4 aparecem na demo (slide 10) |
| 4:05 | Ainda nos ADRs | Em cada ADR, diga só a decisão e a alternativa descartada; o contexto fica no slide |
| 5:15 | Ainda inscrevendo | Pare de inscrever, diga "faltam dois, o fluxo completo está na gravação" e vá para o mapa. As recusas não se cortam |
| 6:30 | Ainda no mapa | Pule a frase dos 94 milissegundos; ela volta nas perguntas |
| 7:10 | Ainda no curl | Pule o terceiro curl (o 200) |
| 8:25 | Ainda em Qualidade | Pule o slide 13: diga a frase da reprodução junto com o slide 12 |
| 8:55 | Ainda no bloco 6 | Diga só "mudou a identidade das telas, os botões são os mesmos" e passe ao slide 15; o antes e depois vai para as perguntas |
| 9:30 | Ainda nos limites | Corte "o fundo do mapa precisa de internet". A federação não se corta |

## Preparação antes de entrar na sala

**Na véspera (e de novo na manhã):**

1. Código no ar: a tag `v1.0` `[conferir no ensaio: a tag existe]`, com o ambiente virtual ativo. Rode `python -m pytest -q` e confira que tudo passa.
2. **Conte os testes** e troque os números na fala do bloco 5 e no slide 11 se forem outros:

```bash
python -m pytest --collect-only -q | tail -1                        # total (474 em 08/11/2026)
python -m pytest --collect-only -q tests/test_seguranca.py | tail -1   # segurança (66)
python -m pytest --collect-only -q -k "test_r9_" | tail -1          # uma regra; troque r9 por r1 a r11
```

3. Rode de novo a revisão de segurança (`python -m pip install -r requirements-dev.txt`, depois `python -m bandit -q -r src` e `python -m pip_audit -r requirements.txt`) e confira a tabela do slide 12 contra `docs/evidencias/seguranca.md`.
4. Defina `MESHTRACKER_SENHA_ORGANIZADOR` e `MESHTRACKER_SENHA_OBSERVADOR` antes do seed, para saber as senhas (sem isso, elas aparecem uma única vez).
5. Defina o mesmo `MESHTRACKER_TOKEN` nos três terminais (app, simulador e terminal da demo).
6. Ponha os prints novos em `docs/evidencias/v1/` e confira os slides 8, 9, 10 e 14.

**Montagem final, depois do último ensaio (o ensaio suja a Charlie e o banco):**

1. Pare o app e o simulador. Apague o banco (`rm instance/meshtracker.db`) e rode `python src/demo_seed.py` (`docs/guia-de-reproducao.md`, "Recomeçar do zero").
2. Suba o app (`python src/app.py`, porta 5000; se estiver ocupada, `--porta 5001` e ajuste as URLs).
3. **Ligue o simulador uns 3 minutos antes de abrir o mapa:** `python src/simulador.py --url http://127.0.0.1:5000 --parar MT-03 --apos 20`. O MT-03 para aos 20 s e fica perdido depois de uns 120 s sem sinal. Deixe o simulador rodando até o fim da fala.
4. Abas abertas, nesta ordem:
   - Slides, no slide 1.
   - **Operação Charlie**, logado como `organizador` (Operações, Operação Charlie). Planejada, 0 inscritos.
   - **Mapa da Bravo**, logado como `organizador` (Operações, Operação Bravo, Abrir mapa). Confira o MT-03 perdido, a faixa com 1 perdido e o rótulo "perdido há".
   - **Aba anônima**, logada como `observador`, na Operação Bravo.
5. **Terminal da demo** (Git Bash, raiz do repositório, venv ativo, `MESHTRACKER_TOKEN` exportado), com os comandos abaixo já no histórico. No PowerShell o `curl` é outro comando; use o Git Bash.
6. Internet ligada, para os tiles do OpenStreetMap (sem ela o fundo do mapa fica liso, e as setas continuam).
7. Zoom do navegador ajustado ao projetor (Ctrl e + até a lista e o formulário caberem), o mesmo nas quatro abas. Teste com o projetor, não só com a tela do notebook.

**Comandos do terminal da demo:**

```bash
# H3 (slide 10): teste do observador
python -m pytest tests/test_funcional.py -q -k observador_recebe_403

# curl 1: sem token, devolve 401
curl -s -w "  -> HTTP %{http_code}\n" -X POST http://127.0.0.1:5000/api/v1/sinais -H "Content-Type: application/json" -d '{"dispositivo": "MT-01", "pacote": 99, "lat": -15.799, "lon": -47.907, "bateria": 80}'

# curl 2: com token, devolve 201 (repetido, devolve 200 duplicado)
curl -s -w "  -> HTTP %{http_code}\n" -X POST http://127.0.0.1:5000/api/v1/sinais -H "Authorization: Bearer $MESHTRACKER_TOKEN" -H "Content-Type: application/json" -d '{"dispositivo": "MT-01", "pacote": 99, "lat": -15.799, "lon": -47.907, "bateria": 80}'
```

Fonte dos comandos: `docs/guia-de-reproducao.md` (passo 11) e `docs/api.md`; os mesmos do `roteiro-5min.md`.

**Cola de inscrição da Charlie** (todos diferentes dos times da Bravo no `src/demo_seed.py`):

| Ordem | Operador | Time | Classe | Dispositivo | Observação |
|---|---|---|---|---|---|
| 1 | Falcão | Azul | Fuzileiro | MT-01 | Entra primeiro |
| recusa 1 | Falcão | qualquer | qualquer | MT-01 | R2 |
| recusa 2 | Lobo | Vermelho | Suporte | MT-01 | R3, consentimento marcado |
| recusa 3 | Lobo | Vermelho | Suporte | MT-02 | R5, consentimento desmarcado |
| 2 | Lobo | Vermelho | Suporte | MT-02 | Agora com consentimento |
| 3 | Coruja | Verde | Médico | MT-03 | |
| 4 | Raposa | Amarelo | Atirador designado | MT-04 | |
| 5 | Pantera | Azul | Suporte | MT-05 | |

As recusas vêm antes da quinta inscrição de propósito: com os cinco inscritos, qualquer tentativa bate antes na R2 (a R2 vence a R3), e o dispositivo repetido não aparece (`docs/evidencias/funcional.md`, seção 2, nota "Jaguar"). Para ir rápido, use o teclado: Tab entre os campos, a letra inicial nos selects, Espaço no consentimento, Enter em "Inscrever". Se o formulário voltar vazio depois de uma recusa, escolha de novo.

**Cuidados na hora:**

- Depois de uma recusa (400), a barra de endereço fica na URL do POST. **Não dê F5**: reenvia o formulário (`docs/evidencias/funcional.md`, seção 5).
- **Não use o MT-03 no curl.** Um sinal com token reviveria o perdido. Use só o MT-01.
- Não clique em "Iniciar operação" na Charlie: só uma operação fica em curso por vez (R6). Não clique em "Encerrar operação" na Bravo: o simulador passa a receber 202, o mapa para de andar, e a operação encerrada não volta a ficar em curso (R6, só avança).
- O curl com token grava uma posição no MT-01 e a seta dele pode dar um salto. Não é problema (`docs/guia-de-reproducao.md`, passo 11).
- O pacote 99 não colide com o simulador. Se o 201 já foi rodado nesse banco no ensaio, a resposta será 200: refaça o seed.

## Plano B

**Se o ao vivo falhar:** use os prints de `docs/evidencias/` (telas da Aula 14; diga isso em voz alta), os prints novos de `docs/evidencias/v1/` e a gravação de tela do ensaio. A gravação ainda precisa ser feita: gravar o bloco 4 inteiro no ensaio, com o app já montado como acima, e guardar o arquivo fora do repositório, no desktop.

| Bloco | Material que serve | Observação |
|---|---|---|
| 1, 2, 3, 7 | nenhum (slides) | |
| 4a (H1) | `01-operadores.png`, `02-inscricao-charlie.png`, `03-recusa-duplicada.png`, `04-recusa-dispositivo.png`, `05-recusa-consentimento.png` | O `04` usa um 6º operador, o Jaguar, tentando o MT-01; ao vivo é o Lobo |
| 4b (H2) | `06-mapa-ativos.png`, `07-mapa-perdido.png` | O `06` mostra os 5 ativos e o contador de descartados (MT-99); o `07` mostra o MT-03 perdido |
| 4c (H3, H4) | `08-observador.png`, `curl-401-201.txt` | O arquivo de texto traz 401, 201, 200 e 202; o token aparece só como `$MESHTRACKER_TOKEN` |
| 5 | `docs/evidencias/seguranca.md` (tabela de achados) | O número de testes se confere no terminal |
| 6 | `docs/evidencias/06-mapa-ativos.png` e `07-mapa-perdido.png` contra `docs/evidencias/v1/` | Os prints novos ainda não existem |

**Falhas prováveis:**

| Sintoma | O que fazer |
|---|---|
| Mapa sem fundo | Siga em frente: as setas continuam. Diga que o fundo depende de internet (dúvida em aberto 1 do backlog) |
| MT-03 não está perdido no topo, e a faixa não mostra 1 perdido | O simulador foi ligado tarde. Mostre `07-mapa-perdido.png` e diga que o estado sai do tempo desde o último sinal |
| Simulador com 401 | Token diferente nos terminais. Mostre `06` e `07` e vá para a API (`docs/guia-de-reproducao.md`, Problemas comuns) |
| Charlie já tem inscritos | Crie uma operação nova em Operações (nome, data e local; nasce planejada) e use a cola nela. Ou use os prints `02` a `05` |
| App não sobe | Gravação de tela do ensaio, mais os prints |

## Perguntas prováveis

**Por que perfil e inscrição separados?**
O mesmo operador joga várias operações, e time, classe e dispositivo mudam de uma para outra. Guardar isso no perfil perderia o valor anterior, e cadastrar dentro de cada operação força o recadastro. O consentimento vale por inscrição. O preço é ter mais entidades e telas, e um identificador estável do operador: não sei se a federação tem número de registro. *Fonte:* `docs/adr/ADR-001-perfil-e-inscricao.md` (Alternativas, Consequências); `docs/backlog.md` (Dúvida em aberto 3).

**Por que Flask e não MEVN?**
A stack MEVN tinha quatro serviços e um build de front-end, para nove dias e uma pessoa, e a demo precisava ser independente do operational-command. Com Flask e SQLite o projeto instala, testa e roda com três comandos, e a regra de negócio fica em `servicos.py`, testável sem servidor. O preço é não ter WebSocket: o mapa consulta a cada 3 segundos. *Fonte:* `docs/adr/ADR-002-stack-flask-sqlite.md`.

**Por que HTTP e não MQTT?**
Sem hardware nem gateway no MVP, o MQTT traria um broker, TLS e permissões por tópico sem mudar o que o organizador vê. HTTP com JSON é o menor contrato que leva o sinal até a regra e ao mapa, e qualquer cliente, como o `curl`, testa. O preço é perder o QoS do MQTT, então a deduplicação virou a regra R8. O MQTT volta com o gateway real, por um novo ADR. *Fonte:* `docs/adr/ADR-003-gateway-por-http.md`.

**Como R2 e R3 são garantidas?**
Por restrições UNIQUE no SQLite, na tabela de inscrição: (operador, operação) para a R2 e (operação, dispositivo) para a R3. O banco recusa mesmo que o código falhe, e o serviço transforma a recusa em mensagem na própria página. A R6, só uma operação em curso por vez, é garantida por um índice único. *Fonte:* `src/schema.sql`; `docs/adr/ADR-002-stack-flask-sqlite.md` (Decisão); testes `test_r2_o_banco_recusa_a_inscricao_repetida_pelo_unique` e `test_r3_o_banco_recusa_o_dispositivo_repetido_pelo_unique`.

**Como se testa o tempo?**
O "agora" é um parâmetro, e nos testes um relógio injetado avança sem esperar. Os limites ficam testados em 59, 60, 61, 119, 120 e 121 segundos. Em uso normal, os limites são configuráveis por `MESHTRACKER_ATRASADO_S` (60) e `MESHTRACKER_PERDIDO_S` (120). *Fonte:* R9 em `docs/backlog.md`; `docs/evidencias/funcional.md` (seção 1); `docs/guia-de-reproducao.md` (Variáveis de ambiente).

**E o consentimento e a LGPD?**
Existe: a inscrição exige consentimento de rastreamento (R5), e ele vale por operação (ADR-001); sinal de quem não está inscrito nunca vira posição (R7), e só se registra a origem e o motivo; o observador só lê (R10). Falta o prazo de guarda das posições depois da operação, que é dúvida em aberto. *Fonte:* `docs/backlog.md` (R5, R7, R10, Dúvida em aberto 2); `docs/adr/ADR-001-perfil-e-inscricao.md` (Consequências).

**O que foi feito em segurança?**
Token de formulário contra CSRF, senha em hash, token do gateway comparado com `hmac.compare_digest`, SQL só parametrizado, saída HTML escapada, `mapa.js` só com `textContent` e CSP sem script inline. Saíram cinco achados baixos (S-1 a S-5): quatro corrigidos e o quinto, o token na linha de comando, aceito, porque o Guia recomenda a variável de ambiente. *Fonte:* `docs/evidencias/seguranca.md`; `docs/guia-de-reproducao.md` (passo 8).

**Por que os sinais são simulados?**
Porque o MVP não tem hardware nem gateway: foi o recorte dos ADR-002 e ADR-003. O simulador chama o mesmo endpoint que um gateway chamaria, então trocar a fonte não deve mudar a regra, e essa é a hipótese 4. Não testei com dispositivo real. *Fonte:* `docs/adr/ADR-003-gateway-por-http.md`; H4 em `docs/hipoteses-e-incrementos.md`; `docs/api.md` (Fontes de sinal).

**Isto foi validado com um organizador?**
Não. Os roteiros foram executados por mim, no papel de organizador, e medem o fluxo, não a primeira impressão de um organizador real. A conversa com a federação é a pendência principal: não tem data, e o problema do recadastro e da visão de conjunto é o que percebi olhando para os meus projetos, não algo que a federação confirmou. *Fonte:* `PRODUCT.md` (Users); `docs/hipoteses-e-incrementos.md` ("Quem valida"); `docs/proposta.md` (Risco principal); `docs/backlog.md` (Dúvida em aberto 4).

**O que mudou nas telas desde a Aula 14? Os testes pegaram?**
Mudou a aparência: moldura preta, faixa de contagem, colchetes no perdido. Alguns testes conferem o HTML: o observador não vê formulários, todo formulário leva o `csrf_token` e nenhum texto vindo do servidor entra no mapa por `innerHTML`. *Fonte:* `DESIGN.md`; `README.md` ("Para mexer no layout e no front"). `[conferir no ensaio: a suíte passa com as telas novas]`

**Já reproduziu o projeto pelo Guia?**
Sim, uma vez. Em 08/11 clonei o ramo `demo/mvp-10-11` (commit `c3998dc`) numa pasta limpa, criei um venv novo e segui só o Guia: 382 testes passaram. Ficaram ambíguos o passo 2 (a frase do `py -3.12` contradizia "3.12 ou mais novo"), o passo 9 (o "Clique em Operações" era redundante) e o passo 11, que travou no PowerShell porque o `curl` ali é outro comando. Foi com as telas da Aula 14; refaço com as telas novas antes da v1.0, até 05/12. *Fonte:* `docs/evidencias/funcional.md` (seções 4 e 5); `docs/hipoteses-e-incrementos.md` (Ficha 12). `[conferir no ensaio: data, commit, testes e passos que travaram na reprodução com as telas novas]`

**Quando o MQTT entra?**
Quando houver gateway real. O gateway recebe os sinais por MQTT e os envia ao mesmo contrato HTTP; trocar o contrato exigiria um novo ADR. Nada disso está pronto. *Fonte:* `docs/api.md` (Fontes de sinal); `docs/adr/ADR-003-gateway-por-http.md` (Justificativa).

## Marcadores para o ensaio

Cada `[conferir no ensaio: ...]` do texto, reunido aqui. Nenhum resultado abaixo existe em 08/11/2026.

| # | O que conferir | Onde entra | Como |
|---|---|---|---|
| 1 | Tag `v1.0` criada em 08/12 e app rodando dela | Abertura deste arquivo; slide 17 | `git tag`; subir o app da tag |
| 2 | Trilha dos últimos 10 pontos e CSV: de fora ou entregues | Slide 4 | `docs/backlog.md`, linha D |
| 3 | Tempo cronometrado de H1 (31 ações e 3 recusas, meta 3 min) e medição por script nas telas novas | Bloco 4a; slide 8, passo 2 | Cronômetro no ensaio, com gravação de tela |
| 4 | Faixa com 1 perdido e 4 ativos; rótulo "perdido há X" no marcador | Bloco 4b; slide 9 | Olhar o mapa depois de 3 minutos de simulador |
| 5 | Tempo humano de H2 (meta 10 s) e mediana por script nas telas novas | Bloco 4b; slide 9, passo 2 | Cronômetro no ensaio |
| 6 | Total de testes, de segurança e por regra | Bloco 5; slides 9 e 11 | Comandos de contagem em "Preparação" |
| 7 | bandit, pip-audit e `tests/test_seguranca.py` rodados de novo | Bloco 5; slide 12 | Comandos em "Preparação", item 3 |
| 8 | Resultado da reprodução com as telas novas (planejada até 05/12) | Bloco 5; slide 13; pergunta sobre o Guia | Clone limpo, venv novo, só o Guia |
| 9 | Prints novos em `docs/evidencias/v1/` | Bloco 6; slides 8, 9, 10 e 14 | Tirar os prints com o app montado |
| 10 | Suíte verde com as telas novas | Pergunta sobre as telas | `python -m pytest -q` |
| 11 | A situação da federação continua a de 08/11/2026 | Bloco 7; slide 15 | Só o autor pode confirmar |
