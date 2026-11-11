# Origem das bibliotecas de front-end

Arquivos copiados para o projeto não depender de CDN (ADR-002). Para conferir: sha256sum <arquivo>.

Caminhos relativos a `src/static/vendor`. Os arquivos foram baixados com `curl -fsSL` em 2026-11-08.

| Arquivo | Biblioteca | Versão | URL de origem | SHA-256 | Licença |
|---|---|---|---|---|---|
| `leaflet/leaflet.js` | Leaflet | 1.9.4 | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js | db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a | BSD-2-Clause |
| `leaflet/leaflet.css` | Leaflet | 1.9.4 | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css | a7837102824184820dfa198d1ebcd109ff6d0ff9a2672a074b9a1b4d147d04c6 | BSD-2-Clause |
| `leaflet/images/marker-icon.png` | Leaflet | 1.9.4 | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png | 574c3a5cca85f4114085b6841596d62f00d7c892c7b03f28cbfa301deb1dc437 | BSD-2-Clause |
| `leaflet/images/marker-icon-2x.png` | Leaflet | 1.9.4 | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png | 00179c4c1ee830d3a108412ae0d294f55776cfeb085c60129a39aa6fc4ae2528 | BSD-2-Clause |
| `leaflet/images/marker-shadow.png` | Leaflet | 1.9.4 | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png | 264f5c640339f042dd729062cfc04c17f8ea0f29882b538e3848ed8f10edb4da | BSD-2-Clause |
| `leaflet/images/layers.png` | Leaflet | 1.9.4 | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/layers.png | 1dbbe9d028e292f36fcba8f8b3a28d5e8932754fc2215b9ac69e4cdecf5107c6 | BSD-2-Clause |
| `leaflet/images/layers-2x.png` | Leaflet | 1.9.4 | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/layers-2x.png | 066daca850d8ffbef007af00b06eac0015728dee279c51f3cb6c716df7c42edf | BSD-2-Clause |
| `fonts/archivo-latin.woff2` | Archivo, fonte variável (eixo de peso 100 a 900), subconjunto latin | v25 | https://fonts.gstatic.com/s/archivo/v25/k3kPo8UDI-1M0wlSV9XAw6lQkqWY8Q82sLydOxI.woff2 (a mesma cópia de `docs/apresentacao/vendor/fonts/`) | 8f704806dbedeaaeca334b11ec348bc3ac3a439d6431544b3afb54f534ee4967 | SIL OFL 1.1 |
| `fonts/chivo-mono-latin.woff2` | Chivo Mono, fonte variável (eixo de peso 100 a 900), subconjunto latin | v11 | https://fonts.gstatic.com/s/chivomono/v11/mFT0WbgRxKvF_Z5eQMO9gx8D1Q.woff2 | c00775f8ecb034b6c193c7b253d698cfe882a1d6c0df67299a3d5382c2e82216 | SIL OFL 1.1 |

Observação: a pasta `leaflet/images/` precisa ficar ao lado de `leaflet/leaflet.css`, porque o CSS aponta para ela por caminho relativo.

A Archivo (interface) e a Chivo Mono (dado medido) são as fontes do app desde a fase 2. A CSP do app não deixa carregar o Google Fonts, por isso as duas ficam aqui, em `fonts/`, e o `app.css` as declara com `@font-face`.

O Pico CSS (2.1.1, MIT) saiu na fase 2: o `app.css` traz a base própria (reset, formulário, tabela), e a decisão está no `DESIGN.md`.
