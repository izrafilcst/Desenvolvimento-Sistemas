# Origem das bibliotecas da apresentação

Copiadas para os slides não dependerem de CDN na sala. Para conferir: `sha256sum <arquivo>`.

| Arquivo | Biblioteca | Versão | Origem | SHA-256 | Licença |
|---|---|---|---|---|---|
| `motion.js` | Motion (antigo Framer Motion), build UMD, global `Motion` | 14.3.1 | https://cdn.jsdelivr.net/npm/motion@14.3.1/dist/motion.js | `914091f25c647b682ad08254cb263b298a6234b23a5c7a92b9dfe6029150e969` | MIT |
| `fonts/archivo-latin.woff2` | Archivo, fonte variável (eixo de peso), subconjunto latin; o deck usa os pesos 800 e 900 | v25 | https://fonts.gstatic.com/s/archivo/v25/k3kPo8UDI-1M0wlSV9XAw6lQkqWY8Q82sLydOxI.woff2 (indicada pelo CSS de `https://fonts.googleapis.com/css2?family=Archivo:wght@800;900`) | `8f704806dbedeaaeca334b11ec348bc3ac3a439d6431544b3afb54f534ee4967` | SIL OFL 1.1 |
| `fonts/nunito-latin.woff2` | Nunito, fonte variável (eixo de peso), subconjunto latin; o deck usa os pesos 400, 600 e 700 | v32 | https://fonts.gstatic.com/s/nunito/v32/XRXV3I6Li01BKofINeaB.woff2 (indicada pelo CSS de `https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700`) | `ba344451eab25b217a165363b1982048a5e5830a0daf36577973955a04cac793` | SIL OFL 1.1 |
| `fonts/chivo-mono-latin.woff2` | Chivo Mono, fonte variável (eixo de peso 100 a 900), subconjunto latin; o deck de teste `slides-briefing.html` usa só em dado (código de regra, dispositivo, data, contagem) | v11 | https://fonts.gstatic.com/s/chivomono/v11/mFT0WbgRxKvF_Z5eQMO9gx8D1Q.woff2 (a mesma cópia de `src/static/vendor/fonts/`, registrada em `src/static/vendor/ORIGEM.md`) | `c00775f8ecb034b6c193c7b253d698cfe882a1d6c0df67299a3d5382c2e82216` | SIL OFL 1.1 |
