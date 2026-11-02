# Proposta de projeto em uma página

Esta é a Ficha 8 do Caderno de Dinâmicas da Aula 7.

| Campo | Conteúdo |
|---|---|
| **Revisão** | Revisada em 01/11/2026 após o recorte do escopo (ADR-002 e ADR-003). |
| **Nome provisório** | MeshTracker Central |
| **Aluno ou integrantes** | Rafael Alves de Sousa Costa (RA 22304563) |
| **Usuário principal** | Organizador de operações da Federação de Airsoft do Distrito Federal e entorno: a pessoa que monta a operação, inscreve os jogadores e acompanha o que acontece em campo. A federação é o público do operational-command, sistema que eu desenvolvo. |
| **Problema observado** | Percebi, ao desenhar o operational-command, que o operador teria de se cadastrar de novo a cada operação, mesmo sendo a mesma pessoa. Além disso, pelo desenho do firmware do MeshTracker, cada dispositivo só enxerga os vizinhos que alcança e esquece quem some por 2 minutos, então ninguém tem uma visão geral de onde cada operador está. Ainda não confirmei isso com a federação: é o que enxergo olhando para o meu próprio projeto. |
| **Como o problema é enfrentado atualmente** | Não confirmei com a federação. Imagino que o cadastro seja refeito a cada operação e que o acompanhamento em campo seja feito por rádio de voz. |
| **Consequência do problema** | O organizador perde tempo recadastrando gente que já conhece, pode demorar a perceber que um operador ficou sem contato e as decisões são tomadas sem dados. |
| **Proposta de solução** | Uma aplicação web em que o organizador mantém o perfil permanente de cada operador, inscreve o operador em cada operação com time e classe e o acompanha num mapa ao vivo com o estado de cada um (ativo, atrasado ou perdido). Nesta demo os sinais vêm de um simulador por HTTP, no mesmo contrato que um gateway real do MeshTracker poderia usar depois. |
| **Escopo mínimo** | Resumo da tabela E/I/D/F do backlog, por incremento. Incremento 1 (até 10/11), itens essenciais: cadastro permanente do operador e operação com situação e inscrição por operação (time, classe, dispositivo e consentimento). Incremento 2 (até 24/11), itens importantes: simulador e recebimento de sinais só de inscritos e sem duplicata, estado do operador e mapa ao vivo com lista lateral, e papel de observador só de leitura. Incremento 3 (até 08/12), item importante: API `/api/v1` documentada, com token do gateway. |
| **Fluxo da Iteração 1** | O organizador inscreve um operador já cadastrado numa operação, escolhendo time, classe e dispositivo e marcando o consentimento; o inscrito aparece na lista da operação e, se uma regra (R1 a R6) for violada, a mensagem aparece na mesma página. |
| **Funcionalidades fora do escopo inicial** | Fora do MVP (linha F do backlog): MQTT, gateway real, ordens, objetivos, topologia da malha e integração com o operational-command, porque exigem hardware, infraestrutura ou outro sistema (ADR-002 e ADR-003). Desejável (linha D): trilha dos últimos 10 pontos e exportação CSV, só se sobrar tempo no Incremento 3. |
| **Tecnologias inicialmente consideradas** | Python 3.12, Flask, SQLite, Jinja, Leaflet (servido pelo próprio app) e pytest (ADR-002). A stack MEVN com MQTT, da versão 1 desta proposta, foi descartada no recorte. |
| **Risco principal** | Validar sozinho: sem conversar com a federação, posso estar resolvendo um problema que o organizador não sente. Mitigação: roteiros cronometrados no papel de organizador, com a limitação declarada, e a conversa com a federação mantida como a pendência principal. |
| **Como a solução será validada** | Testes automatizados das regras R1 a R11, mais os roteiros cronometrados de H1 (até 3 min) e H2 (até 10 s), executados pelo autor no papel de organizador e gravados. A conversa com a federação ainda não aconteceu. |
| **Referência bibliográfica inicial** | CEUBOOK. Engenharia da Computação — Desenvolvimento de Sistemas. Brasília: CEUB, 2024 (capítulo ainda não lido). SOMMERVILLE, Ian. *Engenharia de software*. Tradução: Luiz Cláudio Queiroz. Revisão técnica: Fábio Levy Siqueira. 10. ed. São Paulo: Pearson Education do Brasil, 2018. |
| **Link do repositório** | https://github.com/izrafilcst/Desenvolvimento-Sistemas |
