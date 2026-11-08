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
| `pico/pico.min.css` | Pico CSS | 2.1.1 | https://unpkg.com/@picocss/pico@2.1.1/css/pico.min.css | fbc9a63fc9fc9f72d12fd7fc9806e11fa9f77ae4f9cad146b27003a1119ba3db | MIT |

Observação: a pasta `leaflet/images/` precisa ficar ao lado de `leaflet/leaflet.css`, porque o CSS aponta para ela por caminho relativo.
