# Dinâmicas da Aula 7

O caderno completo, com as dez fichas, está em `Caderno_Aula7_MeshTracker_Central.pdf`. Aqui ficam o mapa do método, a matriz de decisão e o pitch.

A Feira das três ideias, a Entrevista cruzada e o semáforo do pitch dependem dos colegas em sala e não foram realizados. Por isso não há perguntas de colegas, entrevista nem feedback registrados, e o pitch segue na versão 1.

## Mapa do método 3I + 3D

- **Investigar:** o contexto é o das operações de airsoft da federação, para quem eu desenvolvo o operational-command. Percebi que o operador teria de se cadastrar de novo a cada operação e que, pelo desenho do firmware, ninguém tem a visão geral de onde cada operador está. Não conversei com a federação: é o que enxergo olhando para o meu próprio projeto.
- **Interpretar:** organizadores de operações de airsoft da Federação do DF e entorno precisam inscrever operadores já conhecidos em cada nova operação e saber onde cada um está em campo, porque, sem perfil permanente e sem visão geral, acabam recadastrando os operadores e acompanhando a operação às cegas.
- **Idealizar:** uma aplicação web em que o organizador inscreve, em cada operação, operadores já cadastrados (com time e classe) e os acompanha ao vivo no mapa, para não recadastrar ninguém e ter uma visão geral mesmo sem internet.
- **Decidir:** comparei três ideias na matriz abaixo. O MeshTracker Central fez 15 pontos, o diário de obra digital 12 e o dimensionador solar 11.
- **Delimitar:** a primeira iteração fica com o cadastro permanente, a inscrição por operação e o rastreamento ao vivo com simulador. A topologia da malha fica de fora.
- **Documentar:** README, backlog, proposta de uma página e o ADR-001.

## Matriz de decisão

Escala: 2 atende claramente, 1 atende em parte, 0 ainda não atende. Fiz a pontuação sozinho, sem Feira nem entrevista; ela reflete só o meu julgamento. Ideia 1: MeshTracker Central. Ideia 2: dimensionador solar fotovoltaico. Ideia 3: diário de obra digital (RDO).

| Critério | Ideia 1 | Ideia 2 | Ideia 3 | Observação sobre a ideia 1 |
|---|---|---|---|---|
| Problema claro | 2 | 1 | 1 | Tenho usuário e consequência definidos, mas ainda sem confirmação da federação. |
| Usuário acessível | 2 | 1 | 1 | A federação é o público real do operational-command, embora eu ainda não tenha entrevistado ninguém. |
| Relevância | 2 | 1 | 2 | Sem uma central não há visão geral nem confirmação de ordens. |
| Viabilidade técnica | 2 | 1 | 2 | Já trabalho com a stack do operational-command, e a primeira iteração usa simulador, sem depender do firmware incompleto. |
| Escopo mínimo | 1 | 2 | 1 | O fluxo é um só, mas cresceu com a inscrição por operação; por isso tirei a trilha do essencial. |
| Testabilidade | 2 | 2 | 1 | A regra de duplicidade e os estados por tempo são fáceis de testar. |
| Aderência à disciplina | 2 | 1 | 2 | Tem contrato de API, modelo de dados, interface e regra de negócio. |
| Evolução em 3 iterações | 2 | 2 | 2 | Rastreamento, depois ordens, depois hardware real e autenticação das ordens. |
| **Total** | 15 | 11 | 12 |  |

Escolhi o projeto **MeshTracker Central** porque atende ao usuário **organizador de operações de airsoft da Federação do DF e entorno**, resolve **o recadastro dos operadores a cada operação e a falta de visão geral em campo** e permite entregar inicialmente **a inscrição por operação e o acompanhamento ao vivo de operadores simulados no mapa**.

## Pitch, versão 1

Para organizadores de operações de airsoft da Federação do DF e entorno, que recadastram os mesmos operadores a cada operação e não sabem onde cada um está em campo, propomos a Central MeshTracker, um painel web com perfil permanente do operador, inscrição por operação (time e classe) e mapa ao vivo. Na primeira iteração, entregaremos o fluxo de inscrever um operador já cadastrado e vê-lo no mapa, mudando de estado conforme o tempo sem sinal. Saberemos que funciona quando o organizador reinscrever o mesmo operador em uma segunda operação sem cadastrá-lo de novo e identificar, sem explicação, quem está sem sinal e há quanto tempo.
