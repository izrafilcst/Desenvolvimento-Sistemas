# Reprodução pelo Guia, com as telas novas da fase 2

Este documento registra a reprodução do MVP do zero, seguindo só o
`docs/guia-de-reproducao.md`, até ver o mapa com o simulador nas telas novas
(moldura preta, seletor de tema, "Abrir mapa" como botão principal e "Encerrar
operação…" atrás de um `<details>`). É o critério de go/no-go do Incremento 3:
"Go para o Demo Day se o MVP for reproduzido do zero, num clone limpo e num venv
novo, seguindo só o Guia".

- **Data:** 10/11/2026.
- **Máquina:** Windows 11 Pro (10.0.26200), PowerShell, Python 3.14.6, Git. Internet
  disponível (os tiles do OpenStreetMap carregaram).
- **Commit do clone:** `dad318b` (ramo `fase-2/briefing`, o mais novo na hora; o
  anterior, `3e65b79`, só difere do `dad318b` no `README.md`).
- **Onde:** clone novo em `%TEMP%\repro-v1\clone`, fora do repositório, com venv novo
  dentro dele. O `.venv` do repositório principal não foi usado.
- **Tempo:** cerca de 10 minutos, do `git clone` à última conferência no navegador
  (10:44 às 10:54), sem contar a escrita deste documento. O `pip install` levou
  11 s porque o cache de pacotes do pip já estava quente. Numa máquina sem cache,
  conta mais.
- **Portas:** 5000 para o app, a que o Guia manda. Estava livre.

**Ressalva.** Quem reproduziu foi o próprio autor do projeto, com um agente, não
outra pessoa. Eu conheço o projeto e sei o que esperar de cada tela. Um colega
sem esse contexto pode tropeçar em pontos que aqui passaram batido. Por isso o
"sim" do fim deste documento vale como prova de que o Guia funciona, não como
prova de que um desconhecido o seguiria sem ajuda.

## 1. Passo a passo

Cada linha segue a numeração do Guia. Variáveis de ambiente só as que o Guia
manda: `MESHTRACKER_TOKEN` no app e no simulador. Não defini
`MESHTRACKER_SENHA_*` nem `MESHTRACKER_DB`.

| Passo | Resultado | Travou ou ficou ambíguo |
|---|---|---|
| 1. Clonar | Funcionou. Usei o caminho local no lugar de `<endereço-do-repositório>`, no ramo `fase-2/briefing`. | Não |
| 2. Criar e ativar o venv | `python -m venv .venv` e `.\.venv\Scripts\Activate.ps1` funcionaram. O `python` do venv ficou dentro do clone. A frase do `py -3.12`, que contradizia o "3.12 ou mais novo" na reprodução de 08/11, agora está certa ("só se o `python` for anterior ao 3.12") e não pegou aqui, porque o `python` é 3.14. | Não |
| 3. Instalar as dependências | `pip install -r requirements.txt` instalou Flask 3.1.3, Flask-Login 0.6.3, Flask-WTF 1.3.0 e pytest 9.2.0, em 11 s. Só o aviso de que há pip novo, que é ruído. | Não |
| 4. Rodar os testes | `python -m pytest -q`: **528 passed in 58 s**, sem `failed`. A última linha bate com o que o Guia manda esperar (`N passed`). | Não |
| 5. Gerar o token | `python -c "import secrets; ..."` e `$env:MESHTRACKER_TOKEN = "..."` (variante do PowerShell) funcionaram. O token ficou só na sessão e em arquivo fora do repositório. | Não |
| 6. Criar os dados da demo | `python src/demo_seed.py`: 5 operadores, 3 operações (Alfa encerrada, Bravo em curso, Charlie planejada) e os usuários `organizador` e `observador`, com as senhas geradas mostradas uma vez. Bate com a lista do Guia. | Não |
| 7. Subir o app | `python src/app.py` subiu em `http://127.0.0.1:5000` e criou `instance/.secret_key` e `instance/meshtracker.db` sozinho. `GET /` respondeu 302 para o login. | Ambíguo, menor: o app imprime `WARNING: This is a development server...`, e o Guia não diz que o aviso é esperado. Quem lê "WARNING" pode achar que algo deu errado. |
| 8. Rodar o simulador | `python src/simulador.py --url http://127.0.0.1:5000 --parar MT-03 --apos 20`, com o mesmo token: MT-01 a MT-05 em `201 gravado`, MT-99 em `202 descartado`, e o MT-03 parou 20 s depois do início. | Ambíguo, menor: a saída traz também linhas `200 duplicado` (o simulador reenvia um pacote antigo de propósito), e o Guia não explica. Parece erro e não é. |
| 9. Abrir o mapa | Login como `organizador` (campos **Login** e **Senha**, botão **Entrar**), depois a Operação Bravo e **Abrir mapa**. O mapa abriu em `/operacoes/2/mapa`. | Ambíguo, menor, em três pontos. (a) Depois do login o app já cai em **Operações**, então o item 3 ("Clique em **Operações**") é redundante. (b) Na tela da Bravo, ao lado do **Abrir mapa**, está **Encerrar operação…**. O Guia não avisa que ele é irreversível: a operação deixa de aceitar sinais, e o mapa da demo morre. (c) **Abrir mapa** é um link com cara de botão (o botão principal, preto), e **Encerrar operação…** é o `<summary>` de um `<details>` (botão secundário, só abre uma confirmação). O nome de cada um bate com o do Guia. |
| 10. O que você deve ver | Cinco setas com o nome do operador, a faixa de contagem (Perdidos, Atrasados, Ativos, Sem sinal, Descartados, Inscritos) e a tabela Operador, Time, Estado, Último sinal, Bateria. **Atrasado:** a Coruja (MT-03) apareceu como Atrasado aos 1 min 2 s sem sinal (segunda rodada do simulador). **Perdido:** apareceu aos 2 min 2 s, no topo da tabela, com o rótulo "CORUJA · PERDIDO · ÚLTIMO SINAL HÁ 2 MIN 14 S" no mapa. O MT-99 não aparece como seta; só o contador **Descartados** sobe (3 aos 8 s, 83 aos 2 min 33 s). | Ambíguo, menor, em dois pontos. (a) O Guia fala em "MT-03", mas o mapa e a tabela mostram o apelido, **Coruja**. Quem não sabe que o MT-03 é a Coruja (a tabela de inscritos da Bravo mostra o par) não acha o dispositivo. (b) Com o seletor de tema em **Sistema**, o mapa abre no tema escuro mesmo num sistema claro, e as outras telas seguem o sistema. O Guia não diz isso e a diferença espanta. |
| 11. Conferir a API com curl | Rodei a variante do PowerShell, com `curl.exe`: sem token 401, com token 201 (`{"status":"gravado"}`) e a situação em JSON, com `"estado":"ativo"` para os cinco. O defeito de 08/11 (sem versão do PowerShell) foi corrigido. | Não |
| Criar outros usuários | Não exercitado nesta rodada. | Não aplicável |
| Recomeçar do zero | Não exercitado nesta rodada. Já tinha sido provado na reprodução de 08/11 e o texto não mudou. | Não aplicável |

Resumo: **0 passos travaram** e **4 ficaram ambíguos** (7, 8, 9 e 10), todos de
gravidade menor. Nenhum impediu de chegar ao mapa.

## 2. Total de testes

`python -m pytest -q`, no clone, no venv novo: **528 passed in 58.23s**. Na
reprodução de 08/11 eram 382 (ramo `demo/mvp-10-11`); os testes novos são da fase 2
(telas, tema, mapa e simulador).

## 3. Como as telas novas aparecem no roteiro

Nomes de botão e de tela que mudaram em relação a 08/11, como apareceram aqui:

- **Moldura preta.** A barra do topo é preta, com o logo "MESHTRACKER CENTRAL", os links
  **Operadores** e **Operações**, o seletor de tema (**Sistema**, **Claro**, **Escuro**),
  o usuário ("organizador · organizador", login e papel) e o botão **Sair**.
  O observador vê, no lugar do papel, a etiqueta **Somente leitura**.
- **Títulos** em caixa alta e fonte larga. O `h1` aparece com uma animação de
  digitação (`digitar`): um print tirado logo depois de carregar a página pega o
  título cortado ("OPERAÇÃO CHAF"). Esperei 1,5 s antes de cada print.
- **Operações.** Tabela Operação, Data, Local, Situação, Inscritos, e o painel
  **Criar operação** ao lado.
- **Operação (dossiê).** Bloco com Data, Local, Situação, Centro e Inscritos.
  Planejada: **Abrir mapa** (principal, preto) e **Iniciar operação** (secundário).
  Em curso, para o organizador: **Abrir mapa** e **Encerrar operação…**, este
  dentro de um `<details>` que abre uma confirmação ("Depois de encerrada, a operação
  não aceita inscrições nem mudanças..."). Para o observador: só **Abrir mapa**.
- **Inscrever operador.** O formulário tem a mesma ordem de campos (Operador, Time,
  Classe, Dispositivo, consentimento, **Inscrever**). Quem já está inscrito aparece como
  "Falcão · inscrito" no seletor, desabilitado. A mensagem de sucesso agora diz o
  nome e os dados ("Falcão inscrito (Azul, Fuzileiro).") numa etiqueta **FEITO**; a de
  recusa vem numa etiqueta **RECUSA**, com status 400.
- **Mapa.** Título e situação, link **Ver inscrições**, faixa de contagem, mapa com
  réguas, retícula, escala e rótulo "Atualizado às HH:MM:SS", e a tabela de
  operadores com os perdidos e atrasados no topo.

## 4. Prints

Em `docs/evidencias/v1/`, com os mesmos nomes de `docs/evidencias/` (01 a 08). Todos a
partir do clone, em 1440 px de largura, com a barra de rolagem escondida
(`html{scrollbar-width:none}`), página inteira (a altura varia). O token e as
senhas não aparecem em nenhum.

| Arquivo | Tamanho | O que mostra |
|---|---|---|
| `01-operadores.png` | 1440×900 | Os 5 operadores (Coruja, Falcão, Lobo, Pantera, Raposa) e o formulário "Cadastrar operador" com a nota "O cadastro é feito uma vez só" |
| `02-inscricao-charlie.png` | 1440×1011 | A Operação Charlie com os 5 inscritos (Falcão Azul Fuzileiro MT-01, Lobo Vermelho Suporte MT-02, Coruja Verde Médico MT-03, Raposa Amarelo Atirador designado MT-04, Pantera Azul Suporte MT-05) e a etiqueta "FEITO · Pantera inscrito (Azul, Suporte)." |
| `03-recusa-duplicada.png` | 1440×1035 | R2: 400 e "Este operador já está inscrito nesta operação." Os inscritos seguem 5 |
| `04-recusa-dispositivo.png` | 1440×1059 | R3: 400 e "Este dispositivo já pertence a outra inscrição desta operação." (Jaguar tentando o MT-01, que é do Falcão) |
| `05-recusa-consentimento.png` | 1440×1059 | R5: 400 e "A inscrição exige o consentimento de rastreamento." (caixa desmarcada) |
| `06-mapa-ativos.png` | 1440×900 | A Bravo antes dos 60 s do MT-03: cinco setas, 5 Ativos, 0 Atrasados, 0 Perdidos, "Atualizado às 10:49:17" |
| `07-mapa-perdido.png` | 1440×900 | A Bravo depois dos 120 s do MT-03: a Coruja Perdida, no topo da tabela, "2 min 14 s" sem sinal, com o rótulo vermelho no mapa. 1 Perdido, 4 Ativos |
| `08-observador.png` | 1440×900 | A Bravo vista pelo observador: etiqueta "Somente leitura", **Abrir mapa** como única ação e a lista de inscritos, sem formulário, sem **Encerrar operação…** |

Três notas sobre como os prints foram feitos:

- **Ordem.** O Guia não cobre a inscrição na Charlie (diz só que ela "serve para a
  demonstração ao vivo"). Os prints 01 a 05 saíram com o app já no ar (passo 7) e
  antes de ligar o simulador (passo 8), para o relógio dos 60 s e dos 120 s do
  MT-03 só começar quando eu fosse fotografar o mapa. As inscrições seguiram a
  lista do pedido, não o Guia.
- **Jaguar.** Com os 5 já inscritos na Charlie, qualquer tentativa bate antes na
  inscrição duplicada (R2 vence R3). Para mostrar R3 e R5 cadastrei um 6º operador,
  o Jaguar ("Teste Jaguar"), depois do print 01. Ele não entra na Charlie. Para o
  R2, o `<option>` de Falcão, desabilitado no seletor, foi reabilitado na página antes de enviar.
- **Perdido.** O MT-03 parou 20 s depois do início do simulador (10:49:11) e o
  `07` saiu às 10:51:44, 2 min 14 s depois do último sinal dele.

## 5. Ajustes sugeridos para o Guia

Nenhum foi aplicado por mim. Quem aplica é a líder. Linhas do
`docs/guia-de-reproducao.md` na versão `dad318b`.

| # | Linha | Texto atual | Texto novo sugerido |
|---|---|---|---|
| 1 | 112 | `O servidor fica em `http://127.0.0.1:5000`. Deixe esse terminal aberto.` | Acrescentar: `O aviso "WARNING: This is a development server" é esperado. Pode ignorar.` |
| 2 | 129 | `...que o sistema descarta. O `--parar MT-03 --apos 20` faz o MT-03 parar 20 segundos depois do início.` | Acrescentar: `De vez em quando o simulador reenvia um pacote antigo de propósito. Aparece como "200 duplicado" e é esperado.` |
| 3 | 135 | `3. Clique em **Operações**.` | `3. Se ainda não estiver em **Operações**, clique nela (depois do login o app já abre nessa tela).` |
| 4 | 137 (depois do item 5 da lista) | (não existe) | Acrescentar: `Não clique em **Encerrar operação…** (ao lado de **Abrir mapa**, no tema novo). Encerrar não tem volta: a operação deixa de aceitar sinais e o mapa da demo para.` |
| 5 | 141 | `Cinco setas se movendo no mapa, uma por dispositivo.` | `Cinco setas se movendo no mapa, uma por operador, com o apelido (Coruja, Falcão, Lobo, Pantera e Raposa). Na tabela ao lado, cada um aparece com o estado e o tempo do último sinal.` |
| 6 | 142 | `MT-03 para. Cerca de 60 s depois, ele aparece como **atrasado**.` | `O MT-03, que é a Coruja, para. Cerca de 60 s depois, ela aparece como **atrasado**.` |
| 7 | 143 (depois dela) | (não existe) | Acrescentar: `O mapa abre no tema escuro, mesmo que o resto do app esteja claro. O seletor Sistema, Claro e Escuro, no topo, troca o tema.` |
| 8 | 144 | `MT-99 não aparece no mapa. Ele só aumenta o contador de **descartados**.` | Sem mudança. Está certo: o contador sobe (3 aos 8 s, 83 aos 2 min 33 s). |

Os ajustes 1, 2, 3, 4, 5, 6 e 7 são de redação. Nenhum pede mudança de código.
O ajuste 8 é só a confirmação de que a linha continua válida.

## 6. Pontos fora do Guia

- **Favicon.** `GET /favicon.ico` ainda dá 404 (defeito 4 de 08/11, aberto). Vira erro
  no console do navegador em toda página.
- **Animação do título.** O `h1` com a animação `digitar` leva mais de 300 ms para
  terminar. Em print ou em gravação de tela logo depois do carregamento, o título
  sai cortado. Quem grava o deck deve esperar um pouco.
- **Defeitos de 08/11 já corrigidos.** O `curl` do passo 11 ganhou a variante do
  PowerShell e funcionou. A frase do `py -3.12` foi consertada. O cabeçalho do mapa
  agora mostra a data no formato "10/11/2026", igual ao da página da operação.
- **Depois de uma recusa (400)** a barra de endereço fica em
  `/operacoes/<id>/inscricoes` (a URL do POST). Um F5 reenvia o formulário.
  É o contrato, como já estava anotado em 08/11.
- **Limpeza.** O app e o simulador que eu abri foram encerrados pelo número do
  processo (só os do clone). O clone em `%TEMP%\repro-v1\clone` ficou no disco.

## 7. Go ou no-go

**Reproduzido seguindo só o Guia: sim.**

Do clone limpo (`dad318b`) e de um venv novo, os 11 passos do Guia levaram ao mapa
da Bravo com cinco setas, a Coruja (MT-03) atrasada aos 62 s e perdida aos 122 s,
e o MT-99 só no contador de descartados, nas telas novas. A suíte passou inteira
(528 testes). Nenhum passo travou. Os 4 pontos ambíguos são de redação e cabem
nos ajustes da seção 5.

Ressalva, de novo: quem reproduziu foi o próprio autor, com um agente, não outra
pessoa. O Incremento 3 pede que o MVP seja reproduzido num clone limpo e num venv
novo, e isso foi feito. Se o critério for "alguém que não conhece o projeto
reproduz sozinho", falta um colega rodar o Guia, de preferência já com os ajustes
3, 4 e 6, que são os que mais ajudam quem não sabe o que esperar.
