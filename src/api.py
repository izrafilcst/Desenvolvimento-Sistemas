"""API /api/v1 (ADR-003, US05 e US08). Isenta de CSRF; autentica por token ou sessão.

Contrato (documentado em docs/api.md):

    POST /api/v1/sinais       auth.exigir_token  (R11)
        corpo {dispositivo, pacote, lat, lon, bateria}
        401 sem token ou token errado; 400 formato inválido;
        202 {"status":"descartado"} (R7); 200 {"status":"duplicado"} (R8);
        201 {"status":"gravado"}
    GET  /api/v1/situacao[?operacao=<id>]   auth.sessao_ou_token
        sem parâmetro: a operação em curso (404 sem_operacao_em_curso se não há);
        com parâmetro: a operação pedida (404 operacao_inexistente)
    GET  /api/v1/operacoes                  auth.sessao_ou_token

Erros sempre como {"erro": "...", "codigo": "..."}.
"""

from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api/v1")
