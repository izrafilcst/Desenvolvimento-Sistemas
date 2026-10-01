# Dinâmicas da Aula 7 — rascunho

> Rascunho preparado antes da aula. Campos **[a preencher em sala]** dependem dos colegas ou de pessoas reais e não foram inventados. Suposições **[a validar]** ainda precisam de confirmação.

## Mapa do método 3I + 3D (anotado)

| Movimento | Aplicação ao MeshTracker Central |
|---|---|
| 1. Investigar | Contexto: operações de airsoft da Federação do Distrito Federal e entorno, cliente do operational-command. O autor identificou que, sem perfil permanente, o operador teria de se cadastrar de novo a cada operação, e que time e classe são atributos a tratar por operação. Pelo desenho do firmware (README do MeshTracker, ainda em desenvolvimento), cada nó exibirá só o mapa dos vizinhos que alcança, e a tabela de nós guarda no máximo 20 nós e descarta os que somem por 2 minutos, sem visão consolidada para o organizador. **[a validar com a federação: é inferência do projeto, não observação de campo]** |
| 2. Interpretar | Ver o enunciado v0 abaixo. |
| 3. Idealizar | Uma aplicação web que permita ao organizador inscrever, em cada operação, operadores já cadastrados (com time e classe) e acompanhá-los ao vivo no mapa e, depois, emitir ordens com confirmação, de forma que tenha visão geral sem recadastrar ninguém e sem depender de internet. Verificação: testes automatizados das regras e demonstração com 5 operadores simulados em 2 operações. |
| 4. Decidir | Matriz da Ficha 4 (abaixo): Central 15, Diário de obra 12, Solar 11. |
| 5. Delimitar | Iteração 1: cadastro permanente e inscrição por operação, e rastreamento ao vivo com simulador de gateway. Fora agora: topologia da malha. Detalhes em `backlog.md`. |
| 6. Documentar | `README.md`, `docs/backlog.md`, `docs/adr/ADR-001-perfil-e-inscricao.md` e `docs/proposta.md`. A decisão da ponte MQTT ficou no ADR-002. |

## Ficha 2 · Cartões das três ideias

### Ideia 1

- **Título provisório:** MeshTracker Central
- **Usuário identificável:** organizador(a) de operações da Federação de Airsoft do Distrito Federal e entorno (árbitro ou staff que coordena a operação). **[a preencher: nome ou papel de uma pessoa da federação para consultar]**
- **Problema observado:** **[a validar]** pelo desenho do firmware, cada nó só enxerga os vizinhos que alcança, por até 2 minutos, e nada consolida a posição e o estado de todos os operadores. É inferência do projeto, ainda não observação de campo. O autor também identificou que, sem perfil permanente, o operador teria de se recadastrar a cada operação.
- **Consequência:** a perda de um operador pode passar despercebida, ordens ficam sem confirmação, as decisões são tomadas sem dados e o organizador perde tempo recadastrando operadores a cada operação.
- **Como é resolvido hoje:** **[a validar com a federação]** como inscrição e acompanhamento são feitos hoje (hipótese: fichas ou planilhas e rádio de voz).
- **Solução imaginada:** um painel web ao vivo, alimentado por MQTT a partir da malha LoRa, com cadastro permanente de operadores, inscrição por operação (time e classe) e, depois, ordens.
- **Evidência ou pessoa a consultar:** **[a preencher em sala]**
- **Perguntas recebidas dos colegas:** 1. **[Sala]** 2. **[Sala]**

### Ideia 2

- **Título provisório:** Dimensionador solar fotovoltaico
- **Usuário identificável:** estudante de engenharia ou instalador que dimensiona sistemas fotovoltaicos residenciais. Hipótese.
- **Problema observado:** dimensionar módulos e inversor a partir de consumo e irradiação exige cálculos manuais e planilhas sujeitas a erro. **[a validar]**
- **Consequência:** sistema sub ou superdimensionado e retrabalho.
- **Como é resolvido hoje:** planilhas e calculadoras de fabricantes. **[a validar]**
- **Solução imaginada:** uma aplicação web que calcula kWp, módulos e inversor a partir do consumo e da irradiação local e salva o projeto.
- **Evidência ou pessoa a consultar:** **[a preencher em sala]**
- **Perguntas recebidas dos colegas:** 1. **[Sala]** 2. **[Sala]**

### Ideia 3

- **Título provisório:** Diário de obra digital (RDO)
- **Usuário identificável:** engenheiro(a) residente ou mestre de obras. Hipótese.
- **Problema observado:** o registro diário em papel ou planilha é esquecido, alterado depois e difícil de auditar. **[a validar]**
- **Consequência:** disputas e falta de rastro de auditoria.
- **Como é resolvido hoje:** papel, planilhas e mensagens. **[a validar]**
- **Solução imaginada:** uma aplicação web de registro diário que trava após a assinatura e guarda o histórico.
- **Evidência ou pessoa a consultar:** **[a preencher em sala]**
- **Perguntas recebidas dos colegas:** 1. **[Sala]** 2. **[Sala]**

## Ficha 3 · Síntese pós-entrevista

- **Enunciado v0 (para revisar na Entrevista cruzada):** Organizadores de operações de airsoft da Federação do DF e entorno precisam inscrever operadores já conhecidos em cada nova operação e saber onde cada um está em campo porque hoje, sem perfil permanente e sem visão consolidada, recadastram os operadores a cada operação e acompanham a operação sem dados. **[a validar com a federação]**
- **Uma dúvida descoberta:** **[a preencher em sala]**
- **Uma suposição que precisa ser validada:** **[a preencher em sala]** (candidatas: o organizador realmente opera sem internet; o cadastro hoje é refeito a cada operação.)
- **Enunciado revisado do problema:** **[a preencher em sala]**

## Ficha 4 · Matriz de decisão

Escala: 2 = atende claramente, 1 = atende parcialmente, 0 = ainda não atende. Pontuação é estimativa minha e deve ser revista após a Feira e a Entrevista. A soma apoia a decisão, mas não a substitui.

| Critério | Ideia 1 Central | Ideia 2 Solar | Ideia 3 RDO | Observação (Ideia 1) |
|---|---|---|---|---|
| Problema claro | 2 | 1 | 1 | Identifica usuário e consequência, mas o usuário ainda é hipótese |
| Usuário acessível | 2 | 1 | 1 | Há cliente real (Federação de Airsoft do DF e entorno); confirmar uma pessoa para consultar |
| Relevância | 2 | 1 | 2 | Sem a central não há visão consolidada nem ordens confirmadas |
| Viabilidade técnica | 2 | 1 | 2 | Assumo que a stack MEVN já é familiar (operational-command) **[confirmar]**. A Iteração 1 roda com simulador, sem depender do firmware incompleto |
| Escopo mínimo | 1 | 2 | 1 | O fluxo é único, mas cresceu com a inscrição por operação (inscrição → simulador → MQTT → regra → mapa); a trilha saiu do essencial |
| Testabilidade | 2 | 2 | 1 | Dedup e estados por tempo são regras puras |
| Aderência à disciplina | 2 | 1 | 2 | Contrato de API, modelo de dados (perfil, operação, inscrição), interface e regra de negócio |
| Evolução em 3 iterações | 2 | 2 | 2 | Rastreamento → ordens → hardware real e HMAC |
| **TOTAL** | **15** | **11** | **12** | |

**Frase de decisão:** Escolhemos o projeto **MeshTracker Central** porque atende ao usuário **organizador de operações de airsoft da Federação do DF e entorno**, resolve **o recadastro dos operadores a cada operação e a falta de visão consolidada em campo** e permite entregar inicialmente **a inscrição por operação e o acompanhamento ao vivo de operadores simulados no mapa, com estado por tempo sem sinal e regra testada**.

## Ficha 5 · Pitch e semáforo

**Pitch v1:** Para organizadores de operações de airsoft da Federação do DF e entorno, que recadastram os mesmos operadores a cada operação e não sabem onde cada um está em campo, propomos a Central MeshTracker, um painel web com perfil permanente do operador, inscrição por operação (time e classe) e mapa ao vivo. Na primeira iteração, entregaremos o fluxo de inscrever um operador já cadastrado e vê-lo no mapa, mudando de estado conforme o tempo sem sinal. Saberemos que funciona quando o organizador reinscrever o mesmo operador em uma segunda operação sem recadastrá-lo e identificar, sem explicação, quem está sem sinal e há quanto tempo. **[a validar com o usuário]**

- **Feedback Verde (o que está claro):** **[Sala]**
- **Feedback Amarelo (o que precisa ser recortado):** **[Sala]**
- **Feedback Rosa (onde ainda se descreve tecnologia):** **[Sala]**
- **Pitch v2:** **[a escrever após o feedback]**
