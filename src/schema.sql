-- Esquema do MeshTracker Central (Incrementos 1 a 3), conforme docs/backlog.md.
-- R2, R3, R8 e o apelido único são garantidos aqui, por UNIQUE (ADR-002).
-- Times e classes não têm CHECK: são listas fixas no código (servicos.py),
-- para que trocá-las não mexa no modelo (backlog, dúvida 3).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS operador (
    id          INTEGER PRIMARY KEY,
    apelido     TEXT    NOT NULL UNIQUE COLLATE NOCASE
                CHECK (length(trim(apelido)) BETWEEN 1 AND 32),
    nome        TEXT    NOT NULL CHECK (length(trim(nome)) BETWEEN 1 AND 100),
    criado_em   TEXT    NOT NULL                     -- ISO 8601 em UTC
);

CREATE TABLE IF NOT EXISTS operacao (
    id          INTEGER PRIMARY KEY,
    nome        TEXT    NOT NULL CHECK (length(trim(nome)) BETWEEN 1 AND 100),
    data        TEXT    NOT NULL,                    -- AAAA-MM-DD
    local       TEXT    NOT NULL CHECK (length(trim(local)) BETWEEN 1 AND 100),
    situacao    TEXT    NOT NULL DEFAULT 'planejada'
                CHECK (situacao IN ('planejada', 'em_curso', 'encerrada')),
    centro_lat  REAL    NOT NULL CHECK (centro_lat BETWEEN -90 AND 90),
    centro_lon  REAL    NOT NULL CHECK (centro_lon BETWEEN -180 AND 180)
);

-- R6: só pode haver uma operação em curso por vez.
CREATE UNIQUE INDEX IF NOT EXISTS uma_operacao_em_curso
    ON operacao (situacao) WHERE situacao = 'em_curso';

CREATE TABLE IF NOT EXISTS inscricao (
    id             INTEGER PRIMARY KEY,
    operador_id    INTEGER NOT NULL REFERENCES operador (id),
    operacao_id    INTEGER NOT NULL REFERENCES operacao (id),
    time           TEXT    NOT NULL,
    classe         TEXT    NOT NULL,
    dispositivo    TEXT    NOT NULL CHECK (length(dispositivo) BETWEEN 1 AND 32),
    consentimento  INTEGER NOT NULL CHECK (consentimento = 1),   -- R5
    UNIQUE (operador_id, operacao_id),                            -- R2
    UNIQUE (operacao_id, dispositivo)                             -- R3
);

CREATE TABLE IF NOT EXISTS posicao (
    id            INTEGER PRIMARY KEY,
    inscricao_id  INTEGER NOT NULL REFERENCES inscricao (id),
    pacote        INTEGER NOT NULL CHECK (pacote >= 0),
    lat           REAL    NOT NULL CHECK (lat BETWEEN -90 AND 90),
    lon           REAL    NOT NULL CHECK (lon BETWEEN -180 AND 180),
    bateria       REAL    NOT NULL CHECK (bateria BETWEEN 0 AND 100),
    recebido_em   TEXT    NOT NULL,                  -- ISO 8601 em UTC
    UNIQUE (inscricao_id, pacote)                    -- R8
);

CREATE INDEX IF NOT EXISTS posicao_por_inscricao ON posicao (inscricao_id, id);

-- R7: só a origem e o motivo, sem a posição. operacao_id fica NULL quando
-- não havia operação em curso (acréscimo da demo, para contar por operação).
CREATE TABLE IF NOT EXISTS descarte (
    id           INTEGER PRIMARY KEY,
    operacao_id  INTEGER REFERENCES operacao (id),
    dispositivo  TEXT    NOT NULL,
    motivo       TEXT    NOT NULL CHECK (motivo IN ('sem_inscricao', 'sem_operacao_em_curso')),
    recebido_em  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS descarte_por_operacao ON descarte (operacao_id);

CREATE TABLE IF NOT EXISTS usuario (
    id          INTEGER PRIMARY KEY,
    login       TEXT    NOT NULL UNIQUE,
    senha_hash  TEXT    NOT NULL,
    papel       TEXT    NOT NULL CHECK (papel IN ('organizador', 'observador'))
);
