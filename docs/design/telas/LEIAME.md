# Prints das telas (para o Figma)

Gerado em 08/11/2026, a partir do commit `fe538cd` (`git rev-parse --short HEAD`).

Os dados vêm do seed (`src/demo_seed.py`) e do simulador (`src/simulador.py`). Os sinais são simulados: o Coruja (MT-03) para de enviar de propósito para aparecer como perdido no mapa.

Os prints saíram com a barra de rolagem escondida, então a largura do PNG é exatamente a da janela: 1440 ou 390 px. A altura é a da página inteira e varia de arquivo para arquivo. O fundo do deck tem 1920×1080.

## O que cada arquivo mostra

- `login-1440.png`, `login-390.png`: tela de entrada, sem papel.
- `organizador-operadores-*.png`, `observador-operadores-*.png`: lista de operadores.
- `organizador-operacoes-*.png`, `observador-operacoes-*.png`: lista de operações (Alfa encerrada, Bravo em curso, Charlie planejada).
- `organizador-operacao-bravo-*.png`, `observador-operacao-bravo-*.png`: dossiê e inscritos da Bravo, com o formulário de inscrição (só o organizador inscreve).
- `organizador-operacao-charlie-*.png`, `observador-operacao-charlie-*.png`: operação planejada e sem inscritos.
- `organizador-operacao-recusa-1440.png`: recusa de inscrição duplicada (Falcão já inscrito na Bravo).
- `organizador-mapa-*.png`, `observador-mapa-*.png`: mapa da Bravo, com situação dos operadores (Coruja perdido, demais ativos).
- `organizador-mapa-claro-1440.png`, `organizador-mapa-escuro-1440.png`: mesmo mapa nos temas Claro e Escuro.
- `fundo-mapa-parque-1920x1080.png`: só o mapa, em tela cheia, no tema Escuro, sem marcadores, réguas, retícula, carimbo nem zoom. Mantém a atribuição "© OpenStreetMap" e a escala. Serve de fundo do deck.

## Como importar no Figma

1. Arraste os PNG para a página do Figma.
2. Crie um frame da largura exata do print: 1440 ou 390 px. A altura do frame é a do próprio print (página inteira). O fundo do deck vai em frame de 1920×1080.
3. Coloque o print dentro do frame e trave a camada, deixando-a embaixo do conteúdo.

## Tokens e componentes

Os tokens de cor, tipografia e espaçamento, e os componentes, estão no `DESIGN.md`, na seção "Como levar para o Figma".
