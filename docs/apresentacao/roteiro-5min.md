# Roteiro da demo de 5 minutos

Terça, 10/11/2026, Aula 14. Rafael Alves de Sousa Costa apresenta ao professor avaliador o MeshTracker Central, com o código do ramo `demo/mvp-10-11`.

Como ler este arquivo: as linhas que começam com `>` são o que eu digo em voz alta (é só o que conta para os 5 minutos). As linhas em negrito são o que eu clico ou mostro. Cada fala tem logo abaixo a fonte que a justifica. Nenhuma fala afirma validação com a federação de airsoft: ela não aconteceu. Quem executou os roteiros fui eu, no papel de organizador (`docs/hipoteses-e-incrementos.md`, seção "Quem valida").

## Resumo em uma tabela

| Tempo | Bloco | Mostra | Justificativa |
|---|---|---|---|
| 0:00–0:30 | Problema e usuário | slide 1 | `docs/proposta.md`, `README.md` |
| 0:30–1:30 | H1 ao vivo | inscrever os 5 operadores já cadastrados na Operação Charlie; recusas de inscrição duplicada, dispositivo repetido e falta de consentimento | `docs/adr/ADR-001-perfil-e-inscricao.md`, R1 a R6 em `docs/backlog.md`, UNIQUE no banco (`docs/adr/ADR-002-stack-flask-sqlite.md`) |
| 1:30–3:00 | Mapa ao vivo (H2) | setas em movimento, MT-03 perdido, MT-99 no contador de descartados | R7 a R9 em `docs/backlog.md`, `docs/adr/ADR-003-gateway-por-http.md`, relógio injetável (R9 e `docs/evidencias/funcional.md`) |
| 3:00–3:45 | Acesso e API (H3, H4) | observador sem formulários e com 403; curl sem token (401) e com token (201) | R10 e R11 em `docs/backlog.md`, `docs/api.md` |
| 3:45–4:30 | Decisões | slide 5: o recorte do escopo, Flask e SQLite no lugar de MEVN, HTTP no lugar de MQTT, número de testes por regra | `docs/adr/ADR-002-stack-flask-sqlite.md`, `docs/adr/ADR-003-gateway-por-http.md`, `docs/hipoteses-e-incrementos.md` (Fichas 11 e 12) |
| 4:30–5:00 | Limites e próximos passos | slide 6: validado só pelo autor, sinais simulados; app de celular e gateway MQTT falando o mesmo contrato HTTP; conversa com a federação | `docs/hipoteses-e-incrementos.md`, dúvidas em aberto em `docs/backlog.md`, `docs/api.md` (Fontes de sinal) |

## Texto falado

### Bloco 1: Problema e usuário (0:00–0:30)

**Mostre o slide 1.** Conteúdo mínimo: título "MeshTracker Central"; o usuário (organizador de operações de airsoft do DF); os dois problemas; "demo com sinais simulados".

> Este é o MeshTracker Central, um painel web para o organizador de operações de airsoft do Distrito Federal.

*Fonte:* `docs/proposta.md` (Usuário principal, Proposta de solução); `README.md`.

> Percebi dois problemas olhando para o meu projeto. O operador teria de se cadastrar de novo a cada operação. E cada dispositivo esquece quem some por 2 minutos, então ninguém vê o conjunto.

*Fonte:* `docs/proposta.md` (Problema observado); `README.md` ("Por que este projeto existe"); `docs/adr/ADR-001-perfil-e-inscricao.md` (Contexto).

> Não confirmei isso com a federação. Mostro o que está pronto, com sinais simulados.

*Fonte:* `docs/proposta.md` ("Ainda não confirmei com a federação"; Risco principal); `README.md`.

### Bloco 2: H1 ao vivo (0:30–1:30)

**Vá para a aba da Operação Charlie** (organizador, situação Planejada, sem inscritos). Não clique em "Iniciar operação".

> Esta é a Operação Charlie, vazia. Os cinco operadores já estão cadastrados. Inscrever pede só time, classe, dispositivo e consentimento: nenhum dado pessoal de novo. É a hipótese 1.

*Fonte:* `docs/adr/ADR-001-perfil-e-inscricao.md` (Decisão: o perfil é permanente e a inscrição guarda o que muda); R1 em `docs/backlog.md`; H1 em `docs/hipoteses-e-incrementos.md`; o formulário não pede nome (`docs/evidencias/funcional.md`, seção 2, `02-inscricao-charlie.png`).

**Inscreva o Falcão** (Azul, Fuzileiro, MT-01, consentimento marcado, "Inscrever"). Depois, as três recusas, uma a uma. A cola completa está em "Preparação".

**Recusa 1.** Falcão de novo.

> Primeira recusa: o mesmo operador de novo. Regra R2.

*Fonte:* R2 em `docs/backlog.md`; mensagem "Este operador já está inscrito nesta operação." (`docs/evidencias/funcional.md`, seção 2, `03-recusa-duplicada.png`).

**Recusa 2.** Lobo com o dispositivo MT-01, consentimento marcado.

> Segunda: o Lobo com o dispositivo do Falcão. Regra R3. As duas são restrições UNIQUE no banco, não só no código.

*Fonte:* R3 em `docs/backlog.md`; UNIQUE de (operador, operação) e de (operação, dispositivo) em `docs/adr/ADR-002-stack-flask-sqlite.md` (Decisão); `04-recusa-dispositivo.png`.

**Recusa 3.** Lobo com MT-02, consentimento desmarcado.

> Terceira: o Lobo sem consentimento. Regra R5. Sem consentimento, não há inscrição.

*Fonte:* R5 em `docs/backlog.md`; mensagem "A inscrição exige o consentimento de rastreamento." (`05-recusa-consentimento.png`).

**Inscreva o Lobo (MT-02), a Coruja, a Raposa e a Pantera**, pelo teclado, em silêncio (cola em "Preparação"). Ao terminar, mostre a lista com 5 inscritos.

> Cinco inscritos, nenhum cadastro refeito. Rodei esse fluxo por script: 554 milissegundos, para uma meta de 3 minutos. Isso mede o sistema, não um organizador real.

*Fonte:* `docs/evidencias/funcional.md` (seção 3, H1: 554 ms, com a ressalva de que a medição é automatizada); meta de 3 min em H1, `docs/hipoteses-e-incrementos.md`.

### Bloco 3: Mapa ao vivo, H2 (1:30–3:00)

**Vá para a aba do mapa da Bravo** (já aberta, setas se movendo).

> Esta é a Operação Bravo, em curso. O simulador envia a posição de cinco dispositivos por HTTP, no contrato do ADR-003. As setas se movem sem recarregar a página. Ela consulta a API a cada 3 segundos, porque não usei WebSocket. A cor é o time.

*Fonte:* `docs/adr/ADR-003-gateway-por-http.md` (Decisão); `docs/adr/ADR-002-stack-flask-sqlite.md` (Consequências: sem WebSocket, consulta a cada 3 s); `docs/historias.md` (US06).

**Aponte a primeira linha da lista** (Coruja, em vermelho, "Perdido").

> A primeira da lista é a Coruja, perdida há mais de 2 minutos. O simulador parou o dispositivo dele, o MT-03, de propósito. Perdido é mais de 120 segundos sem sinal. Atrasado, de 60 a 120. A lista põe os perdidos primeiro.

*Fonte:* R9 em `docs/backlog.md`; `docs/historias.md` (US06); `docs/evidencias/funcional.md` (seção 3: a lista põe perdidos e atrasados à frente; `07-mapa-perdido.png`); `docs/guia-de-reproducao.md` (passo 8: `--parar MT-03 --apos 20`).

> Hipótese 2: apontar o perdido em até 10 segundos. Por script, a mediana foi 94 milissegundos. De novo, isso mede o fluxo, não uma pessoa.

*Fonte:* H2 em `docs/hipoteses-e-incrementos.md`; `docs/evidencias/funcional.md` (seção 3, H2: mediana de 94 ms, com a ressalva).

> Esperar dois minutos a cada teste seria inviável. Por isso o relógio é injetado nos testes: 59, 60, 61, 119, 120 e 121 segundos.

*Fonte:* R9 em `docs/backlog.md` ("o 'agora' é injetável nos testes"); `docs/evidencias/funcional.md` (seção 1: `relogio.avancar`, `test_funcional_limites_exatos_dos_estados`); os testes de R9 em `tests/` (contagem do autor, ver a lista de perguntas).

**Aponte o contador "Sinais descartados".**

> Agora o contador de descartados. O MT-99 não está inscrito. O sistema responde 202, descarta e só conta. A posição dele nunca vira dado gravado. É a regra R7. Uma parte dos pacotes o simulador reenvia de propósito: o sistema responde 200, duplicado, e não grava de novo. Regra R8.

*Fonte:* R7 e R8 em `docs/backlog.md` (a tabela `descarte` guarda só origem e motivo); respostas 202 e 200 em `docs/adr/ADR-003-gateway-por-http.md` e `docs/api.md` (POST /api/v1/sinais); `docs/historias.md` (US05: o simulador reenvia uma fração dos pacotes); `docs/evidencias/curl-401-201.txt` (seções 3 e 4).

### Bloco 4: Acesso e API, H3 e H4 (3:00–3:45)

**Vá para a aba anônima** (observador, na Operação Bravo).

> Agora o acesso. Esta aba é o observador. Ele vê a lista e o mapa. Não tem botão de iniciar, alterar ou inscrever. É a hipótese 3: o observador só lê.

*Fonte:* R10 em `docs/backlog.md`; H3 em `docs/hipoteses-e-incrementos.md`; `docs/evidencias/funcional.md` (seção 2, `08-observador.png`).

**No terminal da demo, rode:** `python -m pytest tests/test_funcional.py -q -k observador_recebe_403` (leva menos de 1 s).

> Como a tela não tem formulário, o 403 aparece no teste: toda escrita do observador é recusada. Passou.

*Fonte:* R10 em `docs/backlog.md`; `test_funcional_observador_recebe_403_em_toda_escrita` e as três escritas por `fetch` que deram 403 (`docs/evidencias/funcional.md`, seções 1 e 2).

**No mesmo terminal, rode o curl 1 (sem token) e o curl 2 (com token); depois repita o curl 2** (seta para cima e Enter). Os comandos estão em "Preparação".

> Hipótese 4: a API. Sem token, 401. Com token, 201. O mesmo sinal de novo, 200, duplicado. É o contrato que o simulador usa e que um gateway real usaria.

*Fonte:* R11 em `docs/backlog.md`; `docs/api.md` (POST /api/v1/sinais: 401, 201 e 200); H4 em `docs/hipoteses-e-incrementos.md`; `docs/adr/ADR-003-gateway-por-http.md`; `docs/evidencias/curl-401-201.txt`.

### Bloco 5: Decisões (3:45–4:30)

**Mostre o slide 5.** Conteúdo mínimo: quatro linhas (Recorte; Flask e SQLite, não MEVN; HTTP, não MQTT; Testes por regra) e a tabela de testes por regra, com o total de testes da suíte.

> Quatro decisões. Primeira, o recorte. Ficou fora o que exige hardware ou outro sistema: MQTT, gateway real e integração com o operational-command.

*Fonte:* `README.md` ("O que fica de fora"); `docs/backlog.md` (Funcionalidades, linha F); `docs/hipoteses-e-incrementos.md` (Ficha 12).

> Segunda, Flask e SQLite no lugar de Vue, Express e MongoDB. Eram quatro serviços e um build de front-end para nove dias, e eu trabalho sozinho.

*Fonte:* `docs/adr/ADR-002-stack-flask-sqlite.md` (Contexto e Alternativas que descartei).

> Terceira, HTTP no lugar de MQTT: o menor contrato que leva o sinal até a regra e ao mapa. O MQTT volta com o gateway real.

*Fonte:* `docs/adr/ADR-003-gateway-por-http.md` (Justificativa).

> Quarta, os testes. Cada regra tem de 4 a 39 testes com o nome dela: a R5 tem 4, a R9, a do tempo, tem 39. A suíte tem 407 testes verdes.

*Fonte:* contagem por prefixo do nome do teste na pasta `tests/` (R1 16, R2 5, R3 6, R4 7, R5 4, R6 17, R7 13, R8 11, R9 39, R10 16, R11 14; são o piso, porque outros testes também cobrem as regras); total conferido com `python -m pytest --collect-only -q` (407 testes coletados em 08/11/2026). A lista de regras está em `docs/backlog.md`; a Definição de Pronto, em `docs/hipoteses-e-incrementos.md` (Ficha 12).

### Bloco 6: Limites e próximos passos (4:30–5:00)

**Mostre o slide 6.** Duas colunas: Limites e Próximos passos.

> Limites. Quem executou os roteiros fui eu, no papel de organizador. Os sinais são simulados, e os tempos vieram de script. O fundo do mapa precisa de internet. Falta definir por quanto tempo guardar as posições.

*Fonte:* `docs/hipoteses-e-incrementos.md` ("Quem valida"); `docs/evidencias/funcional.md` (seção 3); `docs/backlog.md` (Dúvidas em aberto 1 e 2).

> Próximos passos. Um app de celular ou um gateway MeshTracker, por MQTT, enviando ao mesmo contrato HTTP. E conversar com a federação, que ainda não aconteceu. Obrigado.

*Fonte:* `docs/api.md` (Fontes de sinal); `docs/adr/ADR-003-gateway-por-http.md` (Consequências); `docs/backlog.md` (Dúvidas em aberto 3 e 4); `docs/proposta.md` (Risco principal).

## Palavras faladas

Contagem das linhas `>` de cada bloco, em 08/11/2026. O total cabe em 5 minutos, com folga para os cliques.

| Bloco | Palavras | Tempo do bloco |
|---|---|---|
| 1. Problema e usuário | 65 | 30 s |
| 2. H1 ao vivo | 97 | 60 s |
| 3. Mapa ao vivo (H2) | 187 | 90 s |
| 4. Acesso e API (H3, H4) | 79 | 45 s |
| 5. Decisões | 106 | 45 s |
| 6. Limites e próximos passos | 63 | 30 s |
| **Total** | **597** | **5 min** |

Se mudar uma fala, conte de novo: o bloco 5 já é o mais apertado (cerca de 140 palavras por minuto).

## Se o tempo apertar

| Marca | Se passou do tempo | Corte |
|---|---|---|
| 1:30 | Ainda faltam inscrições | Pare de inscrever, diga "faltam dois, o fluxo completo está na gravação" e vá para o mapa. As recusas não se cortam |
| 3:00 | Ainda no mapa | Pule a frase do relógio injetável; ela volta nas perguntas |
| 3:45 | Ainda no curl | Pule o terceiro curl (o 200) |
| 4:30 | Ainda nas decisões | Leia só as linhas do slide, sem a explicação |

## Preparação antes de entrar na sala

**Na véspera (e de novo na manhã):**

1. Ramo `demo/mvp-10-11` no ar, com o ambiente virtual ativo. Rode `python -m pytest -q` e confira que tudo passa e qual é o total. Se não for 407, troque o número na fala do bloco 5 e na tabela do slide 5.
2. Defina `MESHTRACKER_SENHA_ORGANIZADOR` e `MESHTRACKER_SENHA_OBSERVADOR` antes do seed, para saber as senhas (sem isso, elas aparecem uma única vez).
3. Defina o mesmo `MESHTRACKER_TOKEN` nos três terminais (app, simulador e terminal da demo).

**Montagem final, depois do último ensaio (ensaio suja a Charlie e o banco):**

1. Pare o app e o simulador. Apague o banco (`rm instance/meshtracker.db`) e rode `python src/demo_seed.py` (`docs/guia-de-reproducao.md`, "Recomeçar do zero").
2. Suba o app (`python src/app.py`, porta 5000; se estiver ocupada, `--porta 5001` e ajuste as URLs).
3. **Ligue o simulador uns 3 minutos antes de abrir o mapa:** `python src/simulador.py --url http://127.0.0.1:5000 --parar MT-03 --apos 20`. O MT-03 para aos 20 s e fica perdido depois de uns 120 s sem sinal; em 3 minutos ele já está perdido quando o mapa abrir. Deixe o simulador rodando até o fim da fala.
4. Abas abertas, nesta ordem:
   - Slides, no slide 1.
   - **Operação Charlie**, logado como `organizador` (Operações, Operação Charlie). Planejada, 0 inscritos.
   - **Mapa da Bravo**, logado como `organizador` (Operações, Operação Bravo, Abrir mapa). Confira o MT-03 "Perdido" no topo da lista.
   - **Aba anônima**, logada como `observador`, na Operação Bravo.
5. **Terminal da demo** (Git Bash, na raiz do repositório, venv ativo, `MESHTRACKER_TOKEN` exportado), com os comandos já no histórico. No PowerShell o `curl` é outro comando; use o Git Bash.
6. Internet ligada, para os tiles do OpenStreetMap (sem ela o mapa fica cinza, e as setas continuam).
7. Zoom do navegador ajustado ao projetor (Ctrl e + até a lista e o formulário caberem na tela), e o mesmo zoom nas quatro abas. Teste com o projetor, não só com a tela do notebook.

**Comandos do terminal da demo:**

```bash
# teste do observador (bloco 4)
python -m pytest tests/test_funcional.py -q -k observador_recebe_403

# curl 1: sem token, devolve 401
curl -s -w "  -> HTTP %{http_code}\n" -X POST http://127.0.0.1:5000/api/v1/sinais -H "Content-Type: application/json" -d '{"dispositivo": "MT-01", "pacote": 99, "lat": -15.799, "lon": -47.907, "bateria": 80}'

# curl 2: com token, devolve 201 (repetido, devolve 200 duplicado)
curl -s -w "  -> HTTP %{http_code}\n" -X POST http://127.0.0.1:5000/api/v1/sinais -H "Authorization: Bearer $MESHTRACKER_TOKEN" -H "Content-Type: application/json" -d '{"dispositivo": "MT-01", "pacote": 99, "lat": -15.799, "lon": -47.907, "bateria": 80}'
```

Fonte dos comandos: `docs/guia-de-reproducao.md` (passo 11) e `docs/api.md`. Os mesmos comandos foram rodados em 08/11/2026 contra um app local com o seed: 401, 201 e 200.

**Cola de inscrição da Charlie** (todos diferentes dos times da Bravo; é o que mostra `02-inscricao-charlie.png`):

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
- Não clique em "Iniciar operação" na Charlie: só uma operação fica em curso por vez (R6).
- O curl com token grava uma posição no MT-01 e a seta dele pode dar um salto. Não é problema (`docs/guia-de-reproducao.md`, passo 11).
- O pacote 99 não colide com o simulador (ele começa pela hora atual). Se o 201 já foi rodado nesse banco no ensaio, a resposta será 200: refaça o seed.

## Plano B

**Se o ao vivo falhar:** use os prints de `docs/evidencias/` e a gravação de tela do ensaio. A gravação ainda precisa ser feita: gravar o roteiro inteiro (blocos 2 a 4) no ensaio, com o app já montado como acima, e guardar o arquivo fora do repositório, no desktop.

| Bloco | Prints que servem | Observação |
|---|---|---|
| 1 | nenhum (slide) | |
| 2 (H1) | `01-operadores.png`, `02-inscricao-charlie.png`, `03-recusa-duplicada.png`, `04-recusa-dispositivo.png`, `05-recusa-consentimento.png` | O `04` usa um 6º operador, o Jaguar, tentando o MT-01; ao vivo é o Lobo |
| 3 (H2) | `06-mapa-ativos.png`, `07-mapa-perdido.png` | O `06` mostra os 5 ativos e o contador de descartados (MT-99); o `07` mostra o MT-03 perdido, "2 min 8 s" |
| 4 (H3, H4) | `08-observador.png`, `curl-401-201.txt` | O arquivo de texto traz 401, 201, 200 e 202; o token aparece só como `$MESHTRACKER_TOKEN` |
| 5 e 6 | nenhum (slides) | Os números de testes estão em `docs/evidencias/funcional.md` (seções 1 e 6) |

**Falhas prováveis:**

| Sintoma | O que fazer |
|---|---|
| Mapa cinza, sem fundo | Siga em frente: as setas continuam. Diga que o fundo depende de internet (dúvida em aberto 1 do backlog) |
| MT-03 não está perdido no topo | O simulador foi ligado tarde. Mostre `07-mapa-perdido.png` e diga que o estado sai do tempo desde o último sinal |
| Simulador com 401 | Token diferente nos terminais. Mostre `06` e `07` e vá para a API (`docs/guia-de-reproducao.md`, Problemas comuns) |
| Charlie já tem inscritos | Crie uma operação nova em Operações (nome, data e local; nasce planejada) e use a cola nela. Ou use os prints `02` a `05` |
| App não sobe | Gravação de tela do ensaio, mais os prints |

## Perguntas prováveis

**Por que Flask e não MEVN?**
A stack MEVN tinha quatro serviços e um build de front-end, para um incremento de 9 dias feito por uma pessoa, e a demo precisava ser independente do operational-command. Com Flask e SQLite o projeto instala, testa e roda com três comandos, e a regra de negócio fica em `servicos.py`, testável sem servidor. O preço é não ter WebSocket: o mapa consulta a cada 3 segundos. *Fonte:* `docs/adr/ADR-002-stack-flask-sqlite.md`.

**Por que HTTP e não MQTT?**
Sem hardware nem gateway no MVP, o MQTT traria um broker, TLS e permissões por tópico sem mudar o que o organizador vê. HTTP com JSON é o menor contrato que leva o sinal até a regra e ao mapa, e qualquer cliente, como o `curl`, consegue testar. O preço é perder o QoS do MQTT, então a deduplicação virou a regra R8. O MQTT volta quando houver gateway real, por um novo ADR. *Fonte:* `docs/adr/ADR-003-gateway-por-http.md`.

**E o consentimento e a LGPD?**
Existe: a inscrição exige consentimento de rastreamento (R5), e ele vale por operação (ADR-001); sinal de quem não está inscrito nunca vira posição (R7), e só se registra a origem e o motivo; o observador só lê (R10). Falta: o prazo de guarda das posições depois da operação, que é dúvida em aberto. *Fonte:* `docs/backlog.md` (R5, R7, R10, Dúvida em aberto 2); `docs/adr/ADR-001-perfil-e-inscricao.md` (Contexto e Consequências).

**Como R2 e R3 são garantidas?**
Por restrições UNIQUE no SQLite, na tabela de inscrição: (operador, operação) para a R2 e (operação, dispositivo) para a R3. O banco recusa mesmo que o código falhe, e o serviço transforma a recusa em mensagem na própria página. Quanto à R6, só uma operação em curso por vez, é garantida por um índice único parcial. *Fonte:* `docs/adr/ADR-002-stack-flask-sqlite.md` (Decisão); `docs/backlog.md` (Modelo de dados, R6); `src/schema.sql`.

**Como se testa o tempo?**
O "agora" é um parâmetro, e nos testes um relógio injetado avança sem esperar. Os limites ficam testados em 59, 60, 61, 119, 120 e 121 segundos. Em uso normal, os limites são configuráveis por `MESHTRACKER_ATRASADO_S` (60) e `MESHTRACKER_PERDIDO_S` (120). *Fonte:* R9 em `docs/backlog.md`; `docs/evidencias/funcional.md` (seção 1); `docs/guia-de-reproducao.md` (Variáveis de ambiente).

**O que foi feito em segurança?**
Token de formulário contra CSRF, senha guardada em hash, token do gateway comparado com `hmac.compare_digest`, SQL só parametrizado, saída HTML escapada, `mapa.js` só com `textContent` e política CSP sem script inline; rodei bandit e pip-audit. Saíram cinco achados de severidade baixa, todos tratados: corpo sem limite (agora 64 KB, resposta 413); JSON aninhado demais dava 500 (agora 400); o tempo do login revelava usuário existente (agora confere um hash falso); o simulador seguia redirecionamento levando o token (agora não segue). O quinto, o token na linha de comando, foi aceito: o Guia recomenda a variável de ambiente. *Fonte:* `docs/evidencias/seguranca.md`; cabeçalho CSP em `docs/evidencias/curl-401-201.txt`; `docs/guia-de-reproducao.md` (passo 8).

**Por que os sinais são simulados?**
Porque o MVP não tem hardware nem gateway: foi o recorte dos ADR-002 e ADR-003. O simulador chama o mesmo endpoint que um gateway chamaria, então trocar a fonte não muda a regra, e essa é a hipótese 4. Não testei com dispositivo real. *Fonte:* `docs/adr/ADR-003-gateway-por-http.md`; H4 em `docs/hipoteses-e-incrementos.md`; `docs/api.md` (Fontes de sinal).

**Isto foi validado com um organizador?**
Não. Os roteiros foram executados por mim, no papel de organizador, e medem o fluxo, não a primeira impressão de um organizador real. A conversa com a federação é a pendência principal. *Fonte:* `docs/hipoteses-e-incrementos.md` ("Quem valida"); `docs/proposta.md` (Risco principal); `docs/backlog.md` (Dúvida em aberto 4).

**E se faltar internet em campo?**
As setas e a lista continuam, mas o fundo do mapa fica cinza, porque os tiles vêm do OpenStreetMap. Como ter os tiles offline é dúvida em aberto. *Fonte:* `docs/backlog.md` (Dúvida em aberto 1); `docs/guia-de-reproducao.md` (Pré-requisitos).

## Antes de apresentar, confirmar

- `docs/evidencias/seguranca.md` ainda não estava no ramo `demo/mvp-10-11` quando este roteiro foi escrito (está sendo integrado). Confirme que o arquivo chegou antes de citá-lo.
- O total de 407 testes e a contagem por regra mudam se os testes de segurança entrarem. Reconfira com `python -m pytest --collect-only -q` e atualize o bloco 5.
- Os tempos de H1 (554 ms) e H2 (94 ms) são de script. Se o ensaio com cronômetro for feito antes de terça, troque a fala "mede o sistema, não um organizador real" pelo tempo medido e aponte a gravação. Sem ele, mantenha como está.
- O 403 do observador ao vivo é pelo teste (`pytest -k`), porque a tela do observador não tem formulário. Se quiser mostrá-lo no navegador, prepare no ensaio um `fetch` no console com o token CSRF da própria página, como nas evidências; o nome do campo está nos templates, que não consultei.
- Tempo humano do bloco 2 (31 ações de inscrição e 3 recusas em 60 s) só se sabe no ensaio. Se estourar, vale a regra de corte da tabela "Se o tempo apertar".
- A gravação de tela do ensaio ainda será feita.
