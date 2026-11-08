# Revisão de segurança da demo

- **Data:** 08/11/2026, para a demo de 10/11.
- **Base revisada:** `demo/mvp-10-11` em `71df3bf`, que já inclui as correções de S-1, S-2 e S-3.
- **Testes:** `tests/test_seguranca.py` (66 testes, todos com nome `test_seg_...`).

## Escopo

Lido por inteiro: `src/app.py`, `config.py`, `auth.py`, `db.py`, `repositorio.py`,
`servicos.py`, `paginas.py`, `api.py`, `simulador.py`, `demo_seed.py`, `schema.sql`,
`templates/`, `static/js/mapa.js` e `tests/conftest.py`. Ficaram de fora o PDF, o XLSX,
a pasta `scripts/` e as bibliotecas em `static/vendor/`.

Modelo de ameaça: o app roda num notebook e só escuta em 127.0.0.1. A posição de uma
pessoa é dado pessoal (LGPD). O observador só lê, e qualquer escrita dele recebe 403
(R10). `POST /api/v1/sinais` exige o token do gateway (R11). Os GETs da API aceitam
sessão ou token.

## Como reproduzir

Rode da raiz do repositório, com o venv do projeto:

```bash
python -m pytest -q tests/test_seguranca.py          # só a revisão de segurança
python -m pytest -q                                  # suíte inteira
python -m bandit -r src
python -m pip_audit -r requirements.txt

# Segredos na árvore atual (a saída esperada são só valores de teste e o marcador "cole-o-token-aqui")
git grep -n -I -i -E "(token|senha|secret|chave|password|api[_-]?key)[a-z_]*[\"']?[[:space:]]*[:=][[:space:]]*[\"'][^\"'<\$]{6,}" -- . ':!src/static/vendor'

# Segredos no histórico do branch (a saída esperada é 0)
git log -p --no-textconv --no-ext-diff HEAD -- . ':!src/static/vendor' \
  | grep -a -c -E "^\+.*([0-9a-f]{64}|-----BEGIN|MESHTRACKER_(TOKEN|SECRET_KEY|SENHA_[A-Z]+)=[A-Za-z0-9_-]{16,})"
```

`--no-textconv` é necessário: sem ele, o filtro de diff dos `.docx` falha e o
`git log -p` para no meio do histórico.

**Resultado em 71df3bf:** `pytest -q` dá 448 passed e 1 xfailed. O xfail era o S-4, que
ainda estava aberto. Depois da integração da correção do S-4 (`6bc0608`), a suíte
inteira passa sem xfail.

## Checklist

| Item | Teste ou evidência | Resultado |
|---|---|---|
| Toda rota de escrita dá 403 para o observador (percorrendo `app.url_map`) | `test_seg_observador_recebe_403_em_toda_escrita`, `test_seg_url_map_so_tem_get_e_post` | ok: 5 rotas POST, nada gravado |
| Sem sessão, toda página (GET e POST) redireciona para o login | `test_seg_sem_sessao_toda_pagina_vai_ao_login` | ok |
| Formulário sem token de CSRF é recusado (`WTF_CSRF_ENABLED=True`) | `test_seg_csrf_formulario_sem_token_recusado`, `test_seg_api_isenta_de_csrf_mas_exige_token` | ok: 400 sem token e com token forjado, inclusive em `/login` e `/logout` |
| `POST /api/v1/sinais` dá 401 sem token ou com token errado | `test_seg_sinais_sem_token_valido_recebe_401` (8 casos, inclusive token na query string), `test_seg_sinais_nao_aceita_sessao_no_lugar_do_token`, `test_seg_sem_token_configurado_nada_passa` | ok |
| O token é comparado com `hmac.compare_digest` | `test_seg_token_comparado_com_compare_digest` (espião na função) | ok |
| GETs da API exigem sessão ou token | `test_seg_gets_da_api_exigem_sessao_ou_token` | ok |
| A senha é guardada como hash | `test_seg_senha_guardada_como_hash_com_sal` | ok: scrypt do Werkzeug, com sal |
| Cookie de sessão com HttpOnly e SameSite=Lax | `test_seg_cookie_de_sessao_httponly_e_samesite_lax` | ok: não há cookie `remember_token` |
| Debug desligado em `python src/app.py` | `test_seg_debug_desligado_em_python_src_app` | ok: `run(host="127.0.0.1", debug=False)` |
| Todo SQL usa parâmetros: `' OR 1=1 --` é gravado literalmente | `test_seg_sql_injecao_no_apelido_gravada_literalmente`, `test_seg_sql_injecao_no_login_nao_entra`, `test_seg_sql_so_com_parametros_no_codigo` (AST de `repositorio.py` e `db.py`) | ok |
| XSS: `<script>` no apelido sai escapado; `mapa.js` só usa `textContent` | `test_seg_xss_apelido_e_nome_escapados_nas_paginas` (4 páginas, incluindo o mapa), `test_seg_xss_refletido_no_login_escapado`, `test_seg_templates_com_autoescape_sem_safe_nem_script_inline`, `test_seg_mapa_js_so_usa_textcontent` | ok |
| Limites de entrada da API (400) | `test_seg_limites_da_api_recebem_400` (18 corpos, incluindo NaN, Infinity, bool, 2^63 e 5000 dígitos), `test_seg_parametros_e_ids_gigantes_nao_viram_500`, `test_seg_json_muito_aninhado_recebe_400` | ok depois do S-2 |
| Nenhum segredo no git, nem no histórico do branch | `test_seg_nenhum_arquivo_sensivel_versionado`, `test_seg_sem_token_configurado_nada_passa` (sem token nem chave padrão no código), comandos `git grep` e `git log -p` acima | ok: só valores de teste do `conftest.py` e dos testes, mais o marcador `cole-o-token-aqui` dos docs; nenhum `.db`, `.env`, `instance/` ou `.secret_key` versionado em nenhum commit |
| `bandit -r src` sem achado alto | ver a seção sobre o bandit | ok: 0 alto |
| `pip-audit -r requirements.txt` sem vulnerabilidade conhecida | ver a seção sobre o pip-audit | ok: 0 |
| Extra: open redirect no `next` do login | `test_seg_login_next_so_aceita_caminho_do_site` (9 destinos externos e 1 interno) | ok |
| Extra: enumeração de usuário no login | `test_seg_login_mesma_resposta_para_login_inexistente`, `test_seg_login_inexistente_tambem_confere_hash` | ok depois do S-3 |
| Extra: cabeçalhos CSP, X-Frame-Options, nosniff e Referrer-Policy | `test_seg_cabecalhos_de_seguranca` (página, API e 404) | ok: `script-src 'self'`, `frame-ancestors 'none'` |
| Extra: DoS trivial com corpo enorme | `test_seg_corpo_enorme_na_api_recebe_413`, `test_seg_corpo_enorme_no_login_recebe_413` | ok depois do S-1 |
| Extra: dados pessoais em log | `test_seg_modulos_do_servidor_nao_registram_dados_em_log`, `test_seg_simulador_nao_imprime_token_nem_posicao` | ok |
| Extra: o que o simulador faz com o token | `test_seg_simulador_nao_imprime_token_nem_posicao`, `test_seg_simulador_nao_reenvia_token_em_redirecionamento` | ok depois do S-4: o simulador não imprime o token nem segue redirecionamento |

## Achados

| Id | Severidade | Arquivo | Descrição | Destino |
|---|---|---|---|---|
| S-1 | Baixa | `src/config.py`, `src/app.py` | Não havia `MAX_CONTENT_LENGTH`. Um `POST /login` multipart de 2 MB, sem sessão, era lido inteiro, porque o CSRF lê o formulário antes da view. Um JSON de 2 MB com token era aceito (202). | Corrigido pela líder em `45b0305`: limite de 64 KB e 413 `corpo_grande` em JSON na API. |
| S-2 | Baixa | `src/api.py` (`receber_sinal`) | Com JSON aninhado em cerca de 20 mil níveis, o `json.loads` levanta `RecursionError`, que o `get_json(silent=True)` não captura. O resultado era 500 em vez de 400. Só quem tem o token chega lá. | Corrigido pelo mapa-api em `65ed6c1`. |
| S-3 | Baixa | `src/servicos.py` (`autenticar`) | Com um login que não existe, o scrypt não rodava: a resposta levava ~0,12 ms, contra ~128 ms com um login válido. O tempo revelava quais logins existem; a mensagem e o status já eram iguais. | Corrigido pelo regras em `ae6ce0a`: confere a senha contra um hash falso. |
| S-4 | Baixa | `src/simulador.py:172-173` (`chamar`) | `urllib.request.urlopen` segue 301/302 e reenvia `Authorization: Bearer` para o host do `Location`. Reproduzido em loopback, entre duas portas. | Corrigido pelo mapa-api em `6bc0608`: o simulador abre as URLs com um opener que não segue redirecionamento. A líder tirou o xfail na integração. |
| S-5 | Baixa | `src/simulador.py:235` (`--token`), `docs/guia-de-reproducao.md` | O token passado em `--token` aparece na lista de processos e no histórico do shell. | Aceito com justificativa: o notebook tem um só usuário e a variável `MESHTRACKER_TOKEN` é o caminho principal. O docs acrescenta no Guia a frase que recomenda a variável e avisa que `--token` fica no histórico e na lista de processos. |

## Observações aceitas para a demo

Estes pontos não são achados. São decisões conscientes para uma demo local, a rever se
o sistema sair do notebook.

- **Cookie sem `Secure`:** o app roda em HTTP, em 127.0.0.1. Com HTTPS, ligar `SESSION_COOKIE_SECURE`.
- **Sessão do Flask:** a sessão é um cookie assinado. O logout limpa o cookie no navegador, mas uma cópia antiga dele continua válida no servidor.
- **Tentativas de login:** não há limite. O app só escuta em 127.0.0.1, e cada tentativa custa um scrypt (~128 ms).
- **Servidor:** `app.run` usa o servidor de desenvolvimento do Werkzeug. Fora da demo, o certo é waitress ou gunicorn.
- **CSP:** tem `style-src 'unsafe-inline'` porque o Leaflet posiciona os marcadores com estilo inline. `script-src` é só `'self'`, e nenhum template tem script inline nem atributo `on*`.
- **Senhas da demo:** quando as variáveis não estão definidas, o `demo_seed.py` imprime as senhas geradas uma única vez no terminal. Elas não vão para nenhum arquivo.
- **Logs:** o servidor só registra a linha da requisição (método, caminho e status). A posição vai no corpo do `POST` e não aparece no log. Um erro 500 registra o traceback, sem o corpo.
- **Histórico do git:** um arquivo de trava do Word (`~$...docx`) entrou e saiu em commits de documentação (`604b85b`, `c7ab9e9`). Não é segredo, e o `.gitignore` já barra esse tipo de arquivo.

## bandit (`bandit -r src`, 1448 linhas)

| Regra | Severidade | Local | Justificativa |
|---|---|---|---|
| B310 (urlopen com esquema livre) | Média | `src/simulador.py:173` | `montar_configuracao` só aceita `--url` com `http://` ou `https://` e com host, então o urlopen nunca recebe `file:`. Aceito. |
| B311 (`random` não criptográfico) | Baixa | `src/simulador.py:278` | O `random` só sorteia o percurso simulado. Não é segredo nem token. Aceito. |

Total: 0 alto, 1 médio e 1 baixo, ambos com justificativa. Nenhum `# nosec` foi usado.

Depois da correção do S-4 (`6bc0608`), o simulador deixou de chamar `urlopen` e passou a
usar um opener próprio. Com isso, o B310 sumiu: o `bandit -q -r src` atual dá 0 alto,
0 médio e 1 baixo (o B311).

## pip-audit (`pip-audit -r requirements.txt`)

`No known vulnerabilities found`. Foram auditados Flask 3.1.3, Flask-Login 0.6.3,
Flask-WTF 1.3.0, pytest 9.2.0 e as dependências deles (Werkzeug 3.1.9, entre outras).
