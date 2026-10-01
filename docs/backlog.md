# Escopo e backlog da primeira iteração

Esta é a Ficha 6 do caderno. Quando surgir uma funcionalidade nova, ela entra como Importante, Desejável ou Fora, sem mexer no que já é essencial.

## Modelo de dados inicial

O perfil do operador é permanente. O que muda a cada operação fica na inscrição.

| Entidade | O que guarda | Observação |
|---|---|---|
| Operador | apelido (único), nome e um identificador estável | Cadastrado uma só vez e mantido entre operações |
| Operação | nome, data, local e situação (planejada, em curso ou encerrada) |  |
| Inscrição | operador × operação, time, classe, dispositivo e consentimento de rastreamento | Time, classe e dispositivo valem só para aquela operação |
| Posição | inscrição, latitude, longitude, velocidade, bateria, qualidade do sinal e horário de chegada | Gravada só para inscrições de operação em curso |

As regras que vou testar:

1. Inscrever um operador já cadastrado em uma nova operação não exige novo cadastro.
2. Um operador tem no máximo uma inscrição por operação.
3. Um dispositivo pertence a no máximo uma inscrição por operação.
4. Mudar time ou classe altera só a inscrição, nunca o perfil.
5. A inscrição exige o consentimento de rastreamento.
6. Sinal de dispositivo sem inscrição em operação em curso é descartado e contado, nunca gravado.
7. O mesmo sinal (mesma origem e mesmo número de pacote) vale uma vez só, e o operador é classificado como ativo, atrasado ou perdido pelo tempo sem sinal.

## Funcionalidades

| Funcionalidade | Classe | Justificativa |
|---|---|---|
| Contrato MQTT + simulador de gateway | E | Sem ele nenhum dado atravessa o sistema, e eu não dependo do firmware pronto. |
| Cadastro permanente do operador e inscrição por operação (time, classe e dispositivo) | E | É a ação real do organizador e evita o recadastro a cada operação. |
| Recebimento só de dispositivos inscritos, sem duplicatas, com estado do operador | E | É a regra de negócio central e protege a privacidade de quem não está inscrito. |
| Mapa ao vivo com marcador por time e estado | E | É o que o organizador vê. |
| Ordens com ciclo de vida e confirmação | I | É o diferencial da central, mas não é o núcleo da primeira iteração. |
| Objetivos com alerta de chegada, alertas e trilha | I | Agrega valor, mas pode esperar. |
| Gateway real no ESP32-S3, com autenticação das ordens | D | Depende de o firmware estar pronto, e hoje ele não está. |
| Topologia da malha | F | Exige mudar o protocolo do pacote do firmware. |

E é essencial, I é importante, D é desejável e F fica fora. Também anotei como desejáveis o replay da operação e a importação de operações e objetivos do operational-command.

## Fluxo completo da primeira iteração

Usuário → interface → regra de negócio → persistência → resposta.

| Etapa | Como fica |
|---|---|
| Ação do usuário | O organizador inscreve um operador já cadastrado em uma operação, escolhendo time, classe e dispositivo, e acompanha o mapa enquanto um simulador de gateway envia os sinais. |
| Tela ou rota | Duas telas: “Inscrição na operação” e “Mapa ao vivo”, que recebe as atualizações por WebSocket. O estado inicial vem de GET /api/operators. |
| Regra principal | O operador se cadastra uma vez só. Cada operador tem uma única inscrição por operação, cada dispositivo pertence a uma única inscrição por operação e a inscrição exige o consentimento de rastreamento. O sistema só aceita sinais de dispositivos inscritos em operação em curso, ignora sinais repetidos e classifica o operador como ativo, atrasado ou perdido pelo tempo sem sinal. |
| Dado gravado ou consultado | Operadores, operações, inscrições e posições, no MongoDB. |
| Resposta apresentada | O marcador aparece no mapa na cor do time, com o estado do operador, e se move a cada sinal. Um painel ao lado lista os operadores da operação. |
| Critério de demonstração | Com o ambiente no ar e o simulador rodando, vou cadastrar 5 operadores uma única vez, inscrevê-los na operação 1 e depois na operação 2 sem novo cadastro, e mostrar no mapa os inscritos da operação em curso enquanto um dispositivo não inscrito é descartado. Depois paro um operador e mostro o estado passar para atrasado aos 60 segundos e para perdido aos 120 segundos. Por fim, mostro que o mesmo sinal recebido por dois gateways gera uma única posição e que os testes automatizados passam. |

## Critérios de aceite

| Item | Iteração | Critério |
|---|---|---|
| B1 Contrato MQTT e simulador | 1 | Existe um documento com os tópicos, a qualidade de serviço e o formato das mensagens. O simulador publica 5 operadores e uma mensagem fora do formato é rejeitada. |
| B2 Cadastro e inscrição | 1 | O operador é cadastrado uma vez (apelido único) e inscrito nas operações 1 e 2 sem novo cadastro, com times e classes diferentes. Uma segunda inscrição na mesma operação é recusada, assim como o mesmo dispositivo em duas inscrições da mesma operação e a inscrição sem consentimento. Mudar time ou classe não altera o perfil. Tudo coberto por testes automatizados. |
| B3 Recebimento e estado | 1 | O mesmo sinal gera um único registro. Sinal de dispositivo sem inscrição em operação em curso é descartado e contado. O operador fica atrasado após 60 s e perdido após 120 s sem sinal (valores iniciais, ajustáveis). Coberto por testes. |
| B4 Mapa ao vivo | 1 | Com 5 operadores simulados inscritos, os marcadores se atualizam sem recarregar a página, a cor indica o time e o estado aparece no marcador e na lista lateral. |
| B5 Ordens | 2 | Uma ordem passa por criada, enfileirada, transmitida, entregue e cumprida ou recusada, ou expira ao fim do prazo. Transições inválidas são recusadas. Coberto por testes. |
| B6 Objetivos, alertas e trilha | 2 | O objetivo é marcado como atingido quando o operador fica a até 25 m por 10 s. Há alertas de operador perdido e de bateria abaixo de 20% (valores iniciais, ajustáveis), e a trilha mostra os últimos 10 pontos. |
| B7 Gateway real e autenticação | 3, se o firmware estiver pronto | O gateway publica sinais reais no mesmo contrato. Ordens sem autenticação válida são descartadas. |
| B8 Topologia da malha | fora | Registrada e descartada por ora. |

## Dúvidas em aberto

1. Qual biblioteca de mapas usar (Leaflet ou MapLibre) e como ter o mapa offline em campo, sem internet.
2. Como proteger o broker MQTT, com TLS e permissões por usuário, principalmente no tópico de ordens.
3. Posição de pessoa é dado pessoal (LGPD): além do consentimento na inscrição, preciso definir por quanto tempo guardar as trilhas depois da operação.
4. O cadastro de operadores fica só neste sistema ou será compartilhado com o operational-command, como fonte única?
5. A federação tem um número de registro que identifique cada operador? Times e classes são uma lista fixa da federação ou livres a cada operação?
6. Em jogo competitivo, o sinal aberto do dispositivo mostra a posição dos adversários aos jogadores. Seria preciso filtrar por time ou criptografar no firmware e deixar a visão completa só para o organizador. Isso fica fora desta entrega.
7. Tempo no ar do sinal: pelo layout do README do firmware (cerca de 53 bytes), calculei por volta de 330 ms por sinal, ou 1,1% do tempo a cada 30 s. Preciso conferir no teste de tempo no ar do firmware.
