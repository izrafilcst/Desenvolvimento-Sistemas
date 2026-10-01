# Proposta de projeto em uma página

> Rascunho da Ficha 8. Campos **[a preencher]** dependem de pessoas ou do repositório publicado. Suposições **[a validar]**.

| Campo | Conteúdo |
|---|---|
| **Nome provisório** | MeshTracker Central |
| **Aluno ou integrantes** | **[a preencher]** |
| **Usuário principal** | Organizador(a) de operações da Federação de Airsoft do Distrito Federal e entorno (árbitro ou staff). Pessoa a consultar: **[a preencher]**. |
| **Problema observado** | **[a validar]** Pelo desenho do firmware MeshTracker (em desenvolvimento), cada nó só enxerga os vizinhos que alcança e a tabela de nós guarda no máximo 20 nós, descartando os que somem por 2 minutos. O desenho não prevê visão consolidada, histórico nem ordens confirmadas. É inferência do projeto, ainda não observação de campo. O autor também identificou que, sem perfil permanente, o operador teria de se recadastrar a cada operação. |
| **Como o problema é enfrentado atualmente** | Hipótese: cadastro refeito a cada operação e acompanhamento por rádio de voz. **[a validar com a federação]** |
| **Consequência do problema** | A perda de um operador pode passar despercebida, ordens ficam sem confirmação, as decisões são tomadas sem dados e o organizador perde tempo recadastrando operadores. |
| **Proposta de solução** | Uma aplicação web que permita ao organizador manter o perfil permanente de cada operador, inscrevê-lo em cada operação com time e classe e vê-lo no mapa, ao vivo, e, depois, emitir ordens com confirmação, de forma que não recadastre ninguém e tenha visão geral da operação sem depender de internet. Os dados vêm da malha LoRa do MeshTracker, via gateway e MQTT, e a atualização segue o ritmo do beacon (30 s por padrão). |
| **Escopo mínimo** | Contrato MQTT v1 com simulador de gateway, cadastro permanente de operador e inscrição por operação, ingest idempotente de nós inscritos com estado do operador e mapa ao vivo. |
| **Fluxo da Iteração 1** | O organizador inscreve um operador já cadastrado em uma operação (time, classe, dispositivo) → o simulador publica beacons dos inscritos → MQTT → o backend ignora nós não inscritos, aplica dedup e estado → grava no MongoDB → o mapa atualiza o marcador, com a cor do time e o estado, por WebSocket. |
| **Funcionalidades fora do escopo inicial** | Ordens com ciclo de vida e ack, geofence de objetivos e trilha (Iteração 2). Gateway real com HMAC e replay (Desejável). Topologia da malha (Fora). |
| **Tecnologias inicialmente consideradas** | Vue 3 + Vite, Node.js + Express, MongoDB, Mosquitto (MQTT), WebSocket e Docker Compose, a mesma stack do operational-command. Mapa com Leaflet ou MapLibre (a decidir). O firmware existente (ESP32-S3, ESP-IDF, LoRa SX1278) só entra a partir da Iteração 3. |
| **Risco principal** | O firmware do MeshTracker ainda tem GPS, mesh e UI em stubs. Mitigação: contrato MQTT primeiro e simulador de gateway, de modo que a Iteração 1 não dependa do hardware. |
| **Como a solução será validada** | Testes automatizados do dedup e das transições de estado. Demonstração com 5 operadores simulados ao vivo. Medida proposta: o organizador reinscreve o mesmo operador em uma segunda operação sem recadastro e identifica, sem explicação, qual operador está sem sinal e há quanto tempo. Confirmação com usuário real **[a preencher em sala]**. |
| **Referência bibliográfica inicial** | CEUBOOK. *Engenharia da Computação — Desenvolvimento de Sistemas*. Brasília: CEUB, 2024. **[capítulo a confirmar; ver ADR-001]** |
| **Link do repositório** | **[a preencher após o push]** |
