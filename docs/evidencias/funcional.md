# Evidências funcionais: roteiro da demo de 10/11

Este documento prova o roteiro da demo de ponta a ponta, de duas formas: por
teste automatizado (test client do Flask) e num navegador real. Também registra
os tempos de H1 e H2, a reprodução pelo Guia num clone limpo e os defeitos
achados.

- **H1**: o organizador inscreve 5 operadores já cadastrados numa 2ª operação,
  sem redigitar dados pessoais, em até 3 min.
- **H2**: quem está perdido e há quanto tempo é apontado em até 10 s depois de
  abrir o mapa.

Base: ramo `demo/mvp-10-11`. O navegador rodou o app na porta 5001, com banco
temporário, o simulador `--parar MT-03 --apos 20` e o Playwright.

## 1. Teste automatizado

Arquivo: `tests/test_funcional.py` (21 testes, todos com o prefixo
`test_funcional_`). Comando:

```bash
python -m pytest tests/test_funcional.py -q
```

Resultado: `21 passed`. A suíte inteira também está verde (seção 6).

| Passo do roteiro | Teste | Regra |
|---|---|---|
| Cadastrar 5 operadores | `test_funcional_cadastra_cinco_operadores` | US01 |
| Operação 1: planejada, em curso, encerrada | `test_funcional_operacao1_vai_de_planejada_a_encerrada` | R6 |
| Operação 2 com os mesmos 5, sem novo cadastro | `test_funcional_h1_reinscreve_os_cinco_na_operacao2_sem_novo_cadastro` | R1, R4, H1 |
| Mudar time e classe não mexe no perfil | `test_funcional_alterar_time_e_classe_nao_muda_o_perfil` | R4 |
| Inscrição em operação encerrada | `test_funcional_operacao_encerrada_nao_aceita_inscricao` | R6 |
| Recusa: inscrição duplicada | `test_funcional_recusa_inscricao_duplicada` | R2 |
| Recusa: dispositivo repetido | `test_funcional_recusa_dispositivo_repetido` | R3 |
| Recusa: sem consentimento | `test_funcional_recusa_inscricao_sem_consentimento` | R5 |
| Passagem para em curso, uma por vez | `test_funcional_operacao2_passa_para_em_curso`, `test_funcional_so_uma_operacao_em_curso_por_vez` | R6 |
| API sem token e com token errado: 401 | `test_funcional_api_recusa_sem_token_e_com_token_errado` | R11 |
| Sinais: 201, 200 duplicado, 202 do MT-99 | `test_funcional_sinais_201_200_e_202`, `test_funcional_sinal_fora_de_operacao_em_curso_e_descartado` | R7, R8 |
| Os quatro estados com `relogio.avancar` | `test_funcional_quatro_estados_com_o_relogio`, `test_funcional_limites_exatos_dos_estados` | R9, H2 |
| Observador vê a operação, a lista e o mapa, sem formulários | `test_funcional_observador_ve_a_operacao_sem_formularios`, `..._ve_a_lista_de_operadores_e_operacoes_sem_formularios`, `..._ve_o_mapa_e_a_situacao` | R10 |
| Observador recebe 403 em toda escrita | `test_funcional_observador_recebe_403_em_toda_escrita` | R10 |
| Sem login vai para o login | `test_funcional_sem_login_vai_para_o_login` | US07 |
| Tudo numa tacada só | `test_funcional_roteiro_de_ponta_a_ponta` | todas |

Na H1, o teste confere que a lista de operadores é idêntica antes e depois da
Operação 2 (mesmos ids, apelidos, nomes e datas de cadastro) e que a contagem
continua em 5.

## 2. Evidências no navegador

Cada arquivo foi tirado ao vivo, com o app em `http://127.0.0.1:5001`, banco
temporário e as senhas e o token definidos por variável de ambiente (nenhum
deles aparece nos arquivos).

| Arquivo | O que mostra | Regra ou hipótese |
|---|---|---|
| `01-operadores.png` | Os 5 operadores cadastrados (Coruja, Falcão, Lobo, Pantera, Raposa), cada um com o nome, e o formulário "Cadastrar operador" com a nota "O cadastro é feito uma vez só" | US01, R1, H1 |
| `02-inscricao-charlie.png` | A Operação Charlie, feita ao vivo, com os 5 inscritos em times e classes diferentes dos da Bravo e a mensagem "Operador inscrito." O formulário de inscrição não pede nome nem outro dado pessoal | US03, US04, R1, R4, H1 |
| `03-recusa-duplicada.png` | Status 400 e a mensagem "Este operador já está inscrito nesta operação." Os 5 inscritos continuam 5 | R2 |
| `04-recusa-dispositivo.png` | Status 400 e a mensagem "Este dispositivo já pertence a outra inscrição desta operação." (Jaguar tentando o MT-01, que é do Falcão) | R3 |
| `05-recusa-consentimento.png` | Status 400 e a mensagem "A inscrição exige o consentimento de rastreamento." (caixa desmarcada) | R5 |
| `06-mapa-ativos.png` | Mapa da Bravo com 5 setas coloridas pelo time e os 5 operadores em "Ativo". Contador de sinais descartados (MT-99) | US06, R7, R9 |
| `07-mapa-perdido.png` | O MT-03 (Coruja) como "Perdido", no topo da lista, em vermelho, com "2 min 8 s" desde o último sinal. O anel da seta dele também fica vermelho | R9, H2 |
| `08-observador.png` | A Operação Bravo vista pelo observador: situação, botão "Abrir mapa" e a lista de inscritos. Não há "Iniciar operação", "Alterar" nem "Inscrever operador" | R10 |
| `curl-401-201.txt` | Comando e saída: 401 sem token e com token errado, 201 com token, 200 duplicado, 202 do MT-99 e a situação em JSON. O token aparece só como `$MESHTRACKER_TOKEN` | R7, R8, R11 |

Também no navegador, logado como observador, três escritas pelo `fetch` com o
token CSRF válido da própria página deram 403: `POST /operadores`,
`POST /operacoes/2/avancar` e `POST /operacoes/2/inscricoes`. A página tem um só
formulário, o de "Sair" (`/logout`).

Duas notas sobre como as evidências foram feitas:

- **Jaguar.** Com os 5 operadores já inscritos na Charlie, qualquer tentativa
  bate antes na inscrição duplicada (R2 vence R3). Para mostrar a recusa do
  dispositivo repetido, cadastrei um 6º operador, o Jaguar, depois de tirar o
  `01-operadores.png` e de medir a H1. Ele não entra em nenhuma medida.
- **Console do navegador.** Os únicos erros foram o 404 de `/favicon.ico` (ver
  defeito 4) e os 400 e 403 provocados de propósito.

## 3. Tempos de H1 e H2

**Ressalva.** As duas medidas foram automatizadas (script do Playwright): medem
o tempo do fluxo no sistema, com o servidor na mesma máquina e sem tempo de
leitura, escolha ou digitação de uma pessoa. Não são a medição de um organizador
real. A medição humana, que o plano pede (roteiro cronometrado, com gravação de
tela, executado pelo autor), fica para o ensaio.

### H1: do clique em "Operação Charlie" até o 5º inscrito aparecer

Meta: até 3 min.

| Inscrito | Tempo desde o clique |
|---|---|
| 1º, Falcão | 162 ms |
| 2º, Lobo | 260 ms |
| 3º, Coruja | 358 ms |
| 4º, Raposa | 455 ms |
| 5º, Pantera | **554 ms** |

- O fluxo tem 31 ações: 1 clique na operação e, por inscrito, 6 ações (escolher
  o operador, o time e a classe, digitar o dispositivo, marcar o consentimento,
  clicar em "Inscrever").
- Nenhum cadastro foi refeito: a contagem de operadores continuou em 5 e nenhum
  campo de dado pessoal foi preenchido (o teste automatizado confere o mesmo).
- Conta para o ensaio, sem ser medida: 3 min dividido por 31 ações dá cerca de
  5,8 s por ação. Se uma pessoa levar mais que isso em média, estoura a meta. A
  margem é pequena e é o ensaio humano que decide a H1.

### H2: da abertura do mapa da Bravo até o perdido aparecer no topo da lista

Meta: até 10 s. Com o MT-03 perdido (mais de 120 s sem sinal), cinco aberturas
seguidas, do clique em "Abrir mapa" até a primeira linha da lista mostrar
"Perdido":

| Abertura | 1ª | 2ª | 3ª | 4ª | 5ª |
|---|---|---|---|---|---|
| Tempo | 94 ms | 94 ms | 101 ms | 109 ms | 90 ms |

Mediana de 94 ms. O perdido vem na primeira resposta da API, sem esperar o
ciclo de 3 s do mapa (`INTERVALO_MS`), e a lista põe os perdidos e atrasados à
frente dos ativos. Num ensaio humano, o tempo que sobra dos 10 s é o de ver e
dizer em voz alta quem está perdido.

## 4. Reprodução pelo Guia, num clone limpo

Clone do ramo `demo/mvp-10-11` numa pasta temporária, venv novo dentro dele,
Windows 11 com PowerShell e Git Bash, Python 3.14.6, só os comandos do
`docs/guia-de-reproducao.md`. O clone veio no commit `c3998dc`, o mais novo do
ramo na hora.

| Passo | Resultado | Travou ou ficou ambíguo |
|---|---|---|
| 1. Clonar | Funcionou. Usei o caminho local no lugar de `<endereço-do-repositório>` | Não |
| 2. Criar e ativar o venv | `python -m venv .venv` e `Activate.ps1` funcionaram | Ambíguo: "se o `python` não for o 3.12, use `py -3.12`" contradiz o "3.12 ou mais novo" do início. Aqui o `python` é 3.14 e só há o 3.14, então `py -3.12` falharia. Em máquina com a política de execução do PowerShell restrita, o `Activate.ps1` também trava, e o Guia não diz o que fazer (aqui não travou) |
| 3. Instalar dependências | Flask 3.1.3 e as demais, sem erro | Só o aviso de que há pip novo, que é ruído |
| 4. Rodar os testes | `382 passed in 37s` | Não |
| 5. Gerar o token | Funcionou, com a variante do PowerShell (`$env:`) | Não |
| 6. Criar os dados da demo | 5 operadores, 3 operações, 2 usuários; senhas geradas mostradas uma vez | Não |
| 7. Subir o app | Subiu na porta 5000 e criou `instance/.secret_key` sozinho | Não |
| 8. Rodar o simulador | MT-01 a MT-05 em 201, MT-99 em 202, MT-03 parou aos 20 s | Não |
| 9. Abrir o mapa | Entrou como `organizador`, Operações, Operação Bravo, Abrir mapa | Menor: depois do login já se cai em Operações, então o passo 3 ("Clique em Operações") é redundante. O "Abrir mapa" é um link com cara de botão |
| 10. O que se deve ver | 5 setas, 12 tiles do mapa carregados, MT-03 atrasado aos 62 s e perdido aos 122 s, MT-99 só no contador de descartados | Não |
| 11. Conferir a API com curl | 401 sem token, 201 com token, situação em JSON, no Git Bash | **Travou no PowerShell**: o `curl` é alias de `Invoke-WebRequest` e dá "parâmetros obrigatórios ausentes: Uri". Este passo não tem a versão do PowerShell, ao contrário dos passos 2 e 5. Contornei no Git Bash |
| Recomeçar do zero | Rodar o seed com o banco cheio dá "O banco já tem dados" e código 1. Com o app parado, `Remove-Item instance\meshtracker.db` e o seed funcionaram | Não. Com o app ligado, o Windows trava o arquivo, mas o Guia já manda parar o app antes |

A frase "leva uns 15 minutos" bate com o que vi (o grosso é o `pip install` e os
testes, uns 40 s cada).

## 5. Defeitos encontrados

Nenhum bloqueia o roteiro da demo. Todos foram enviados à líder por mensagem,
com o passo, o esperado e o obtido, e nenhum foi corrigido por mim.

| # | Onde (dono) | O que acontece | Gravidade |
|---|---|---|---|
| 1 | `docs/guia-de-reproducao.md`, passo 11 (docs) | No PowerShell, o `curl` do Guia não roda (alias de `Invoke-WebRequest`) e o passo não tem versão PowerShell | Menor |
| 2 | `docs/guia-de-reproducao.md`, passo 2 (docs) | A frase do `py -3.12` contradiz "3.12 ou mais novo" | Menor |
| 3 | `src/templates/mapa.html` (mapa-api) | O cabeçalho mostra "2026-11-10" e "em curso"; a página da operação mostra "10/11/2026" e "Em curso" | Menor |
| 4 | `src/templates/base.html` (web) | Toda página pede `/favicon.ico` e recebe 404, que vira erro no console | Menor |

Observação sem pedido de correção: depois de uma recusa (400), a barra de
endereço fica em `/operacoes/<id>/inscricoes`, a URL do POST. Um F5 reenvia o
formulário. É o contrato (a mesma página volta com 400). Vale avisar quem
apresenta para não dar F5 na tela de erro.

## 6. Como repetir

```bash
python -m pytest tests/test_funcional.py -q   # o roteiro pelo test client
python -m pytest -q                           # a suíte inteira
```

Resultado da suíte inteira, no worktree da funcional (base `c35e497`):
`402 passed` (381 que já existiam e 21 do roteiro funcional). O número muda
quando os outros donos entregam mais testes.
