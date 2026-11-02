# Dinâmicas da Aula 7

O caderno completo, com as dez fichas, está em `Caderno_Aula7_MeshTracker_Central.pdf`. Aqui ficam o mapa do método, a matriz de decisão e o pitch.

A Feira das três ideias, a Entrevista cruzada e o semáforo do pitch dependem dos colegas em sala e não foram realizados. Por isso não há perguntas de colegas, entrevista nem feedback registrados. O pitch ganhou uma segunda versão, revisão minha após o recorte do escopo, e a primeira continua aqui como foi escrita na Aula 7.

## Mapa do método 3I + 3D

- **Investigar:** o contexto é o das operações de airsoft da federação, para quem eu desenvolvo o operational-command. Percebi que o operador teria de se cadastrar de novo a cada operação e que, pelo desenho do firmware, ninguém tem a visão geral de onde cada operador está. Não conversei com a federação: é o que enxergo olhando para o meu próprio projeto.
- **Interpretar:** organizadores de operações de airsoft da Federação do DF e entorno precisam inscrever operadores já conhecidos em cada nova operação e saber onde cada um está em campo, porque, sem perfil permanente e sem visão geral, acabam recadastrando os operadores e acompanhando a operação às cegas.
- **Idealizar:** uma aplicação web em que o organizador inscreve, em cada operação, operadores já cadastrados (com time e classe) e os acompanha ao vivo no mapa, para não recadastrar ninguém e ter uma visão geral mesmo sem internet.
- **Decidir:** comparei três ideias na matriz abaixo. O MeshTracker Central fez 15 pontos, o diário de obra digital 12 e o dimensionador solar 11.
- **Delimitar:** o recorte de 01/11/2026 divide o MVP em três incrementos: o 1 (até 10/11) fica com o cadastro permanente, a operação e a inscrição por operação; o 2 (até 24/11), com o simulador, os sinais só de inscritos, o estado do operador, o mapa ao vivo e o papel de observador; o 3 (até 08/12), com a API `/api/v1` documentada, com token, e o Guia de reprodução. Ficam de fora o MQTT, o gateway real, as ordens, os objetivos, a topologia da malha e a integração com o operational-command (ADR-002 e ADR-003).
- **Documentar:** README, backlog, proposta de uma página, os ADR-001, ADR-002 e ADR-003, as histórias de usuário (Ficha 13) e as hipóteses e incrementos (Fichas 11 e 12).

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

**Nota de revisão (01/11/2026):** As notas acima são as da Aula 7. Com o recorte, o escopo mínimo da Ideia 1 passaria a 2 e a viabilidade passa a se apoiar em Flask e SQLite em vez da stack do operational-command. A escolha não muda.

Escolhi o projeto **MeshTracker Central** porque atende ao usuário **organizador de operações de airsoft da Federação do DF e entorno**, resolve **o recadastro dos operadores a cada operação e a falta de visão geral em campo** e permite entregar inicialmente **a inscrição por operação e o acompanhamento ao vivo de operadores simulados no mapa**.

## Pitch, versão 1

Para organizadores de operações de airsoft da Federação do DF e entorno, que recadastram os mesmos operadores a cada operação e não sabem onde cada um está em campo, propomos a Central MeshTracker, um painel web com perfil permanente do operador, inscrição por operação (time e classe) e mapa ao vivo. Na primeira iteração, entregaremos o fluxo de inscrever um operador já cadastrado e vê-lo no mapa, mudando de estado conforme o tempo sem sinal. Saberemos que funciona quando o organizador reinscrever o mesmo operador em uma segunda operação sem cadastrá-lo de novo e identificar, sem explicação, quem está sem sinal e há quanto tempo.

## Pitch revisado

**Pitch, versão 2** (revisão própria após o recorte; o semáforo dos colegas não foi realizado): Para organizadores de operações de airsoft da Federação do DF e entorno, que recadastram os mesmos operadores a cada operação e não sabem onde cada um está em campo, propomos o MeshTracker Central, um painel web com perfil permanente do operador, inscrição por operação e mapa ao vivo. No primeiro incremento, entregaremos o cadastro único do operador e a inscrição dele em cada operação, com time, classe e dispositivo. Saberemos que funciona quando o organizador inscrever 5 operadores já cadastrados numa segunda operação em até 3 minutos, sem redigitar dados, e, no segundo incremento, apontar no mapa quem está perdido e há quanto tempo em até 10 segundos.
