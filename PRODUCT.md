# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Organizador** de operações de airsoft da Federação do Distrito Federal e entorno: monta a operação, inscreve os jogadores e acompanha o que acontece em campo. Usa o app num notebook, em campo, durante a operação.
- **Observador:** acompanha listas e mapa só para leitura (R10). Não vê formulários.
- **Integrador do gateway:** fala com o app só pela API `/api/v1`, com token (R11). Hoje é o simulador; depois, um gateway MQTT ou um app de celular no mesmo contrato HTTP.
- **Avaliador do curso** (professor, banca do Demo Day em 15/12/2026): assiste à apresentação no projetor e pode reproduzir o MVP pelo Guia.

Ninguém da federação validou o produto até 08/11/2026. A validação foi feita só pelo autor, no papel de organizador, e não há data para a conversa com a federação.

## Product Purpose

O MeshTracker Central liga a inscrição dos operadores ao rastreamento em campo. O organizador cadastra cada operador uma vez, inscreve-o em cada operação com time, classe, dispositivo e consentimento, e acompanha num mapa ao vivo quem está ativo, atrasado ou perdido.

Sucesso, pelas hipóteses (`docs/hipoteses-e-incrementos.md`):
- H1: inscrever 5 operadores já cadastrados numa 2ª operação, sem redigitar dados, em até 3 min;
- H2: apontar quem está perdido e há quanto tempo em até 10 s depois de abrir o mapa;
- H3: nenhum sinal de não inscrito vira posição e nenhuma escrita do observador passa;
- H4: o simulador e um `curl` usam só a API, sem tocar no banco.

## Positioning

É a central que falta entre dois projetos do autor: o operational-command (gestão de operações) e o dispositivo MeshTracker (ESP32-S3, GPS e malha LoRa de 433 MHz), em que cada dispositivo só enxerga os vizinhos e esquece quem some por 2 minutos. A central dá a visão de conjunto que a malha sozinha não dá, e o perfil permanente acaba com o recadastro.

## Operating Context

- **App (`/login`, `/operadores`, `/operacoes`, `/operacoes/<id>`, `/operacoes/<id>/mapa`):** superfície de trabalho, modo Operate. Notebook em campo, olhada rápida no mapa a cada poucos segundos, formulários de inscrição em sequência. O mapa atualiza a cada 3 s.
- **Decks (`docs/apresentacao/`):** superfície de apresentação, modo Persuade. Projetor em sala de aula, palco de 1920 px, apresentação de 10 minutos no Demo Day e de 5 minutos na Aula 14. O deck oficial é o suíço (`slides-suico.html`).
- O fundo do mapa vem dos tiles do OpenStreetMap e precisa de internet; sem ela, os marcadores aparecem sobre fundo liso. Tiles offline são dúvida em aberto (`docs/backlog.md`).

## Capabilities and Constraints

- Regras R1 a R11 (`docs/backlog.md`), todas com testes. Estados do operador: sem sinal, ativo (até 60 s), atrasado (60 a 120 s), perdido (acima de 120 s).
- Flask, Jinja e `sqlite3` sem ORM (ADR-002). Sem build de front-end e sem dependência nova de Python. Leaflet e as fontes (Archivo e Chivo Mono) servidos pelo próprio app em `src/static/vendor/`.
- CSP `default-src 'self'` e `script-src 'self'`: nada de script inline nem fonte externa. Todo texto vindo do servidor entra no mapa por `textContent`.
- Times (Azul, Vermelho, Verde, Amarelo) e classes (Fuzileiro, Suporte, Atirador designado, Médico) são listas fixas no código.
- Fora do MVP: MQTT, gateway real, ordens, objetivos, topologia da malha, integração com o operational-command e app de celular.
- Em aberto: prazo de guarda das posições (LGPD), identificador da federação para o operador, listas de times e classes da federação.

## Brand Commitments

- Nome: MeshTracker Central. Textos em português do Brasil, diretos, sem jargão de marketing.
- Direção visual confirmada pelo usuário em 08/11/2026 para as telas do app: briefing tático pré-missão sobre a base do deck suíço. O detalhe é do `DESIGN.md`.
- Anti-referências obrigatórias: nada copiado de jogos (logo, nome, fontes, telas, sons, personagens); nada de armas, insígnias, patentes, caveiras ou brasões; nada de dado inventado para enfeitar.

## Evidence on Hand

- Seed da demo (`src/demo_seed.py`): 5 operadores, operações Alfa (encerrada), Bravo (em curso, no Parque da Cidade, com o simulador) e Charlie (planejada e vazia), usuários `organizador` e `observador`.
- Prints, tempos e revisão de segurança S-1 a S-5 em `docs/evidencias/`. 474 testes em 08/11/2026, 66 deles de segurança.
- Os sinais são simulados. Não há depoimento, cliente, uso real nem validação com a federação: nada disso pode aparecer como fato.

## Product Principles

1. Todo número na tela vem do sistema ou do conteúdo real do repositório.
2. A regra aparece onde o organizador age: recusa na própria página, com o motivo em texto.
3. O estado do operador sempre tem texto ao lado da cor, e as cores de estado são as mesmas no mapa, na lista, no deck e no `DESIGN.md`.
4. Vermelho só para recusa e perda.
5. O que é limite do MVP é dito como limite, não escondido.

## Accessibility & Inclusion

- App: contraste de pelo menos 4,5:1, texto de pelo menos 16 px, foco visível, e nenhuma animação em dado que se atualiza a cada 3 s além de uma transição curta de estado. Respeitar `prefers-reduced-motion`.
- Deck: texto legível no projetor (corpo de pelo menos 26 px no palco de 1920) e texto secundário com contraste alto.
