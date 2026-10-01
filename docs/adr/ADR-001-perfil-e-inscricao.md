# ADR-001: Perfil permanente do operador separado da inscrição por operação

- **Status:** proposto (rascunho da Aula 7)
- **Data:** 2026-09-30

## Contexto

O mesmo operador participa de várias operações de airsoft da Federação do Distrito Federal e entorno **[a validar com a federação]**. O autor identificou que, sem perfil permanente, o operador teria de se cadastrar de novo a cada operação. Time, classe e o dispositivo MeshTracker (`node_id`) podem mudar de uma operação para outra **[a validar]**. Além disso, a posição de pessoas é dado pessoal, então o consentimento e o rastreamento valem por operação. O modelo de dados precisa decidir onde cada atributo mora.

## Decisão

Modelar o **Operador** como perfil permanente (apelido único, nome, identificador estável) e criar a **Inscrição** como entidade própria, ligando operador e operação, com time, classe, dispositivo e consentimento de rastreamento. As posições pertencem à inscrição e só são gravadas para inscrições de operações em curso.

Regras que decorrem da decisão:

- uma inscrição por operador por operação;
- um dispositivo por inscrição em cada operação;
- alterar time ou classe muda só a inscrição, nunca o perfil;
- inscrever um operador já cadastrado em nova operação não exige novo cadastro.

A escolha da tecnologia de persistência (relacional ou documentos) fica para outra decisão. Este ADR trata apenas do modelo lógico.

## Alternativas consideradas

1. **Cadastro dentro de cada operação** (o operador é recriado a cada operação, com time e classe no próprio registro). Descartada inicialmente porque **[a fundamentar após a leitura]**. Argumentos candidatos, ainda não validados: causa o recadastro, duplica dados e impede o histórico do operador entre operações.
2. **Perfil permanente com time, classe e dispositivo no próprio perfil** (sem inscrição). Descartada inicialmente porque **[a fundamentar após a leitura]**. Argumentos candidatos, ainda não validados: esses atributos podem mudar por operação, e o valor anterior se perderia.

## Justificativa

Frase de ligação:

> Com base em **[autor e obra, após a Ficha 7]**, decidimos **separar o perfil permanente do operador da inscrição por operação** porque **[a fundamentar com o conceito lido]**. A alternativa **de cadastrar o operador dentro de cada operação** foi inicialmente descartada porque **[a fundamentar]**.

A referência precisa estar ligada a esta decisão, não apenas listada no fim.

## Consequências esperadas

- **Positivas:** fim do recadastro, histórico do operador entre operações, consentimento e rastreamento por inscrição, e regras de unicidade claras e testáveis.
- **Negativas:** mais entidades e telas (perfil e inscrição), o que já pesou na matriz (escopo mínimo 1). Exige um identificador estável do operador **[a validar com a federação]** e uma política de retenção das posições (dúvida 3 do backlog).

## Referências consultadas

- CEUBOOK. *Engenharia da Computação — Desenvolvimento de Sistemas*. Brasília: CEUB, 2024. **[capítulo a confirmar na biblioteca]**
- PRIMO, A. L. G.; MURARI, M. L.; OLIVEIRA, L. R. A. de. Desenvolvimento de um sistema de informação web para quantificação da arborização urbana. *Revista AIDIS de Ingeniería y Ciencias Ambientales*, v. 15, n. 1, p. 465, 2022. **[confirmar se trata de modelo de dados]**

Observação: o slide 22 agrupa "CEUBOOK; PRIMO et al." sob o título "Desenvolvimento de Sistemas, CEUB, 2024", mas o slide 29 lista duas obras distintas (o CEUBOOK de 2024 e um artigo de 2022). Confira qual delas trata de modelo de dados antes de citar.
