# Escopo e backlog da primeira iteração

Esta é a Ficha 6 do caderno. Quando surgir uma funcionalidade nova, ela entra como Importante, Desejável ou Fora, sem mexer no que já é essencial.

Revisei este backlog em 01/11/2026, depois de recortar o escopo para caber nos três incrementos. A troca de stack e a troca do contrato do gateway estão registradas em [ADR-002: Flask e SQLite no lugar da stack MEVN](adr/ADR-002-stack-flask-sqlite.md) e em [ADR-003: Sinais do gateway por HTTP no lugar de MQTT](adr/ADR-003-gateway-por-http.md).

## Modelo de dados

O perfil do operador é permanente. O que muda a cada operação fica na inscrição.

| Tabela | Campos | Restrições |
|---|---|---|
| `operador` | id, apelido, nome, criado_em | `apelido` único |
| `operacao` | id, nome, data, local, situacao, centro_lat, centro_lon | `situacao` ∈ {planejada, em_curso, encerrada} |
| `inscricao` | id, operador_id, operacao_id, time, classe, dispositivo, consentimento | único (operador_id, operacao_id); único (operacao_id, dispositivo); consentimento obrigatório |
| `posicao` (Inc 2) | id, inscricao_id, pacote, lat, lon, bateria, recebido_em | único (inscricao_id, pacote) |
| `descarte` (Inc 2) | id, dispositivo, motivo, recebido_em | Registra só a origem e o motivo, sem a posição |
| `usuario` (Inc 2) | id, login, senha_hash, papel | `papel` ∈ {organizador, observador} |

Times e classes vêm de listas fixas no código:

- **Times:** Azul, Vermelho, Verde e Amarelo, cada um com uma cor.
- **Classes:** Fuzileiro, Suporte, Atirador designado e Médico.

Se a federação tiver listas próprias (dúvida 3, no fim deste documento), trocar as listas não mexe no modelo.

## Regras

As regras que vou testar, numeradas de R1 a R11. A coluna Inc diz em qual incremento cada uma entra.

| # | Regra | Inc |
|---|---|---|
| R1 | Inscrever um operador já cadastrado em uma nova operação não exige novo cadastro. | 1 |
| R2 | Um operador tem no máximo uma inscrição por operação. | 1 |
| R3 | Um dispositivo pertence a no máximo uma inscrição por operação. | 1 |
| R4 | Mudar time ou classe altera só a inscrição, nunca o perfil. | 1 |
| R5 | A inscrição exige consentimento de rastreamento. | 1 |
| R6 | A operação só avança planejada → em curso → encerrada. Só pode haver uma operação em curso por vez, e não há inscrição em operação encerrada. | 1 |
| R7 | Sinal de dispositivo sem inscrição na operação em curso é descartado e contado, nunca gravado como posição. | 2 |
| R8 | O mesmo sinal (mesmo dispositivo e mesmo número de pacote na operação) vale uma vez só. | 2 |
| R9 | O estado do operador sai do tempo desde o último sinal: sem sinal (nunca recebeu), ativo (até 60 s), atrasado (de 60 a 120 s) ou perdido (acima de 120 s). Os limites são configuráveis por variável de ambiente, e o "agora" é injetável nos testes. | 2 |
| R10 | O observador só lê. Qualquer escrita feita por ele recebe 403. | 2 |
| R11 | `POST /api/v1/sinais` exige o token do gateway. | 3 |

R1 a R5 vêm do [ADR-001](adr/ADR-001-perfil-e-inscricao.md) e do backlog da Aula 7. A R6 é nova: simplifica o roteamento do sinal ("uma operação por vez") e é a máquina de estados da operação. A antiga regra 7 da Aula 7 (dois gateways) virou a R8, que tem o mesmo efeito e um caso de uso só.

## Funcionalidades

E é essencial, I é importante (com o incremento em que entra), D é desejável e F fica fora.

| Funcionalidade | Classe | Justificativa |
|---|---|---|
| Cadastro permanente do operador | E | Sem ele o recadastro continua; é a base de tudo. |
| Operação com situação e inscrição por operação (time, classe, dispositivo e consentimento) | E | É a ação real do organizador e fecha o fluxo do Incremento 1. |
| Simulador e recebimento de sinais só de inscritos, sem duplicata | I (Inc 2) | É a regra central do rastreamento, mas depende da inscrição pronta. |
| Estado do operador e mapa ao vivo com lista lateral | I (Inc 2) | É o que o organizador vê; vem logo depois do recebimento. |
| Papel de observador, só leitura | I (Inc 2) | Protege a operação de escritas indevidas. |
| API `/api/v1` documentada, com token do gateway | I (Inc 3) | Deixa o simulador trocável pelo gateway real sem mudar a regra. |
| Trilha dos últimos 10 pontos e exportação CSV | D | Só se sobrar tempo no Incremento 3. |
| MQTT, gateway real, ordens, objetivos, topologia da malha e integração com o operational-command | F | Fora do MVP: exigem hardware, infraestrutura ou outro sistema (ADR-002 e ADR-003). |

## Fluxo completo da Iteração 1

Usuário → interface → regra de negócio → persistência → resposta.

| Etapa | Como fica |
|---|---|
| Ação do usuário | O organizador inscreve um operador já cadastrado numa operação, escolhendo time, classe e dispositivo e marcando o consentimento. |
| Tela ou rota | `/operacoes/<id>`, com formulário de inscrição que envia para `POST /operacoes/<id>/inscricoes`. |
| Regra principal | R1 a R6. |
| Dado gravado ou consultado | `operador`, `operacao` e `inscricao`, no SQLite. |
| Resposta apresentada | O inscrito aparece na lista da operação com time e classe; se uma regra for violada, a mensagem aparece na mesma página. |
| Critério de demonstração | Cadastrar 5 operadores, inscrevê-los na operação 1 e depois na operação 2, sem novo cadastro e com times diferentes; mostrar a recusa da inscrição duplicada, do dispositivo repetido e da inscrição sem consentimento; reiniciar o app e mostrar que os dados continuam lá. |

## Critérios de aceite por incremento

Cada incremento termina com um go/no-go (Ficha 12). Até 01/11/2026 nenhum incremento foi entregue: os critérios abaixo são o plano, não um resultado.

| Incremento | Critério de aceite |
|---|---|
| 1 (até 10/11) | As regras R1 a R6 têm testes. Os dados continuam lá depois de reiniciar o app. O roteiro de demonstração é: cadastrar 5 operadores; inscrever os 5 na operação 1 e depois na operação 2, sem novo cadastro e com times diferentes; mostrar que uma inscrição duplicada, um dispositivo repetido e uma inscrição sem consentimento são recusados. Os erros de regra aparecem como mensagem na própria página, sem erro 500. Telas: `/operadores` (lista e formulário de cadastro), `/operacoes` (lista e formulário de criação) e `/operacoes/<id>` (situação, botões de transição válidos, lista de inscritos e formulário de inscrição). |
| 2 (até 24/11) | As regras R7 a R10 têm testes. Com 5 inscritos simulados e o dispositivo MT-99, que não foi inscrito: os marcadores se movem sem recarregar a página; o MT-99 aparece só no contador de descartados; o MT-03, que o simulador para de propósito, passa para atrasado aos 60 s e para perdido aos 120 s; os pacotes duplicados não geram posição repetida. O observador vê listas e mapa, mas não vê formulários, e qualquer escrita dele recebe 403. |
| 3 (até 08/12) | Todos os endpoints de `/api/v1` estão documentados em `docs/api.md`, com payload, códigos de resposta e exemplos em `curl`. Um cliente externo (`curl`) consome a situação e envia sinais só pela API. Sem token, a resposta é 401 (R11). O MVP é reproduzido do zero, num clone limpo e num venv novo, seguindo só o Guia de reprodução; um colega, se houver, entra como evidência adicional. |

## Dúvidas em aberto

1. Como ter os tiles do mapa offline em campo, sem internet. O Leaflet fica dentro do projeto e os marcadores aparecem mesmo sem os tiles, mas o fundo do mapa depende de internet.
2. Por quanto tempo guardar as posições. Posição de pessoa é dado pessoal (LGPD): além do consentimento na inscrição, preciso definir por quanto tempo guardar o que for gravado depois da operação.
3. Se a federação tem um identificador próprio para cada operador e se times e classes são uma lista fixa dela ou livres a cada operação.
4. Quando e como conversar com a federação para validar a H1 e a H2, que por enquanto só eu posso validar, no papel de organizador.
