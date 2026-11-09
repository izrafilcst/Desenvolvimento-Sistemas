# MeshTracker Central

Painel web para acompanhar ao vivo a posição e o estado dos operadores em operações de airsoft, a partir da rede LoRa do MeshTracker (nesta demo, com sinais simulados). É o meu projeto do Ciclo 2 de Desenvolvimento de Sistemas (Engenharia de Computação, CEUB, 2026/2).

**Aluno:** Rafael Alves de Sousa Costa · **RA:** 22304563

## Por que este projeto existe

Nas operações de airsoft da Federação do Distrito Federal e entorno, o organizador precisa inscrever os jogadores e acompanhar o que acontece em campo. Eu desenvolvo o operational-command, um sistema web para gerir operações, e o MeshTracker, um dispositivo com GPS e rádio LoRa que forma uma rede entre os jogadores sem depender de internet. Faltava ligar os dois.

Dois problemas me motivaram. O primeiro é que, sem um perfil permanente, o operador teria de se cadastrar de novo a cada operação, mesmo sendo a mesma pessoa. O segundo é que, pelo desenho do firmware, cada dispositivo só enxerga os vizinhos que alcança e esquece quem some por 2 minutos, então o organizador não tem uma visão geral. Ainda não conversei com a federação sobre isso: é o que percebo olhando para o meu próprio projeto.

## Em que ponto está

Book v1 revisado em 01/11/2026: o escopo foi recortado para caber nos incrementos do Ciclo 2 (ADR-002 e ADR-003).

Em 08/11/2026 ficou pronta a demo do MVP para a Aula 14 (10/11), no branch `demo/mvp-10-11`. Ela já cobre os três incrementos: cadastro permanente do operador, operação com situação, inscrição por operação, sinais filtrados e sem duplicata, estado do operador, mapa ao vivo, papel de observador, API `/api/v1` com token e Guia de reprodução. As regras R1 a R11 têm testes. Os operadores são simulados; a validação foi feita só pelo autor. A tag `v1.0` fica para a entrega do Incremento 3, em 08/12.

## O que entra em cada incremento

- **Incremento 1 (até 10/11):** cadastro permanente do operador, operação com situação e inscrição por operação (time, classe, dispositivo e consentimento), com as regras R1 a R6 testadas e os dados persistidos no SQLite.
- **Incremento 2 (até 24/11):** simulador, sinais só de dispositivos inscritos e sem duplicata, estado do operador (ativo, atrasado ou perdido), mapa ao vivo e papel de observador (regras R7 a R10).
- **Incremento 3 (até 08/12):** API `/api/v1` documentada, com token do gateway (R11), Guia de reprodução e release v1.0.

O Demo Day é em 15/12.

## O que fica de fora

MQTT, gateway real, ordens, objetivos, topologia da malha e integração com o operational-command. Exigem hardware, infraestrutura ou outro sistema, e a troca de stack e de contrato está registrada nos ADR-002 e ADR-003.

## Como executar

Com Python 3.12 ou mais novo, num ambiente virtual, o projeto instala, testa e roda com três comandos:

```
pip install -r requirements.txt
python -m pytest -q
python src/app.py
```

O app abre em http://127.0.0.1:5000. A API está documentada em [docs/api.md](docs/api.md), e o [Guia de reprodução](docs/guia-de-reproducao.md) traz cada passo com a explicação e os problemas comuns.

### Tutorial: ligar o sistema com o mapa ao vivo

Você vai usar dois terminais: um para o app e outro para o simulador. Os comandos abaixo são para o PowerShell, no Windows; no Linux, no macOS ou no Git Bash, os equivalentes estão logo depois.

**1. Na primeira vez, prepare o ambiente** (na raiz do repositório):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
```

Todos os testes devem passar. Se o PowerShell recusar o `Activate.ps1`, rode antes `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

**2. Na primeira vez, crie o token do gateway e os dados da demo:**

```powershell
python -c "import secrets; print(secrets.token_urlsafe(24))"
$env:MESHTRACKER_TOKEN = "cole-o-token-aqui"
python src/demo_seed.py
```

O seed cria 5 operadores e as operações Alfa (encerrada), Bravo (em curso, alimentada pelo simulador) e Charlie (planejada e vazia). Ele também cria os usuários `organizador` e `observador` e imprime as senhas uma única vez: anote-as. Guarde o token também, porque ele é pedido em toda sessão nova do terminal.

**3. Terminal 1, o app:**

```powershell
.venv\Scripts\Activate.ps1
$env:MESHTRACKER_TOKEN = "o-mesmo-token"
python src/app.py
```

**4. Terminal 2, o simulador:**

```powershell
.venv\Scripts\Activate.ps1
$env:MESHTRACKER_TOKEN = "o-mesmo-token"
python src/simulador.py --url http://127.0.0.1:5000 --parar MT-03 --apos 20
```

O simulador imprime uma linha por sinal. O `--parar MT-03 --apos 20` corta os sinais do MT-03 depois de 20 s: ele fica atrasado depois de 60 s sem sinal e perdido depois de 120 s.

**5. No navegador**, abra http://127.0.0.1:5000, entre como `organizador` e vá em Operações → Operação Bravo → Abrir mapa.

**Para desligar**, aperte Ctrl+C nos dois terminais. **Para recomeçar do zero**, apague `instance/meshtracker.db` e rode o seed de novo.

No Linux, no macOS e no Git Bash, a ativação é `source .venv/bin/activate` (Git Bash: `source .venv/Scripts/activate`), e a variável se define com `export MESHTRACKER_TOKEN="o-mesmo-token"`. O resto é igual.

### Para mexer no layout e no front

| Tela | Endereço | Arquivos |
|---|---|---|
| Login | `/login` | `src/templates/login.html` |
| Operadores | `/operadores` | `src/templates/operadores.html` |
| Operações | `/operacoes` | `src/templates/operacoes.html` |
| Uma operação (inscrição, recusas, transições) | `/operacoes/3` (Charlie) | `src/templates/operacao.html` |
| Mapa ao vivo | `/operacoes/2/mapa` (Bravo) | `src/templates/mapa.html`, `src/static/js/mapa.js`, `src/static/css/mapa.css` |
| Moldura comum (menu, mensagens) | todas | `src/templates/base.html`, `src/static/css/app.css` |

- O visual segue o [`DESIGN.md`](DESIGN.md) (tokens, estados e componentes). O CSS fica em `app.css` (base, moldura e páginas comuns) e `mapa.css`, sem framework. O app não tem build de front-end: o que você salva é o que o navegador recebe.
- **Mudou CSS ou JS:** recarregue a página com Ctrl+F5. **Mudou um template:** pare o app (Ctrl+C) e suba de novo, porque ele roda sem o modo de depuração.
- Para ver a tela do observador, entre com o usuário `observador` numa janela anônima.
- Os prints de todas as telas, bons para importar no Figma como referência, estão em [docs/evidencias/](docs/evidencias/). Os slides da demo ficam em `docs/apresentacao/` e abrem direto no navegador (setas para navegar, N para as notas).
- Depois de qualquer mudança, rode `python -m pytest -q`. Alguns testes conferem o HTML: o observador não pode ver formulários, todo formulário leva o `csrf_token` e nenhum texto vindo do servidor entra no mapa por `innerHTML`.

## Como regenerar o Caderno e o Kit

O Caderno (PDF) e o Kit (Excel) são gerados por scripts em `scripts/`. O Caderno precisa do LibreOffice Writer (`sudo apt install libreoffice-writer`) e os dois, de um ambiente virtual:

```
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/preencher_kit.py
.venv/bin/python scripts/gerar_caderno.py
```

O modelo do Kit precisa estar na pasta pai do repositório, com o nome padrão (`Kit_Artefatos_Aula_10_Jornada_do_Conhecimento_Ciclo_2_CEUB_v1.2.xlsx`), ou ser indicado com `--modelo CAMINHO`.

## Estrutura

```
README.md
docs/
  Caderno_Aula7_MeshTracker_Central.pdf   caderno de dinâmicas preenchido
  Kit_Aula10_MeshTracker_Central.xlsx     kit de artefatos da Aula 10 preenchido
  proposta.md                             proposta de uma página (Ficha 8)
  backlog.md                              escopo, regras, fluxo e critérios de aceite (Ficha 6)
  dinamicas.md                            método, matriz de decisão e pitch
  historias.md                            histórias de usuário e critérios de aceitação (Ficha 13)
  hipoteses-e-incrementos.md              hipóteses, incrementos e go/no-go (Fichas 11 e 12)
  api.md                                  contrato da API /api/v1, com exemplos em curl
  guia-de-reproducao.md                   do clone ao mapa com o simulador
  adr/
    ADR-001-perfil-e-inscricao.md         perfil permanente separado da inscrição
    ADR-002-stack-flask-sqlite.md         Flask e SQLite no lugar da stack MEVN
    ADR-003-gateway-por-http.md           sinais do gateway por HTTP no lugar de MQTT
  evidencias/                             prints, tempos e revisão de segurança da demo
  apresentacao/                           roteiro e slides da demo de 10/11
requirements.txt                          dependências para instalar, testar e rodar
requirements-dev.txt                      bandit e pip-audit, para a revisão de segurança
scripts/                                  gerador do Caderno e do Kit
src/
  app.py                                  create_app(), servidor e comando criar-usuario
  config.py                               variáveis de ambiente
  paginas.py  api.py                      rotas das páginas e da API (sem regra de negócio)
  auth.py                                 login, papéis (R10) e token do gateway (R11)
  servicos.py                             regras de negócio R1 a R9
  repositorio.py  db.py  schema.sql       todo o SQL, conexão e esquema do SQLite
  simulador.py                            operadores simulados, só pela API
  demo_seed.py                            dados da demo
  templates/  static/                     páginas Jinja, CSS, mapa.js, tema.js, Leaflet e fontes
tests/                                    pytest: serviços, páginas, API, simulador, segurança e roteiro
```

## Projetos relacionados

- **MeshTracker:** firmware para ESP32-S3 com GPS e rede mesh LoRa de 433 MHz.
- **operational-command:** aplicação web para gerir operações. A demo é independente: não integra nem reaproveita código do operational-command (ADR-002).
