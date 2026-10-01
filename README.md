# MeshTracker Central

Painel web para acompanhar ao vivo a posição e o estado de operadores em campo (atualizado a cada beacon, 30 s por padrão), alimentado por MQTT a partir da malha LoRa do MeshTracker. Projeto do Ciclo 2 de Desenvolvimento de Sistemas (Engenharia de Computação, CEUB, 2026/2).

## Problema

Pelo desenho do firmware MeshTracker (em desenvolvimento), cada nó só enxerga os vizinhos que alcança por até 2 minutos. O desenho não prevê visão consolidada, histórico nem ordens confirmadas para quem coordena a operação. O contexto é o de operações de airsoft no Distrito Federal e entorno, onde, sem perfil permanente, o operador teria de se cadastrar de novo a cada operação.

## Status

Fase de proposta (Aula 7). **Ainda não há código executável:** a Iteração 1 começa depois da aula.

## Integrantes

**[a preencher]**

## Escopo atual

**Iteração 1 (Essencial):**
- Contrato MQTT v1 e simulador de gateway.
- Cadastro permanente de operador e inscrição por operação (time, classe e dispositivo), sem recadastro.
- Ingest idempotente de nós inscritos, com estado do operador (ATIVO, ATRASADO, PERDIDO).
- Mapa ao vivo com marcador por time e estado.

**Depois:** ordens com ciclo de vida e ack, geofence de objetivos e trilha (Iteração 2); gateway real com HMAC e replay (Desejável). **Fora:** topologia da malha.

## Como executar

Não se aplica nesta fase. Quando a Iteração 1 existir, este campo terá os comandos para subir o ambiente.

## Estrutura

```
README.md
docs/
  proposta.md                        # proposta de uma página (Ficha 8)
  backlog.md                         # escopo E/I/D/F, fluxo e critérios de aceite
  dinamicas.md                       # mapa do método, cartões, matriz e pitch
  adr/ADR-001-perfil-e-inscricao.md  # modelo de dados (primeira decisão)
  adr/ADR-002-ponte-mqtt-backend.md  # ponte MQTT para o navegador
src/
tests/
```

## Projetos relacionados

- MeshTracker: firmware ESP32-S3 com GPS e mesh LoRa 433 MHz, do autor.
- operational-command: aplicação MEVN de operações, do autor, cuja stack serve de referência.
