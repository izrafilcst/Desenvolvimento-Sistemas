# API do MeshTracker Central

A API fica em `/api/v1`. Ela recebe sinais dos dispositivos e devolve a situação
das operações. Sempre responde em JSON.

Não há CSRF nesta API. A autenticação é por token (para quem envia sinais) ou
por token ou sessão (para as consultas).

## Autenticação

- **Token**: cabeçalho `Authorization: Bearer <token>`. O token é o valor de
  `MESHTRACKER_TOKEN` no servidor. Se a variável não estiver definida, nenhum
  token é aceito e a rota de sinais responde sempre 401.
- **Sessão**: o login pela página do sistema. Vale para as consultas `GET`, para
  organizador e observador.

Nos exemplos, o token está em `$MESHTRACKER_TOKEN`:

```bash
export MESHTRACKER_TOKEN="cole-o-token-aqui"
```

## Erros

Todo erro tem o mesmo formato:

```json
{"erro": "Token ausente ou inválido.", "codigo": "nao_autorizado"}
```

| Código | Status HTTP | Quando |
|---|---|---|
| `nao_autorizado` | 401 | Sem token, token errado, ou sem `MESHTRACKER_TOKEN` no servidor (nas consultas, também sem sessão) |
| `formato_invalido` | 400 | Corpo ou parâmetro com formato errado |
| `sem_operacao_em_curso` | 404 | `GET /situacao` sem parâmetro e sem operação em curso |
| `operacao_inexistente` | 404 | `GET /situacao?operacao=<id>` com id que não existe |
| `nao_encontrado` | 404 | Página ou rota que não existe |
| `metodo_nao_permitido` | 405 | Método HTTP que a rota não aceita |
| `proibido` | 403 | Papel sem permissão para a ação |

## POST /api/v1/sinais

Recebe uma posição de um dispositivo. Exige token.

Corpo (JSON):

```json
{"dispositivo": "MT-01", "pacote": 12, "lat": -15.799, "lon": -47.907, "bateria": 87.5}
```

| Campo | Tipo | Regra |
|---|---|---|
| `dispositivo` | texto | De 1 a 32 caracteres, sem vazio |
| `pacote` | inteiro | 0 ou mais |
| `lat` | número | De -90 a 90 |
| `lon` | número | De -180 a 180 |
| `bateria` | número | De 0 a 100 |

Respostas:

| Status | Corpo | Significado |
|---|---|---|
| 201 | `{"status": "gravado"}` | Posição guardada |
| 200 | `{"status": "duplicado"}` | Mesmo dispositivo e mesmo pacote já recebidos nesta operação. Nada novo é guardado |
| 202 | `{"status": "descartado"}` | Não há operação em curso, ou o dispositivo não está inscrito nela. Só a origem e o motivo são guardados, não a posição |
| 400 | `codigo: "formato_invalido"` | Corpo que não é objeto JSON, campo faltando ou com tipo errado, valor fora da faixa, número que não é finito, `pacote` que não é inteiro ou é negativo, `dispositivo` vazio ou com mais de 32 caracteres |
| 401 | `codigo: "nao_autorizado"` | Sem token, token errado, ou servidor sem `MESHTRACKER_TOKEN` |

Exemplo que grava uma posição:

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/sinais \
  -H "Authorization: Bearer $MESHTRACKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dispositivo": "MT-01", "pacote": 12, "lat": -15.799, "lon": -47.907, "bateria": 87.5}'
```

Resposta esperada: `HTTP/1.1 201` e `{"status": "gravado"}`.

Exemplo sem token (401):

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/sinais \
  -H "Content-Type: application/json" \
  -d '{"dispositivo": "MT-01", "pacote": 12, "lat": -15.799, "lon": -47.907, "bateria": 87.5}'
```

## GET /api/v1/situacao

Situação ao vivo de uma operação. Aceita token ou sessão.

- Sem parâmetro: a operação em curso. Se não há, 404 `sem_operacao_em_curso`.
- Com `?operacao=<id>`: a operação pedida. Se o valor não for inteiro, 400
  `formato_invalido`. Se a operação não existe, 404 `operacao_inexistente`.

Resposta 200:

```json
{
  "operacao": {
    "id": 2, "nome": "Operação Bravo", "data": "2026-11-10",
    "local": "Parque da Cidade", "situacao": "em_curso",
    "centro_lat": -15.799, "centro_lon": -47.907
  },
  "descartados": 3,
  "inscritos": [
    {
      "inscricao_id": 6, "apelido": "Falcão", "time": "Vermelho",
      "cor": "#d1242f", "classe": "Médico", "dispositivo": "MT-01",
      "estado": "ativo", "segundos": 4,
      "lat": -15.7992, "lon": -47.9068, "bateria": 87.5, "rumo": 90.0
    }
  ]
}
```

Campos dos inscritos:

- `estado`: `sem_sinal` (nenhuma posição), `ativo` (até 60 s desde a última
  posição), `atrasado` (de 60 s a 120 s), `perdido` (acima de 120 s). Os limites
  vêm de `MESHTRACKER_ATRASADO_S` e `MESHTRACKER_PERDIDO_S`.
- `segundos`: segundos desde a última posição. `null` se não há posição.
- `lat`, `lon`, `bateria`: da última posição. `null` se não há posição.
- `rumo`: em graus, 0 é norte e 90 é leste. O servidor calcula com as duas
  últimas posições distintas. `null` se não há um par de posições distintas
  (por exemplo, o operador parou desde o primeiro sinal).
- `descartados`: quantos sinais da operação foram descartados.

Exemplos:

```bash
# operação em curso
curl -s http://127.0.0.1:5000/api/v1/situacao \
  -H "Authorization: Bearer $MESHTRACKER_TOKEN"

# operação 2, pelo id
curl -s "http://127.0.0.1:5000/api/v1/situacao?operacao=2" \
  -H "Authorization: Bearer $MESHTRACKER_TOKEN"
```

## GET /api/v1/operacoes

Lista todas as operações. Aceita token ou sessão.

Resposta 200:

```json
{
  "operacoes": [
    {
      "id": 1, "nome": "Operação Alfa", "data": "2026-10-25",
      "local": "Parque da Cidade", "situacao": "encerrada",
      "centro_lat": -15.799, "centro_lon": -47.907, "inscritos": 5
    }
  ]
}
```

```bash
curl -s http://127.0.0.1:5000/api/v1/operacoes \
  -H "Authorization: Bearer $MESHTRACKER_TOKEN"
```

## Fontes de sinal

Hoje, a única fonte de sinais é o simulador (`src/simulador.py`), que chama
`POST /api/v1/sinais` como um dispositivo faria.

No futuro, a fonte pode ser um app de celular ou um gateway MeshTracker que
recebe os sinais por MQTT. Nos dois casos, a fonte deve falar este mesmo contrato
HTTP, conforme a ADR-003 (`docs/adr/ADR-003-gateway-por-http.md`). Nada disso
está pronto ainda. Esta seção descreve só a direção.
