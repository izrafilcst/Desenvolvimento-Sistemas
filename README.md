# MeshTracker Central

Painel web para acompanhar ao vivo a posição e o estado dos operadores em operações de airsoft, a partir da rede LoRa do MeshTracker. É o meu projeto do Ciclo 2 de Desenvolvimento de Sistemas (Engenharia de Computação, CEUB, 2026/2).

**Aluno:** Rafael Alves de Sousa Costa · **RA:** 22304563

## Por que este projeto existe

Nas operações de airsoft da Federação do Distrito Federal e entorno, o organizador precisa inscrever os jogadores e acompanhar o que acontece em campo. Eu desenvolvo o operational-command, um sistema web para gerir operações, e o MeshTracker, um dispositivo com GPS e rádio LoRa que forma uma rede entre os jogadores sem depender de internet. Faltava ligar os dois.

Dois problemas me motivaram. O primeiro é que, sem um perfil permanente, o operador teria de se cadastrar de novo a cada operação, mesmo sendo a mesma pessoa. O segundo é que, pelo desenho do firmware, cada dispositivo só enxerga os vizinhos que alcança e esquece quem some por 2 minutos, então o organizador não tem uma visão geral. Ainda não conversei com a federação sobre isso: é o que percebo olhando para o meu próprio projeto.

## Em que ponto está

Fase de proposta (Aula 7). Ainda não há código executável: a primeira iteração começa depois da aula.

## O que entra na primeira iteração

- Contrato de mensagens MQTT e um simulador de gateway no lugar do hardware.
- Cadastro permanente do operador e inscrição em cada operação (time, classe e dispositivo), sem recadastro.
- Recebimento dos sinais só dos dispositivos inscritos, sem duplicatas, com o estado de cada operador (ativo, atrasado ou perdido).
- Mapa ao vivo com um marcador por operador, na cor do time.

Ficam para depois: ordens com confirmação, objetivos com alerta de chegada e trilha de posição (Iteração 2), gateway real com autenticação das ordens e replay da operação (Iteração 3, se houver tempo). Fica de fora, por enquanto, o desenho da topologia da malha.

## Como executar

Ainda não se aplica. Quando a primeira iteração existir, os comandos para subir o ambiente entram aqui.

## Estrutura

```
README.md
docs/
  Caderno_Aula7_MeshTracker_Central.pdf   caderno de dinâmicas preenchido
  proposta.md                             proposta de uma página
  backlog.md                              escopo, fluxo e critérios de aceite
  dinamicas.md                            método, matriz de decisão e pitch
  adr/ADR-001-perfil-e-inscricao.md       primeira decisão de arquitetura
src/
tests/
```

## Projetos relacionados

- **MeshTracker:** firmware para ESP32-S3 com GPS e rede mesh LoRa de 433 MHz.
- **operational-command:** aplicação web (MongoDB, Express, Vue e Node) para gerir operações; a stack dela serve de referência para este projeto.
