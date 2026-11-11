---
version: 1
slug: "src-templates-base-html"
primary_target: "src/templates/base.html"
related_targets: ["src/templates/mapa.html","src/templates/operacao.html","src/templates/operacoes.html","src/templates/operadores.html","src/templates/login.html"]
---

# Telas do app (Operate)

Escopo: /login, /operadores, /operacoes, /operacoes/<id>, /operacoes/<id>/mapa. Modo Operate. Público: o organizador num notebook em campo e o observador só leitura. Tarefas: inscrever 5 operadores em até 3 min (H1) e apontar o perdido em até 10 s (H2). Restrições: CSP self, sem build, sem dependência nova, testes de HTML verdes. Direção fixada pelo brief do usuário (briefing tático sobre a base suíça), sem rolagem de conceito. Tema: modo Sistema por padrão (mapa sempre escuro, as outras telas seguem o sistema), com seletor Claro e Escuro.

## Direction contract

THESIS: a tela é um quadro de situação, não um painel de cartões; recusa o dashboard cinza com cartões de métrica.
OWN-WORLD: tinta #0b0b0b, papel #ecebe6/#ffffff, um vermelho #d1242f só para perda e recusa, estados #1a7f37/#d4a72c/#d1242f/#6e7781; Archivo e Chivo Mono; cantos retos; colchetes de alvo; réguas de coordenadas; grade de 160 px.
STORY: o organizador vê de imediato quem está perdido e há quanto tempo, e inscreve sem redigitar; recusas aparecem no próprio formulário.
FIRST VIEWPORT: no mapa, moldura preta; título digitado com data, local e situação; faixa com Perdidos, Atrasados, Ativos, Sem sinal, Descartados e Inscritos; mapa escuro com colchetes, réguas, retícula e carimbo à esquerda; lista de 580 px à direita com o perdido no topo.
FORM: briefing tático sobre papel suíço, fixado pelo usuário (1 de 1); seed: none (unavailable)
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
