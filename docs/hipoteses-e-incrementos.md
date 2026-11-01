# Hipóteses e incrementos

Estas são as Fichas 11 e 12 do Book (Kit da Aula 10). Preenchi as duas em 01/11/2026, depois do recorte do escopo (veja o [backlog](backlog.md)). As regras R1 a R11 citadas aqui estão definidas no backlog, e a troca de stack e de contrato do gateway está em [ADR-002: Flask e SQLite no lugar da stack MEVN](adr/ADR-002-stack-flask-sqlite.md) e em [ADR-003: Sinais do gateway por HTTP no lugar de MQTT](adr/ADR-003-gateway-por-http.md).

## Ficha 11: canvas de hipóteses

A prioridade é risco × incerteza, como no Kit: risco Alto vale 3, Médio vale 2 e Baixo vale 1, e a incerteza vai de 1 a 3. A H1 vai primeiro, mesmo empatando com a H2, porque é pré-requisito dela: sem inscrição não há o que rastrear.

| # | Acreditamos que… | Usuário | Saberemos quando… | Como testar | Risco | Incerteza (1–3) | Prioridade | Incremento |
|---|---|---|---|---|---|---|---|---|
| H1 | manter o perfil permanente do operador e inscrevê-lo por operação elimina o recadastro | Organizador | o organizador inscreve 5 operadores já cadastrados numa 2ª operação sem redigitar dados pessoais, em até 3 min | Roteiro cronometrado no Incremento 1, executado pelo autor no papel de organizador, com gravação de tela | Alto | 3 | 9 | 1 |
| H2 | ver cada operador no mapa com o estado (ativo, atrasado, perdido) faz o organizador perceber quem ficou sem contato | Organizador | no roteiro, quem está perdido e há quanto tempo é apontado em até 10 s depois de abrir o mapa | Roteiro cronometrado com 5 operadores simulados na Aula 15 (Ficha 18), executado pelo autor no papel de organizador | Alto | 3 | 9 | 2 |
| H3 | aceitar só sinais de inscritos com consentimento e restringir o observador à leitura protege a posição de quem não deveria ser rastreado | Organizador e operadores | nenhum sinal de não inscrito vira posição e nenhuma escrita do observador passa, nos testes | Testes automatizados | Médio | 2 | 4 | 2 |
| H4 | expor a situação e o recebimento de sinais em `/api/v1` permite trocar o simulador pelo gateway real sem mudar a regra | Organizador (e o futuro gateway) | o simulador e um cliente `curl` usam só a API, sem tocar no banco | Teste de API e reprodução pelo Guia | Baixo | 2 | 2 | 3 |

## Ficha 12: incrementos e go/no-go

| Incremento | Quando | Entrega | Hipóteses | Critério de aceitação | Go/no-go |
|---|---|---|---|---|---|
| 1 | Aula 14 · 10/11 | Cadastro do operador, operação com situação e inscrição por operação, persistidos | H1 | R1 a R6 testadas; dados persistem após reiniciar; roteiro do Incremento 1 demonstrado (cadastrar 5 operadores, inscrevê-los na operação 1 e depois na 2, e mostrar a recusa da inscrição duplicada, do dispositivo repetido e da inscrição sem consentimento) | Go se os testes estiverem verdes e o roteiro da H1 for cumprido em até 3 min, com a gravação como evidência |
| 2 | Aula 16 · 24/11 | Simulador, sinais filtrados e sem duplicata, estado do operador, mapa ao vivo e papel de observador | H2 · H3 | R7 a R10 testadas; roteiro do Incremento 2 demonstrado (5 inscritos simulados e um dispositivo não inscrito, marcadores que se movem sem recarregar, estados atrasado e perdido) | Go se, no roteiro, o operador perdido for apontado em até 10 s e nenhuma escrita indevida passar nos testes |
| 3 | Aula 18 · 08/12 | `/api/v1` documentada com token, Guia de reprodução e release v1.0 | H4 | Endpoints em `docs/api.md`; 401 sem token; tag `v1.0` | Go para o Demo Day se o MVP for reproduzido do zero, num clone limpo e num venv novo, seguindo só o Guia |

O Demo Day é em 15/12 (Aula 19). Nenhum go/no-go foi registrado até 01/11/2026.

## Quem valida

O próprio autor, no papel de organizador. Isso fica escrito assim nas Fichas 11, 12, 16 e 18, com a limitação declarada: quem construiu o sistema conhece as telas, então o teste mede o fluxo, não a primeira impressão de um organizador real. A validação com a federação continua como a pendência principal, e a Ficha 3 continua "não realizada". Se um colega ou organizador aparecer depois, ele entra como evidência adicional, sem mudar o critério.

## Definição de Pronto

Os 6 itens do Kit, sem alteração. O item 6 ("Outra pessoa consegue executar seguindo apenas o Book") é verificado com o clone limpo do Incremento 3, que eu mesmo faço; se mais ninguém tiver executado o Book, o go/no-go registra isso na observação do item 6 em vez de dar o item como atendido sem ressalva, e um colega, se houver, entra como evidência adicional. No planejamento, a coluna "Atende?" fica em branco e é preenchida em cada go/no-go.

| # | Item da Definição de Pronto | Atende? |
|---|---|---|
| 1 | Critérios de aceitação da história atendidos e demonstráveis | |
| 2 | Regra de negócio fora da rota (servicos.py) e coberta por teste pytest verde | |
| 3 | Dado persiste após reiniciar a aplicação | |
| 4 | Commit com mensagem legível e README atualizado | |
| 5 | Ficha correspondente do Book atualizada com a evidência (print, hash ou link) | |
| 6 | Outra pessoa consegue executar seguindo apenas o Book | |

## Âncoras × decisões

| Autor | Decisão do projeto |
|---|---|
| Pressman e Maxim | Cada incremento termina em go/no-go registrado na Ficha 16, com critério definido antes. |
| Sommerville | O recorte em 3 incrementos (2.3.2), a máquina de estados da operação e do operador (5.4.2) e as camadas rotas → serviços → repositório (6.3.1). |
| Cohn | O backlog em histórias com critérios de aceitação e iterações de duas semanas. |
| Gothelf e Seiden | As hipóteses H1 a H4 com sinal mensurável e a validação com o organizador antes de crescer o escopo. |

Li Sommerville (2018), nas seções 2.3.2 (p. 48), 5.4.2 (p. 137–138) e 6.3.1 (p. 156), e posso citá-lo como fundamento. Pressman, Cohn e Gothelf e Seiden não foram lidos: as linhas deles ligam autor e decisão, sem afirmar leitura.
