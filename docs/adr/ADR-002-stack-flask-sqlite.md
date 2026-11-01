# ADR-002: Flask e SQLite no lugar da stack MEVN

**Status:** aceito · **Data:** 01/11/2026 · **Autor:** Rafael Alves de Sousa Costa

## Contexto

A proposta da Aula 7 (Ficha 8) listava Vue 3 com Vite, Node.js com Express, MongoDB, Mosquitto, WebSocket e Docker Compose, a mesma stack do operational-command. Ao montar os incrementos na Aula 10 (Ficha 12), percebi que ela não cabe no meu prazo: são 9 dias até o Incremento 1, em 10/11, e faço o projeto sozinho. A avaliação pesa o Book em 60% e o MVP em 40%, então o tempo do MVP não pode consumir o do Book. Além disso, a demonstração da faculdade precisa ser independente do operational-command: não reaproveita o código dele nem se integra a ele.

O consumo é pequeno: um organizador, uma operação por vez, até cerca de 10 operadores simulados, tudo num único notebook, em um processo Python mais o simulador.

O ADR-001 também deixou uma escolha em aberto: banco relacional ou de documentos. Este ADR resolve as duas coisas, a stack e o banco.

## Decisão

Uso Python 3.12 e Flask, com páginas em templates Jinja renderizadas no servidor, em HTML e CSS simples. Uso SQLite pelo módulo `sqlite3` da biblioteca padrão, sem ORM; o esquema fica em `src/schema.sql`. O mapa usa o Leaflet copiado para `src/static/vendor/`, sem CDN, com os tiles do OpenStreetMap quando houver internet. Os testes usam pytest. O simulador é um script Python que usa só a biblioteca padrão (`urllib`). Não há Node, Docker nem build de front-end.

O código se organiza em camadas, e as chamadas seguem o sentido rotas → serviços → repositório → SQLite:

```
src/
  app.py           create_app(); rotas HTTP e de páginas. Não contém regra de negócio.
  servicos.py      Regras de negócio. Funções que recebem o repositório e devolvem resultado ou erro de negócio.
  repositorio.py   Todo o SQL. Única camada que conhece o SQLite.
  db.py            Conexão e inicialização do banco a partir de schema.sql.
  schema.sql
  simulador.py     Processo separado (Incremento 2).
  templates/  static/
tests/
  test_servicos.py  test_rotas.py  test_api.py  conftest.py (banco temporário por teste)
```

As regras de negócio são testadas direto em `servicos.py`, com um banco SQLite temporário.

Com o banco relacional, a unicidade das regras R2 (um operador tem no máximo uma inscrição por operação) e R3 (um dispositivo pertence a no máximo uma inscrição por operação) passa a ser garantida pelo próprio banco, com restrições de unicidade sobre (operador, operação) e sobre (operação, dispositivo) na tabela de inscrição. Isso resolve a dúvida que o ADR-001 deixou aberta.

O projeto instala, testa e roda com três comandos: `pip install -r requirements.txt`, `python -m pytest -q` e `python src/app.py`.

## Alternativas que descartei

- **MEVN (Vue, Express, MongoDB, WebSocket e Docker).** Descartei porque são quatro serviços e um build de front-end para um incremento de 9 dias.
- **Flask com MongoDB.** Descartei porque as regras R2 e R3 ficam mais simples como restrição de unicidade num banco relacional, declarada no mesmo `schema.sql` que cria as tabelas, e porque o MongoDB seria mais um servidor para subir.

## Justificativa

Com base em SOMMERVILLE (2018, seção 6.3.1), decidi organizar o MVP em Flask e SQLite, com as camadas rotas → serviços → repositório, porque assim a regra de negócio fica isolada e testável e o sistema inteiro roda num notebook com três comandos. A alternativa MEVN foi descartada porque exigia quatro serviços e um build de front-end para um incremento de 9 dias.

A escolha da stack é uma decisão sobre técnicas de construção (bibliotecas, estruturas e ferramentas), um dos tipos de decisão para os quais o guia de ADR da AWS (KUNCE; GOBY, 2022, p. 3) pede um registro. O mesmo guia diz que, no mínimo, um ADR define o contexto, a decisão e as consequências (p. 4); é a estrutura que sigo aqui, com as alternativas e a justificativa a mais.

Este ADR não substitui nenhum outro. A stack MEVN estava na proposta da Aula 7, e não em um ADR, e a dúvida do ADR-001 era uma pergunta em aberto, não uma decisão tomada. Pelo guia da AWS, o estado Substituído é o de um ADR aceito que um novo ADR troca (p. 7), e não é o caso aqui.

## Consequências

O que ganho: instalo, testo e rodo o MVP com três comandos, sem Node, Docker nem build de front-end; os testes das regras são rápidos, porque rodam direto em `servicos.py` com um SQLite temporário, sem subir servidor nem broker; a Definição de Pronto do Kit vale sem adaptação, porque a stack é da mesma família do modelo OS_OFB do professor (Flask, SQLite, `servicos.py` e pytest); e as regras R2 e R3 passam a ser garantidas pelo banco, e não só pelo código.

O que pago: sem WebSocket, não há tempo real por empurrão, então o mapa consulta a situação a cada 3 segundos; trocar de banco depois exige migração, porque, mesmo com todo o SQL em `repositorio.py`, o esquema e os dados teriam de ser levados para o novo banco; e o SQLite sem ORM atende ao consumo pequeno que descrevi no contexto, não a muitos acessos simultâneos.

## Referências

- SOMMERVILLE, Ian. *Engenharia de software*. Tradução: Luiz Cláudio Queiroz. Revisão técnica: Fábio Levy Siqueira. 10. ed. São Paulo: Pearson Education do Brasil, 2018.
- KUNCE, Darius; GOBY, Dominik. *Usar registros de decisão de arquitetura para agilizar a tomada de decisões técnicas para um projeto de desenvolvimento de software*. [S. l.]: Amazon Web Services, mar. 2022. (AWS Prescriptive Guidance). Disponível em: https://docs.aws.amazon.com/pt_br/prescriptive-guidance/latest/architectural-decision-records/. Acesso em: 1 nov. 2026.
