# Guia de reprodução: do clone ao mapa

Este guia mostra como subir o MeshTracker Central no seu computador, carregar
dados de demonstração e ver o mapa com o simulador.

Leva uns 15 minutos. Não é preciso conhecer o projeto.

## Pré-requisitos

- Python 3.12 ou mais novo.
- Git.
- Internet, para o fundo do mapa (os tiles do OpenStreetMap). Sem internet, o
  mapa aparece cinza, mas o resto funciona.

Os comandos abaixo valem para bash (Linux, macOS e Git Bash no Windows). Onde o
PowerShell é diferente, a versão dele vem logo depois.

## 1. Clonar o projeto

```bash
git clone <endereço-do-repositório> meshtracker
cd meshtracker
```

## 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
```

Ative o ambiente:

```bash
# Linux e macOS
source .venv/bin/activate

# Git Bash no Windows
source .venv/Scripts/activate
```

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1
```

No Windows, se o `python` não for o 3.12, use `py -3.12 -m venv .venv`.

## 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

## 4. Rodar os testes

```bash
python -m pytest -q
```

Todos os testes devem passar. A última linha deve ser só `N passed`, sem nenhum `failed`.

## 5. Gerar o token do gateway

O token é a senha que os sinais dos dispositivos usam para entrar na API. O app
e o simulador precisam do mesmo token.

```bash
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

Copie o resultado e exporte a variável nos **dois** terminais que você vai usar
(o do app e o do simulador):

```bash
export MESHTRACKER_TOKEN="cole-o-token-aqui"
```

```powershell
$env:MESHTRACKER_TOKEN = "cole-o-token-aqui"
```

## 6. Criar os dados da demo

```bash
python src/demo_seed.py
```

O comando cria:

- Cinco operadores fictícios: Falcão, Lobo, Coruja, Raposa e Pantera.
- Três operações:
  - **Operação Alfa**: já encerrada.
  - **Operação Bravo**: em curso. É a que o simulador alimenta.
  - **Operação Charlie**: planejada e sem inscritos. Serve para a demonstração ao vivo.
- Dois usuários: `organizador` e `observador`.

As senhas dos usuários aparecem **uma única vez** no fim da saída. Anote-as.
Se você definir `MESHTRACKER_SENHA_ORGANIZADOR` e `MESHTRACKER_SENHA_OBSERVADOR`
antes de rodar, o comando usa essas senhas e não mostra nenhuma.

Se o banco já tem dados, o comando não grava nada e sai com erro. Veja
"Recomeçar" mais abaixo.

## 7. Subir o app (terminal 1)

Use o terminal em que você exportou `MESHTRACKER_TOKEN`:

```bash
python src/app.py
```

O servidor fica em `http://127.0.0.1:5000`. Deixe esse terminal aberto.

## 8. Rodar o simulador (terminal 2)

Abra outro terminal, ative o ambiente e exporte o mesmo `MESHTRACKER_TOKEN`
(passo 5). Depois rode:

```bash
python src/simulador.py --url http://127.0.0.1:5000 --parar MT-03 --apos 20
```

O simulador pega o token do ambiente. Se preferir, passe o token direto com
`--token <valor>`.

O simulador manda posições dos dispositivos MT-01 a MT-05 para a Operação Bravo.
Ele também manda sinais de um dispositivo sem inscrição (MT-99), que o sistema
descarta. O `--parar MT-03 --apos 20` faz o MT-03 parar 20 segundos depois do início.

## 9. Abrir o mapa

1. Abra `http://127.0.0.1:5000` no navegador.
2. Entre como `organizador`, com a senha anotada no passo 6.
3. Clique em **Operações**.
4. Clique em **Operação Bravo**.
5. Clique em **Abrir mapa**.

## 10. O que você deve ver

- Cinco setas se movendo no mapa, uma por dispositivo.
- MT-03 para. Cerca de 60 s depois, ele aparece como **atrasado**.
  Depois de 120 s parado, aparece como **perdido**.
- MT-99 não aparece no mapa. Ele só aumenta o contador de **descartados**.

## 11. Conferir a API com curl

Sem token, a API recusa (401):

```bash
curl -i http://127.0.0.1:5000/api/v1/situacao
curl -i -X POST http://127.0.0.1:5000/api/v1/sinais \
  -H "Content-Type: application/json" \
  -d '{"dispositivo": "MT-01", "pacote": 99, "lat": -15.799, "lon": -47.907, "bateria": 80}'
```

Com token, a posição é gravada (201). Este comando grava uma posição de verdade
no MT-01 da Operação Bravo. Se o mapa já estiver aberto, a seta do MT-01 pode
mudar um pouco. Não é problema para a demonstração.

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/sinais \
  -H "Authorization: Bearer $MESHTRACKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dispositivo": "MT-01", "pacote": 99, "lat": -15.799, "lon": -47.907, "bateria": 80}'
```

Para ver a situação da operação em curso:

```bash
curl -s http://127.0.0.1:5000/api/v1/situacao \
  -H "Authorization: Bearer $MESHTRACKER_TOKEN"
```

Mais exemplos e todos os códigos de erro estão em `docs/api.md`.

## Criar outros usuários

```bash
python src/app.py criar-usuario <login> <organizador|observador>
```

Exemplo: `python src/app.py criar-usuario ana.lima observador`. O comando pede a
senha duas vezes (ela não aparece na tela). A senha precisa ter pelo menos 8 caracteres.

## Recomeçar do zero

Pare o app (Ctrl+C), apague o banco e rode o seed de novo:

```bash
rm instance/meshtracker.db
python src/demo_seed.py
```

```powershell
Remove-Item instance\meshtracker.db
python src\demo_seed.py
```

Se você definiu `MESHTRACKER_DB`, apague o arquivo que essa variável aponta.

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `Address already in use` ao subir o app | A porta 5000 já está ocupada | Rode `python src/app.py --porta 5001` e use `http://127.0.0.1:5001` (e o `--url` do simulador) |
| Mapa cinza, sem fundo | Sem internet, ou o OpenStreetMap bloqueado | Confira a conexão. As setas e os dados continuam funcionando |
| Simulador mostra 401 | Token diferente nos dois terminais, ou `MESHTRACKER_TOKEN` não exportado no app | Exporte o mesmo valor nos dois terminais e reinicie o app |
| API responde 404 `sem_operacao_em_curso` | Nenhuma operação está em curso | Rode `python src/demo_seed.py` (ou recomece, veja acima) |
| `O banco já tem dados` ao rodar o seed | O banco já foi preenchido | Apague o banco e rode de novo, veja "Recomeçar do zero" |

## Variáveis de ambiente

| Variável | Padrão | Para que serve |
|---|---|---|
| `MESHTRACKER_TOKEN` | nenhum | Token do gateway. Sem ele, a API de sinais responde sempre 401 |
| `MESHTRACKER_DB` | `instance/meshtracker.db` | Arquivo do banco SQLite |
| `MESHTRACKER_SECRET_KEY` | criada e guardada em `instance/.secret_key` | Chave de sessão do Flask |
| `MESHTRACKER_ATRASADO_S` | `60` | Segundos sem sinal até o dispositivo ficar atrasado |
| `MESHTRACKER_PERDIDO_S` | `120` | Segundos sem sinal até o dispositivo ficar perdido. Precisa ser maior que o anterior |
| `MESHTRACKER_SENHA_ORGANIZADOR` | gerada | Senha do usuário `organizador` no seed (mínimo 8 caracteres) |
| `MESHTRACKER_SENHA_OBSERVADOR` | gerada | Senha do usuário `observador` no seed (mínimo 8 caracteres) |

As três primeiras e as duas de atraso e perda são lidas em `src/config.py`. As
duas `MESHTRACKER_SENHA_*` são lidas pelo `src/demo_seed.py`.
