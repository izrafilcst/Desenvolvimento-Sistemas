# Escopo mínimo e backlog da Iteração 1

> Rascunho da Ficha 6. Regra da aula: funcionalidade nova que surgir vai para Importante, Desejável ou Fora.

## Modelo de dados inicial

O perfil do operador é permanente. O que muda a cada operação fica na inscrição.

| Entidade | Conteúdo | Observação |
|---|---|---|
| Operador | apelido (único), nome, identificador estável **[a validar com a federação]** | Cadastrado uma única vez e mantido entre operações |
| Operação | nome, data, local, situação (planejada, em curso, encerrada) | |
| Inscrição | operador × operação, time, classe, dispositivo (`node_id`), consentimento de rastreamento | Time, classe e dispositivo valem só para aquela operação |
| Posição | inscrição, lat, lon, velocidade, bateria, rssi, snr, hop, pkt_id, recebido_em | Gravada só para inscrições de operação em curso |

Regras de negócio:

1. **Reinscrição sem recadastro:** inscrever um operador já cadastrado em uma nova operação usa o perfil existente.
2. Um operador só pode ter uma inscrição por operação.
3. Um dispositivo só pode estar em uma inscrição por operação.
4. Alterar time ou classe muda só a inscrição, nunca o perfil.
5. A inscrição exige consentimento de rastreamento.
6. Beacon de nó sem inscrição em operação em curso é descartado e contado, nunca gravado.
7. Dedup por `(src_id, pkt_id)` e estado ATIVO, ATRASADO ou PERDIDO pelo tempo desde o último beacon.

## Ficha 6 · Funcionalidades

| # | Funcionalidade | Classe | Justificativa |
|---|---|---|---|
| B1 | Contrato MQTT v1 + simulador de gateway | E | Sem ele não há dado atravessando o sistema nem independência do firmware |
| B2 | Cadastro permanente de operador e inscrição por operação (time, classe, dispositivo) | E | É a ação real do organizador e evita o recadastro a cada operação |
| B3 | Ingest idempotente só de nós inscritos + estado do operador | E | É a regra de negócio central e protege a privacidade |
| B4 | Mapa ao vivo com marcador por time e estado | E | É a resposta visível ao organizador |
| B5 | Ordens com ciclo de vida e ack | I | Diferencial da central, mas não é o núcleo da Iteração 1 |
| B6 | Geofence de objetivos, alertas e trilha | I | Agrega valor real, mas pode esperar |
| B7 | Gateway real ESP32-S3 + HMAC nas ordens | D | Depende da mesh do firmware, hoje em stubs |
| B8 | Topologia da malha | F | Exige mudar o protocolo do pacote (relayer no cabeçalho) |

Registrados como Desejável, fora da tabela: replay da operação e importação de operações e objetivos do operational-command.

## Fluxo completo da Iteração 1

Usuário → Interface → Regra de negócio → Persistência → Resposta

- **Ação do usuário:** o organizador inscreve um operador já cadastrado em uma operação, com time, classe e dispositivo, e acompanha o mapa enquanto um simulador de gateway publica beacons.
- **Tela ou rota:** telas "Inscrição na operação" e "Mapa ao vivo" (WebSocket), com `GET /api/operators` para o estado inicial.
- **Regra principal:** inscrição sem recadastro, com as unicidades e o consentimento das regras 1 a 5. O ingest aceita só nós inscritos em operação em curso, com dedup e estado pelo tempo sem sinal.
- **Dado gravado ou consultado:** operadores, operações, inscrições e posições, em MongoDB.
- **Resposta apresentada:** o marcador aparece com a cor do time e o estado, e se move conforme os beacons. Um painel lista os operadores da operação.
- **Critério de demonstração:** com `docker compose up` e o simulador rodando:
  1. cadastrar 5 operadores uma única vez;
  2. inscrevê-los na operação 1 e depois na operação 2, sem novo cadastro e com times e classes diferentes;
  3. com a operação 1 em curso, os inscritos aparecem no mapa e um nó não inscrito é descartado;
  4. parar um operador o leva a ATRASADO aos 60 s e a PERDIDO aos 120 s;
  5. o mesmo beacon vindo de 2 gateways simulados gera 1 posição;
  6. os testes automatizados passam.

## Backlog com critérios de aceite

| # | Item | Iteração | Critério de aceite |
|---|---|---|---|
| B1 | Contrato MQTT v1 + simulador | 1 | Documento com tópicos, QoS e payloads. O simulador publica 5 operadores em `mt/v1/up/{node}/beacon`. Mensagem fora do formato é rejeitada. |
| B2 | Cadastro e inscrição | 1 | O operador é cadastrado uma vez (apelido único) e inscrito nas operações 1 e 2 sem novo cadastro, com times e classes diferentes. Segunda inscrição na mesma operação é rejeitada. O mesmo dispositivo em duas inscrições da mesma operação é rejeitado. Inscrição sem consentimento é rejeitada. Editar time ou classe não altera o perfil. Coberto por testes automatizados. |
| B3 | Ingest idempotente + estado | 1 | Mesmo `(src_id, pkt_id)` gera um registro só. Beacon de nó sem inscrição em operação em curso é descartado e contado. ATRASADO após 60 s e PERDIDO após 120 s sem beacon (valores iniciais, configuráveis). Coberto por testes automatizados. |
| B4 | Mapa ao vivo | 1 | Com 5 operadores simulados inscritos, os marcadores atualizam sem recarregar a página. A cor do marcador indica o time, e o estado aparece no marcador e no painel lateral. |
| B5 | Ordens com ciclo de vida | 2 | Uma ordem percorre criada, enfileirada, transmitida, entregue e cumprida ou recusada, ou expira no fim do TTL. Transição inválida é rejeitada. Coberto por testes. |
| B6 | Geofence, alertas e trilha | 2 | Objetivo marcado como atingido quando a distância (Haversine) ≤ 25 m por 10 s. Alertas de operador perdido e de bateria abaixo de 20% (valores iniciais, configuráveis). A trilha mostra os últimos 10 pontos. |
| B7 | Gateway real + HMAC | 3 (se a mesh estiver pronta) | O gateway publica beacons reais no contrato v1. Ordens sem HMAC válido são descartadas. |
| B8 | Topologia da malha | Fora | Registrada e descartada agora. |

## Dúvidas registradas (a investigar)

1. Mapa: Leaflet ou MapLibre, e como ter tiles offline para o campo sem internet.
2. Broker: TLS e ACL por usuário, em especial para o tópico de ordens.
3. Posição de pessoas é dado pessoal (LGPD). Além do consentimento na inscrição, definir por quanto tempo as trilhas são guardadas depois da operação.
4. Tempo no ar do beacon: pelo layout do README (cerca de 53 B) calculei ≈330 ms no ar, com preâmbulo, ou ≈1,1% a cada 30 s. Conferir em `test_native_airtime` no repositório do firmware.
5. Cadastro de operador: independente desta aplicação na Iteração 1 ou compartilhado com o operational-command (fonte única)? Decidir depois; candidato a ADR.
6. Identificador estável do operador: a federação tem número de registro? **[a validar com a federação]** Sem ele, o apelido precisa ser único.
7. Times e classes: lista fixa definida pela federação ou livre por operação? **[a validar com a federação]**
8. Jogo competitivo: pelo desenho do firmware, o beacon aberto mostra a posição de todos os nós aos dispositivos dos jogadores, inclusive adversários. Filtro por time ou criptografia no firmware, e visão completa só para o organizador, ficam fora desta entrega.

## Pendências do fechamento

**[a preencher em sala]**
