---
name: MeshTracker Central
description: Briefing de campo sobre papel suíço. Painel para inscrever operadores e acompanhar a operação de airsoft num mapa ao vivo.
colors:
  tinta: "#0b0b0b"
  tinta-2: "#4a4a46"
  chao: "#ecebe6"
  superficie: "#ffffff"
  superficie-2: "#f5f5f2"
  fio: "rgba(11, 11, 11, 0.16)"
  grade: "rgba(11, 11, 11, 0.06)"
  vermelho: "#d1242f"
  vermelho-fundo: "rgba(209, 36, 47, 0.06)"
  moldura: "#0b0b0b"
  moldura-tinta: "#f4f4f1"
  moldura-tinta-2: "#b9b9b3"
  escuro-chao: "#0c0d0d"
  escuro-superficie: "#151717"
  escuro-superficie-2: "#1c1f1f"
  escuro-tinta: "#ecebe6"
  escuro-tinta-2: "#a5a6a0"
  escuro-fio: "rgba(236, 235, 230, 0.16)"
  escuro-grade: "rgba(236, 235, 230, 0.05)"
  escuro-vermelho-texto: "#ff6b5e"
  estado-ativo: "#1a7f37"
  estado-atrasado: "#d4a72c"
  estado-perdido: "#d1242f"
  estado-sem-sinal: "#6e7781"
  time-azul: "#1f6feb"
  time-vermelho: "#d1242f"
  time-verde: "#1a7f37"
  time-amarelo: "#d4a72c"
typography:
  titulo:
    fontFamily: "Archivo, 'Segoe UI', system-ui, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "0.01em"
  secao:
    fontFamily: "Archivo, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "0.04em"
  numero:
    fontFamily: "Archivo, 'Segoe UI', system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 900
    lineHeight: 1
  corpo:
    fontFamily: "Archivo, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  rotulo:
    fontFamily: "Archivo, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.04em"
  dado:
    fontFamily: "'Chivo Mono', ui-monospace, Consolas, monospace"
    fontSize: "1rem"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  nenhum: "0px"
  circulo: "50%"
spacing:
  e1: "4px"
  e2: "8px"
  e3: "12px"
  e4: "16px"
  e5: "24px"
  e6: "32px"
  e7: "48px"
  e8: "64px"
components:
  botao-primario:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.superficie}"
    typography: "{typography.rotulo}"
    rounded: "{rounded.nenhum}"
    padding: "0 24px"
    height: "44px"
  botao-secundario:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    typography: "{typography.rotulo}"
    rounded: "{rounded.nenhum}"
    padding: "0 24px"
    height: "44px"
  campo:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    typography: "{typography.corpo}"
    rounded: "{rounded.nenhum}"
    padding: "0 12px"
    height: "44px"
  selo-ativo:
    backgroundColor: "{colors.estado-ativo}"
    textColor: "#ffffff"
    typography: "{typography.rotulo}"
    rounded: "{rounded.nenhum}"
    padding: "3px 8px 2px"
  selo-atrasado:
    backgroundColor: "{colors.estado-atrasado}"
    textColor: "{colors.tinta}"
    typography: "{typography.rotulo}"
    rounded: "{rounded.nenhum}"
    padding: "3px 8px 2px"
  selo-perdido:
    backgroundColor: "{colors.estado-perdido}"
    textColor: "#ffffff"
    typography: "{typography.rotulo}"
    rounded: "{rounded.nenhum}"
    padding: "3px 8px 2px"
  selo-sem-sinal:
    backgroundColor: "{colors.estado-sem-sinal}"
    textColor: "#ffffff"
    typography: "{typography.rotulo}"
    rounded: "{rounded.nenhum}"
    padding: "3px 8px 2px"
  moldura:
    backgroundColor: "{colors.moldura}"
    textColor: "{colors.moldura-tinta}"
    height: "56px"
    padding: "0 32px"
---

# Design System: MeshTracker Central

## Overview

**Creative North Star: "Briefing de campo sobre papel suíço"**

O app é uma ferramenta de trabalho (modo Operate): o organizador inscreve operadores e, durante a operação, olha o mapa a cada poucos segundos para saber quem está sem contato. A identidade vem de duas fontes. Da base suíça do deck vêm a tinta quase preta, um único vermelho, a grade de colunas visível, a Archivo e o motivo dos pontos dos operadores, em que o anel vazado é o perdido. Dos briefings táticos pré-missão vem só o vocabulário neutro do gênero: mapa como fundo, colchetes de alvo, réguas de coordenadas, retícula, carimbo de hora, blocos de dossiê e dado em fonte mono.

A identidade mora na moldura, nos cabeçalhos, no mapa e nos selos. Formulários, tabelas e mensagens de regra seguem previsíveis: controles padrão da web, texto de 16 px ou mais, contraste de 4,5:1 ou mais e foco visível. Todo número na tela vem do sistema. Nada é copiado de jogo nenhum: nem logo, nem fonte, nem tela, nem som. E não há armas, insígnias, patentes, caveiras nem brasões.

Decisão de tema, tomada pelo usuário em 08/11/2026: o padrão é o **modo Sistema**. Nele, as telas de trabalho seguem o esquema claro ou escuro do sistema e o mapa é sempre escuro. Com o sistema claro, o resultado é o híbrido escolhido nas prévias. Um seletor na moldura troca para **Claro** (tudo claro, mapa incluído) ou **Escuro** (tudo escuro). A escolha fica no `localStorage` do navegador.

**Key Characteristics:**
- moldura preta fixa, igual em todos os temas;
- cantos retos; o círculo é só do operador;
- colchetes de alvo como assinatura: no quadro do mapa, no dossiê e no operador perdido;
- cor de estado sempre acompanhada de texto e de forma;
- Archivo para ler e Chivo Mono para medir.

## Colors

A paleta é restrita: tinta, papel e um vermelho, mais as quatro cores de estado. A cor de verdade fica com o mapa e com os estados.

### Primary
- **Tinta** (#0b0b0b): texto, fios fortes, botão primário no claro e moldura. Sobre o chão, dá 16,5:1.
- **Vermelho de perda e recusa** (#d1242f): só no estado perdido, na recusa de regra e na bateria baixa. Branco sobre ele dá 5,24:1, e ele sobre o branco também. No escuro, o texto vermelho usa **#ff6b5e** (6,97:1 sobre o chão escuro), e o preenchimento continua #d1242f.

### Neutral
| Token | Claro | Escuro | Papel | Contraste do texto |
|---|---|---|---|---|
| chão | #ecebe6 | #0c0d0d | fundo da página, com a textura de grade | tinta 16,5:1 · 16,3:1 |
| superfície | #ffffff | #151717 | tabelas, blocos, campos | tinta 19,7:1 · 15,2:1 |
| superfície 2 | #f5f5f2 | #1c1f1f | cabeçalho de tabela, hover | tinta 18,0:1 · 13,9:1 |
| tinta 2 | #4a4a46 | #a5a6a0 | rótulos, metadados, texto secundário | 8,2 a 8,9:1 · 6,8 a 7,9:1 |
| fio | tinta a 16% | tinta a 16% | divisórias finas | (não é texto) |
| grade | tinta a 6% | tinta a 5% | textura de colunas e quadrícula | (não é texto) |
| moldura | #0b0b0b | #0b0b0b | barra do topo, igual nos dois | #f4f4f1 17,9:1, #b9b9b3 10,0:1 |

### Estados do operador (a mesma tabela no mapa, na lista, no deck e aqui)
| Estado | Regra (R9) | Cor | Texto sobre a cor | Forma no mapa | Selo |
|---|---|---|---|---|---|
| Ativo | até 60 s | #1a7f37 | #ffffff (5,08:1) | anel cheio | "Ativo", com ponto cheio |
| Atrasado | de 60 a 120 s | #d4a72c | #0b0b0b (8,78:1) | anel tracejado | "Atrasado", com ponto cheio |
| Perdido | acima de 120 s | #d1242f | #ffffff (5,24:1) | anel vazado com colchetes de alvo | "Perdido", com anel vazado |
| Sem sinal | nunca recebeu | #6e7781 | #ffffff (4,55:1) | não aparece no mapa | "Sem sinal", com ponto cheio |

O anel sobre o mapa escuro tem pelo menos 3,26:1 (perdido) e 3,37:1 (ativo). No mapa claro, o anel ganha um contorno de 1,5 px na cor da tinta, porque o âmbar sobre o cinza claro dá só 1,58:1.

### Times (dado do servidor)
As cores dos times vêm de `servicos.TIMES` e chegam pela API no campo `cor`: Azul #1f6feb, Vermelho #d1242f, Verde #1a7f37 e Amarelo #d4a72c. Elas aparecem só na seta do marcador e na amostra quadrada ao lado do nome do time, nunca em fundo, borda ou texto. O time Vermelho tem o mesmo tom do perdido, e o Verde e o Amarelo têm os tons de ativo e atrasado. Por isso o estado nunca depende só da cor: ele tem anel, forma e texto.

### Named Rules
**A Regra do Vermelho Único.** Vermelho só para perda (operador perdido, bateria abaixo de 20%) e recusa (mensagem de regra). Nunca em botão, link, título ou enfeite.

**A Regra do Mapa Escuro.** No modo Sistema, a tela do mapa é sempre escura, mesmo com o sistema claro. Só o seletor em "Claro" deixa o mapa claro.

**A Regra do Dado Real.** Todo número, coordenada e hora na tela vem do sistema: a API, o banco ou o relógio do navegador no carimbo de atualização. As réguas e a retícula são calculadas a partir do mapa e do centro da operação. Nada de rumo, código ou contagem inventados para enfeitar.

## Typography

**Fonte de interface:** Archivo (variável, pesos 100 a 900), com 'Segoe UI', system-ui e sans-serif como reserva.
**Fonte de dado:** Chivo Mono (variável, pesos 100 a 900), com ui-monospace e Consolas como reserva.

**Character:** a Archivo é a grotesca do deck suíço e carrega títulos, números grandes e texto. A Chivo Mono é da mesma fundição (Omnibus-Type), então os dois desenhos conversam. A mono serve só para medir: coordenada, dispositivo, tempo, bateria, hora e login.

As duas fontes ficam em `src/static/vendor/fonts/` (subconjunto latin, woff2) e são licenciadas pela SIL OFL 1.1, com a origem registrada em `src/static/vendor/ORIGEM.md`. A CSP do app não deixa carregar o Google Fonts.

### Hierarchy
- **Título** (900, 2.25rem/36px, altura de linha 1, caixa alta por CSS): o nome da página, com o efeito de digitação.
- **Seção** (800, 1.25rem/20px, 1.2, caixa alta, espaçamento 0.04em): títulos de bloco ("Inscritos", "Inscrever operador").
- **Número** (900, 2rem/32px, 1, `tabular-nums`): contagem por estado na faixa do mapa.
- **Corpo** (400, 1rem/16px, 1.5): texto, células de tabela e opções. Prosa com no máximo 70ch.
- **Rótulo** (700, 1rem/16px, 1.2, caixa alta, espaçamento 0.04em): rótulo de campo, cabeçalho de tabela, rótulo do dossiê e texto do selo.
- **Dado** (Chivo Mono 500, 1rem/16px, 1.4, `tabular-nums`): MT-01, −15,7990, 2 min 10 s, 73%, 21:39:36.

### Named Rules
**A Regra dos 16 px.** Nenhum texto do app fica abaixo de 1rem. A única exceção é a atribuição do OpenStreetMap (0.75rem), que é crédito obrigatório e não é conteúdo.

**A Regra da Mono que Mede.** Mono só em dado medido ou identificador. Rótulo, botão e título nunca usam mono.

## Layout

- **Grade:** a textura do chão mostra colunas de 160 px e uma quadrícula de 32 px, nas cores `grade`, sem dado. Ela é um fundo, não uma grade de encaixe.
- **Espaçamento:** a escala e1 a e8 (4, 8, 12, 16, 24, 32, 48 e 64 px). O espaço acima de um título de seção é maior que o espaço abaixo dele.
- **Moldura:** 56 px de altura, no topo da página (rola junto com ela), com 32 px de margem lateral.
- **Página comum** (`/operadores`, `/operacoes`, `/operacoes/<id>`): conteúdo de até 1280 px, centralizado, com 32 px de margem. A partir de 1024 px, a tabela fica à esquerda (flexível) e o formulário à direita (400 px). Abaixo de 1024 px, eles se empilham, com a tabela primeiro.
- **Mapa** (`/operacoes/<id>/mapa`): largura total, com 32 px de margem. Por cima vem o cabeçalho (título, data, local e situação) e, logo abaixo, a faixa de dossiê com a contagem. Depois vêm o mapa (flexível) e a lista (580 px), lado a lado a partir de 1024 px. A altura do mapa é a da janela menos a moldura, o cabeçalho e a faixa, com mínimo de 420 px. Abaixo de 1024 px, a lista desce para baixo do mapa, que fica com 55vh (mínimo de 300 px).
- **Login:** um bloco de 28rem centralizado no chão com a grade.
- **Celular (até 719 px):** a moldura vira duas linhas (marca e Sair em cima; menu e seletor de tema embaixo), a faixa de contagem quebra em 3 + 3, e as tabelas rolam na horizontal dentro do próprio bloco, sem rolar a página.
- **Pontos de quebra:** 720 px e 1024 px.

## Elevation & Depth

Não há sombras. A profundidade vem de tom e de fio: o chão fica atrás, a superfície fica sobre ele com um fio de 1 px na cor da tinta, e o cabeçalho de tabela usa a superfície 2. As sobreposições do mapa (carimbo, réguas e rótulos) usam a superfície com 90 a 94% de opacidade e um fio de 1 px.

### Named Rules
**A Regra do Plano.** Nada flutua. Se algo precisa se destacar, ganha fio forte, colchete ou cor de estado, nunca sombra ou desfoque.

## Shapes

Os cantos são retos (raio 0) em tudo: botão, campo, bloco, selo e tabela. O círculo aparece só no operador: o anel do marcador, o ponto do selo e o motivo dos pontos da marca. Os colchetes de alvo são quatro cantos em L, com 18 px de braço e 2 px de traço (12 px e 3 px no marcador perdido), desenhados com gradientes em CSS, sem imagem.

## Components

### Moldura e menu
- **Faixa preta** (#0b0b0b), igual em todos os temas, com fio inferior de 1 px a 14% de opacidade.
- **Marca:** o motivo dos pontos (quatro pontos cheios e o anel vazado, em #f4f4f1, sem vermelho), seguido de "MeshTracker" (Archivo 900) e "Central" (Archivo 500), em caixa alta.
- **Menu:** Operadores e Operações, em Rótulo, cor #b9b9b3. No hover, o texto fica #f4f4f1. A página atual tem `aria-current="page"`, texto #f4f4f1 e sublinhado de 2 px.
- **Sessão:** o login e o papel em mono #b9b9b3 e o botão Sair com contorno claro. Sair é o único formulário que o observador vê.
- **Seletor de tema:** três botões (Sistema, Claro e Escuro), sem formulário e com `aria-pressed`. Vem de `static/js/tema.js`, que aplica `data-tema` no `<html>` antes de pintar a página e guarda a escolha no `localStorage`, dentro de try/catch. Sem JS, os botões ficam escondidos e vale o modo Sistema pelo CSS.

### Botões
- **Forma:** cantos retos, 44 px de altura, 0 e 24 px de padding, texto em Rótulo e caixa alta.
- **Primário:** fundo tinta e texto superfície (no escuro, o inverso). Usado em Inscrever, Cadastrar, Criar, Entrar, Iniciar operação e Encerrar operação.
- **Secundário:** fundo transparente e contorno de 2 px na tinta. Usado em Abrir mapa e Salvar.
- **Hover:** o primário clareia um pouco e o secundário ganha fundo superfície 2. **Foco:** contorno de 2 px na cor da tinta, afastado 2 px. **Desabilitado:** 40% de opacidade e cursor padrão.
- **Link de ação na tabela** ("Alterar"): texto sublinhado, sem caixa. Ele abre o `<details>` da linha.

### Campos, select e checkbox
- **Campo e select:** 44 px de altura, fundo superfície, contorno de 1 px na tinta 2, cantos retos e texto Corpo. O dispositivo usa a fonte de dado. O select tem uma seta desenhada em CSS.
- **Rótulo:** acima do campo, em Rótulo e tinta 2, ligado pelo `<label>`.
- **Foco:** contorno de 2 px na tinta, sem afastamento.
- **Checkbox:** 22 px, com `accent-color` na tinta e o texto ao lado em Corpo.
- **Erro de regra:** a mensagem aparece no topo do formulário (veja Mensagem de regra), e os valores digitados continuam nos campos.

### Tabela
- Fundo superfície, cabeçalho em superfície 2 com Rótulo em tinta 2 e fio inferior de 2 px na tinta. Linhas com fio de 1 px e células com 10 px de padding.
- A primeira coluna (o apelido) é `<th scope="row">` em peso 700. Os números ficam alinhados à direita, na fonte de dado.
- A linha do perdido tem fundo vermelho a 9% (16% no escuro), e a do atrasado, âmbar a 14% (12% no escuro). O estado continua no selo.

### Mensagem de regra
- **Recusa** (categoria `erro`, `role="alert"`): bloco com fio de 1 px vermelho e fundo vermelho a 6%. À esquerda, uma etiqueta "Recusa" no estilo do selo perdido (fundo vermelho, texto branco). À direita, a mensagem do servidor em Corpo na cor da tinta. A página volta com status 400.
- **Feito** (categoria `sucesso`, `role="status"`): o mesmo bloco com fio na tinta e etiqueta "Feito" no estilo do selo ativo.
- **Aviso** (categoria `aviso` e falha de atualização do mapa): o mesmo bloco com fio na tinta e etiqueta "Aviso" no estilo do selo atrasado.

### Selo de estado e selo de situação
- **Selo de estado:** retângulo com o texto em Rótulo, um marcador de 8 px antes dele (ponto cheio, ou anel vazado no perdido) e as cores da tabela de estados.
- **Selo de situação da operação:** "Planejada" com contorno de 2 px na tinta e fundo transparente; "Em curso" com fundo tinta e texto chão; "Encerrada" com contorno de 2 px na tinta 2 e texto tinta 2.

### Bloco de dossiê (página da operação)
- Superfície com fio de 1 px, 24 px de padding e colchetes de alvo 9 px para fora.
- Itens, só com dados reais: Data, Local, Situação (o selo), Centro (latitude e longitude com 4 casas, na fonte de dado) e Inscritos (o total). Cada item tem o Rótulo em cima e o valor embaixo (Archivo 700 1.25rem, ou dado 1.125rem).
- As ações ficam no canto direito: o botão de transição (só o organizador vê) e Abrir mapa.
- "Ordens e objetivos" estão fora do MVP (`docs/backlog.md`), então o app não tem lista de objetivos.

### Faixa de dossiê (mapa)
- Uma linha de células com fio entre elas: Perdidos, Atrasados, Ativos, Sem sinal e Descartados. Cada célula tem o Rótulo e, embaixo, o Número, com o marcador do estado antes dele. O número de perdidos usa o vermelho de texto. No fim, alinhada à direita, fica a célula Inscritos.
- Os números são contados no navegador a partir da mesma resposta de `/api/v1/situacao` que desenha o mapa. Eles mudam sem animação.

### Marcador do mapa
- **Anel** de 36 px e 4 px de borda na cor do estado: cheio no ativo, tracejado no atrasado e vazado (sem fundo) no perdido. No ativo e no atrasado, o fundo é a superfície a 90%. No mapa claro, o anel tem contorno de 1,5 px na tinta.
- **Seta** de 22 px na cor do time, girada pelo `rumo` (sem giro quando o rumo é nulo), com traço de 1,5 px no contraste do fundo. No perdido, a seta fica com 55% de opacidade, porque é a última direção conhecida.
- **Rótulo:** o apelido em mono, caixa alta e 1rem, numa etiqueta superfície com fio. No perdido, a etiqueta é vermelha com texto branco e diz "Coruja · perdido há 2 min 10 s", com o tempo vindo de `segundos`.
- **Colchetes de alvo** vermelhos em volta do perdido. O perdido fica acima dos outros (`zIndexOffset`).
- Todo texto entra por `textContent`. A cor do time passa pela validação de hex de `corSegura`.

### Quadro do mapa (réguas, retícula, carimbo)
- **Quadro:** fio de 1 px na tinta e colchetes de alvo em volta.
- **Réguas:** uma faixa de 26 px no topo (longitude) e outra à esquerda (latitude), com tracinhos a cada 0,0005° e números a cada 0,001° (três casas, vírgula decimal). Tudo é recalculado do próprio mapa em `move` e `zoom`.
- **Retícula:** uma cruz de 56 px no centro da operação (`centro_lat` e `centro_lon`), a 55% de opacidade, sem texto.
- **Carimbo:** canto superior esquerdo, com "Atualizado às 21:39:36" em dado. É o mesmo `#atualizacao` de hoje, com `aria-live="polite"`.
- **Escala métrica** do Leaflet (`L.control.scale`, sem milhas) no canto inferior esquerdo, e o zoom no canto superior direito, com cantos retos.
- **Tiles do OpenStreetMap filtrados no painel de tiles**, sem trocar de provedor nem mexer na CSP. No claro: `grayscale(1) contrast(.92) brightness(1.04)`. No escuro: `grayscale(1) invert(1) brightness(.78) contrast(1.15)`. Sem internet, o fundo fica liso (claro #d9d9d4, escuro #1a1c1c), e os marcadores, a lista e a faixa continuam funcionando.

### Lista lateral (mapa)
- A Tabela com Operador, Time, Estado, Último sinal e Bateria, ordenada por prioridade (perdido, atrasado, sem sinal, ativo; depois pelo apelido), como hoje.
- A bateria abaixo de 20% fica em vermelho de texto, peso 700.
- Abaixo da tabela, uma nota em tinta 2: "Sinais de dispositivos não inscritos são descartados e só contados."

### Título que aparece como digitado
- Só no `<h1>`, nunca em dado que muda. É feito só com CSS: `clip-path` de `inset(0 100% 0 0)` até `inset(0)`, em 450 ms com `steps(16)`.
- Fica desligado com `prefers-reduced-motion: reduce`. O texto inteiro está no HTML desde o início, então leitores de tela não esperam.

### Movimento
- **Transições de estado:** 150 a 200 ms, `ease-out`, só na cor de fundo e na borda (hover e foco).
- **Mapa:** os marcadores mudam de posição sem animação a cada 3 s. Nenhuma varredura ou "troca de câmera" no app; elas ficam para o deck.

### O que vem do Pico e o que é próprio
- **Padrão:** o Pico continua como base de reset e de formulário, com as variáveis dele (`--pico-*`) redefinidas a partir dos tokens acima: fonte, cores, raio 0, espaçamentos e foco. São próprios: a moldura, os selos, o dossiê, a faixa, a tabela, as mensagens, o seletor de tema e tudo no mapa.
- **Se quem implementar decidir tirar o Pico:** registre aqui a decisão e garanta estilo próprio para todo elemento usado (`button`, `input`, `select`, `checkbox`, `details`/`summary`, `table`, `label`, `a[role=button]`, `hgroup`), além de devolver aos controles do Leaflet o visual descrito acima.

## Do's and Don'ts

### Do:
- **Do** ponha o texto do estado ao lado de toda cor de estado, no selo, no rótulo do perdido e na faixa.
- **Do** use os colchetes de alvo só no quadro do mapa, no dossiê da operação e no operador perdido.
- **Do** use a fonte de dado em todo valor medido: coordenada, dispositivo, tempo, bateria e hora.
- **Do** confira 4,5:1 para texto e 3:1 para anel e ícone, nos dois temas.
- **Do** mantenha a moldura preta e a mesma em todos os temas.

### Don't:
- **Don't** use vermelho fora de perda e recusa (Regra do Vermelho Único).
- **Don't** invente dado para enfeitar: nada de rumo, código de missão, contagem ou coordenada que o sistema não mandou.
- **Don't** use armas, insígnias, patentes, caveiras, brasões, nem logo, fonte, tela ou som de jogo.
- **Don't** anime dado que se atualiza a cada 3 s, nem use varredura ou digitação fora do título.
- **Don't** use sombra, desfoque, gradiente em texto ou canto arredondado.
- **Don't** ponha texto abaixo de 16 px (fora a atribuição do OpenStreetMap).

## Como levar para o Figma

1. **Fontes:** instale a Archivo e a Chivo Mono no computador (as duas estão no Google Fonts) antes de abrir o arquivo.
2. **Coleção "Primitivas"** (um modo só): crie uma variável de cor para cada hex do frontmatter (`tinta`, `vermelho`, `estado-ativo`...) e variáveis de número para `spacing` (e1 a e8) e `rounded`.
3. **Coleção "Tema"**, com dois modos, **Claro** e **Escuro**. Cada variável aponta para uma primitiva:

| Variável | Claro | Escuro |
|---|---|---|
| tema/chao | chao | escuro-chao |
| tema/superficie | superficie | escuro-superficie |
| tema/superficie-2 | superficie-2 | escuro-superficie-2 |
| tema/tinta | tinta | escuro-tinta |
| tema/tinta-2 | tinta-2 | escuro-tinta-2 |
| tema/fio | fio | escuro-fio |
| tema/vermelho-texto | vermelho | escuro-vermelho-texto |
| tema/botao | tinta | escuro-tinta |
| tema/botao-texto | superficie | tinta |

   As cores de estado, de time e da moldura ficam fora dessa coleção, porque não mudam com o tema. Para ver o modo Sistema, ponha os frames do mapa no modo Escuro e os das outras telas no modo do sistema (o híbrido é a tela do mapa no Escuro e as outras no Claro).
4. **Estilos de texto:** Título, Seção, Número, Corpo, Rótulo e Dado, com os valores de `typography`. Rótulo, Seção e Título usam caixa alta no próprio estilo.
5. **Componentes:** Botão (primário e secundário, com os estados padrão, hover, foco e desabilitado), Campo, Select, Checkbox, Selo de estado (4 variantes), Selo de situação (3), Mensagem (Recusa, Feito, Aviso), Linha de tabela (normal, atrasado, perdido), Marcador (ativo, atrasado, perdido), Colchetes de alvo, Faixa de dossiê e Moldura (com o seletor de tema).
6. **Prints de referência:** os prints de cada tela, para organizador e observador, em 1440×900 e 390×844, ficam em `docs/design/telas/`. Importe-os como camadas travadas embaixo dos frames.
7. **De volta ao código:** o que mudar no Figma volta como pedido à parte. Atualize primeiro este arquivo (tokens e regras) e depois o CSS.
