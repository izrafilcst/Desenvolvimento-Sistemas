# ADR-001: Perfil permanente do operador separado da inscrição por operação

**Status:** proposto · **Data:** 01/10/2026 · **Autor:** Rafael Alves de Sousa Costa

## Contexto

Os operadores de airsoft costumam participar de várias operações da federação. Se o sistema guardasse tudo dentro de cada operação, a mesma pessoa teria de se cadastrar de novo a cada vez. Além disso, time, classe e o dispositivo MeshTracker que a pessoa usa podem mudar de uma operação para outra, e a posição de alguém em campo é dado pessoal: o consentimento e o rastreamento valem só para a operação em que a pessoa está inscrita. Ainda não confirmei com a federação como isso funciona na prática; parto do que percebi ao desenhar o operational-command.

## Decisão

Vou separar duas coisas. O **operador** é um perfil permanente, com apelido único, nome e um identificador estável, cadastrado uma única vez. A **inscrição** liga um operador a uma operação e guarda o que vale só ali: time, classe, dispositivo e consentimento de rastreamento. As posições pertencem à inscrição e só são gravadas enquanto a operação está em curso.

Isso gera quatro regras que vou testar: um operador tem no máximo uma inscrição por operação; um dispositivo pertence a no máximo uma inscrição por operação; mudar time ou classe altera só a inscrição; e inscrever um operador que já existe em uma nova operação não pede novo cadastro. A escolha entre banco relacional e de documentos fica para outra decisão; aqui trato só do modelo lógico.

## Alternativas que descartei

- **Cadastrar o operador dentro de cada operação**, com time e classe no próprio registro. Descartei porque força o recadastro, duplica dados e impede ver o histórico de uma mesma pessoa.
- **Guardar time, classe e dispositivo no perfil**, sem inscrição. Descartei porque esses dados podem mudar de uma operação para outra, e o valor anterior se perderia.

## Justificativa

Com base no CEUBOOK (2024), que a aula indica para decisões de modelo de dados, decidi separar o perfil permanente do operador da inscrição por operação porque o operador se cadastra uma única vez e tudo o que muda a cada operação fica registrado na inscrição. A alternativa de cadastrar o operador dentro de cada operação foi descartada porque obrigaria o recadastro e duplicaria dados. Ainda não li o capítulo correspondente: a leitura não foi realizada, e a fundamentação com o conceito do livro será completada depois dela.

## Consequências

O que ganho: fim do recadastro, histórico do operador entre operações, consentimento por inscrição e regras de unicidade fáceis de testar. O que pago: mais entidades e mais telas, a necessidade de um identificador estável para o operador (ainda não sei se a federação tem um número de registro) e uma política de quanto tempo guardar as posições depois da operação.

## Referências

- CEUBOOK. Engenharia da Computação — Desenvolvimento de Sistemas. Brasília: CEUB, 2024. Capítulo ainda não lido.
- PRIMO, A. L. G.; MURARI, M. L.; OLIVEIRA, L. R. A. de. Desenvolvimento de um sistema de informação web para quantificação da arborização urbana. Revista AIDIS de Ingeniería y Ciencias Ambientales, v. 15, n. 1, p. 465, 2022. Também indicada pela aula; ainda não consultada.
