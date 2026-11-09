# Prints das telas (para o Figma e o deck)

Gerado em 09/11/2026, a partir do commit `738e8f8` (`git rev-parse --short HEAD`).

Os dados vêm do seed (`src/demo_seed.py`) e do simulador (`src/simulador.py`). Os sinais são simulados: o Coruja (MT-03) para de enviar de propósito para aparecer como perdido no mapa. A Charlie aparece com cinco inscritos, que o organizador fez pelo formulário.

Os prints saíram com a barra de rolagem escondida, então a largura do PNG é exatamente a da janela: 1440 ou 390 px. A altura é a da página inteira e varia de arquivo para arquivo. O fundo do deck tem 1920×1080.

## O que cada arquivo mostra

- `login-1440.png`, `login-390.png`: tela de entrada, sem papel.
- `organizador-operadores-*.png`, `observador-operadores-*.png`: lista de operadores.
- `organizador-operacoes-*.png`, `observador-operacoes-*.png`: lista de operações (Alfa encerrada, Bravo em curso, Charlie planejada).
- `organizador-operacao-bravo-*.png`, `observador-operacao-bravo-*.png`: dossiê e inscritos da Bravo. O organizador vê o formulário de inscrição e o botão Encerrar; o observador vê só leitura, sem formulário.
- `organizador-operacao-charlie-*.png`, `observador-operacao-charlie-*.png`: operação planejada e sem inscritos.
- `organizador-operacao-charlie-inscritos-1440.png`: a Charlie com os cinco inscritos (Coruja, Falcão, Lobo, Pantera, Raposa), feitos pelo organizador.
- `organizador-operacao-recusa-1440.png`: recusa de inscrição duplicada (Falcão já inscrito na Bravo). A opção do Falcão vem desabilitada no seletor; para mostrar a recusa do servidor, o teste reabilitou essa opção na página antes do envio.
- `organizador-mapa-*.png`, `observador-mapa-*.png`: mapa da Bravo, com a situação dos operadores (Coruja perdido, demais ativos).
- `organizador-mapa-claro-1440.png`, `organizador-mapa-escuro-1440.png`: mesmo mapa nos temas Claro e Escuro.
- `fundo-mapa-parque-1920x1080.png`: só o mapa, em tela cheia, no tema Escuro, sem marcadores, réguas, retícula, carimbo nem zoom. Mantém a atribuição "© OpenStreetMap" e a escala. Serve de fundo do deck.

## Recortes de prova (`recortes/`)

Recortes de elemento ou de região, em escala 1:1 (pixel CSS, sem `deviceScaleFactor` 2), para o projetor.

- `h1-charlie-inscritos.png` (848×342): o bloco de inscritos da Charlie com os cinco.
- `h2-faixa.png` (1376×78): a faixa de contagem do mapa da Bravo (Perdidos, Atrasados, Ativos, Sem sinal, Descartados, Inscritos).
- `h2-coruja.png` (640×400): região do mapa em volta da Coruja perdida, com colchetes e rótulo, no zoom 17.
- `h3-observador.png` (1440×328): topo da Bravo como observador, com a moldura, "Somente leitura" e o dossiê, sem formulário.

## Como importar no Figma

1. Arraste os PNG para a página do Figma.
2. Crie um frame da largura exata do print: 1440 ou 390 px. A altura do frame é a do próprio print (página inteira). O fundo do deck vai em frame de 1920×1080.
3. Coloque o print dentro do frame e trave a camada, deixando-a embaixo do conteúdo.

## Tokens e componentes

Os tokens de cor, tipografia e espaçamento, e os componentes, estão no `DESIGN.md`, na seção "Como levar para o Figma".
