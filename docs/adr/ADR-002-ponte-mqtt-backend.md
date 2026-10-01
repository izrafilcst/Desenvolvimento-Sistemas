# ADR-002: Backend como única ponte entre o MQTT e o navegador

- **Status:** proposto (decisão da Iteração 1, fora da entrega da Aula 7)
- **Data:** 2026-09-30

## Contexto

A Central recebe posições dos operadores por MQTT, publicadas por um gateway que escuta a malha LoRa. O firmware foi projetado para que cada nó emita um beacon a cada 30 s. O navegador do coordenador precisa ver esses dados ao vivo, e as regras (dedup por `(src_id, pkt_id)` e estado por tempo) precisam ser aplicadas e gravadas em um lugar só.

## Decisão

O navegador nunca fala com o broker. O backend assina `mt/v1/up/#`, aplica dedup e estado, grava no MongoDB e retransmite ao navegador por WebSocket. O contrato de tópicos e payloads é versionado (`mt/v1`).

## Alternativas consideradas

1. **Navegador ligado direto ao broker (MQTT sobre WebSocket).** Descartada inicialmente porque **[a fundamentar após a leitura]**. Argumentos candidatos, ainda não validados: expõe credenciais do broker ao cliente, duplica as regras no front-end e não grava o histórico.
2. **Backend expondo só REST, com o navegador consultando por polling (sem WebSocket).** Descartada inicialmente porque **[a fundamentar após a leitura]**. Argumento candidato: polling é mais simples, mas atrasa a atualização e multiplica requisições. Com beacons de 30 s talvez baste, então isso deve ser avaliado antes de decidir.

A escolha do MQTT como transporte entre o gateway e o backend é uma decisão à parte, candidata a ADR-003.

## Justificativa

Frase de ligação:

> Com base em **[autor e obra, após a leitura]**, decidimos **que o backend seja a única ponte entre o MQTT e o navegador** porque **[a fundamentar com o conceito lido]**. A alternativa **de ligar o navegador direto ao broker** foi inicialmente descartada porque **[a fundamentar]**.

A referência precisa estar ligada a esta decisão, não apenas listada no fim.

## Consequências esperadas

- **Positivas:** um único ponto de autenticação, regras e persistência. O front-end fica simples. O firmware fica desacoplado pelo contrato versionado.
- **Negativas:** o backend passa a ser ponto único de falha da visualização, há uma pequena latência extra e o contrato versionado exige manutenção.

## Referências consultadas

- FERREIRA, Arthur G. *Interface de programação de aplicações (API) e web services*. Curitiba: SRV, 2021. **[edição e capítulo a confirmar na biblioteca; conferir a autoria na capa, pois o slide 22 cita Ferreira e Rajabov e o slide 29 só Ferreira]** O livro trata de APIs e web services, então confirme que o conceito lido sustenta esta decisão.
- Alternativa de fundamentação, se o conceito de fronteiras entre camadas se ajustar melhor após a leitura: MARTIN, Robert C. *Arquitetura Limpa*. Rio de Janeiro: Alta Books, 2019 (indicado na aula para "Camadas e fronteiras").
