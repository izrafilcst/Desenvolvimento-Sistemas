/* Mapa ao vivo (US06). Busca /api/v1/situacao a cada 3 s e desenha marcadores, lista e faixa de dossiê.
 * Todo texto vindo do servidor entra por textContent ou setAttribute, nunca por innerHTML.
 * Réguas, retícula e contagens são calculadas aqui, do próprio mapa e da mesma resposta da API. */
(function () {
  'use strict';

  const raiz = document.getElementById('mapa-pagina');
  if (!raiz) { return; }

  const INTERVALO_MS = 3000;
  const TEMPO_LIMITE_MS = 5000;
  const NS_SVG = 'http://www.w3.org/2000/svg';
  const CENTRO_PADRAO = [-15.7939, -47.8828];
  const COR_PADRAO = '#6e7781';
  const ROTULO = { ativo: 'Ativo', atrasado: 'Atrasado', perdido: 'Perdido', sem_sinal: 'Sem sinal' };
  // Quem precisa de atenção primeiro: perdido, atrasado (H2), sem sinal, ativo.
  const PRIORIDADE = { perdido: 0, atrasado: 1, sem_sinal: 2, ativo: 3 };
  const PESO_Z = { perdido: 1000, atrasado: 500, sem_sinal: 0, ativo: 0 };
  const ESPESSURA_REGUA = 26;       // px: faixa das réguas no topo e à esquerda
  const PX_ENTRE_NUMEROS = 96;      // px mínimos entre dois números de uma régua
  const MILESIMO = 0.001;           // grau: os números das réguas são múltiplos dele
  const ZOOM_MINIMO = 15;           // a operação tem uns 300 m de raio; no nível 15 já cabem uns 2,5 km
  const ZOOM_DOS_ROTULOS = 17;      // abaixo dele só o perdido e o atrasado levam rótulo
  const PECAS_FIXAS = '.carimbo, .leaflet-control-zoom, .leaflet-control-scale, .leaflet-control-attribution';   // os rótulos não as cobrem

  const aviso = document.getElementById('aviso');
  const atualizacao = document.getElementById('atualizacao');
  const descartados = document.getElementById('descartados');
  const resumoDeSituacao = document.getElementById('situacao-status');   // região de status só para leitor de tela
  const lista = document.getElementById('lista');
  const urlSituacao = raiz.dataset.urlSituacao + '?operacao=' + encodeURIComponent(raiz.dataset.operacaoId);

  const marcadores = new Map();   // inscricao_id -> { marcador, partes }
  let mapa = null;
  let centroOperacao = CENTRO_PADRAO;
  let reguas = null;              // { topo, esq, reticula }, só existe com o Leaflet carregado
  let ajustouVista = false;
  let emAndamento = false;
  let horaDaUltima = null;
  let avisoDoMapa = '';   // problema que não some a cada atualização
  let ultimoResumo = null;   // o que a região de status disse por último

  // ---------------------------------------------------------------- apoio

  function el(tag, classe, texto) {
    const elemento = document.createElement(tag);
    if (classe) { elemento.className = classe; }
    if (texto !== undefined) { elemento.textContent = texto; }
    return elemento;
  }

  function estadoSeguro(estado) {
    return Object.prototype.hasOwnProperty.call(ROTULO, estado) ? estado : 'sem_sinal';
  }

  function corSegura(cor) {
    return typeof cor === 'string' && /^#[0-9a-fA-F]{3,8}$/.test(cor) ? cor : COR_PADRAO;
  }

  function temPosicao(inscrito) {
    return Number.isFinite(inscrito.lat) && Number.isFinite(inscrito.lon);
  }

  function formatarSegundos(segundos) {
    if (!Number.isFinite(segundos)) { return '-'; }
    if (segundos < 60) { return segundos + ' s'; }
    return Math.floor(segundos / 60) + ' min ' + (segundos % 60) + ' s';
  }

  function formatarBateria(bateria) {
    return Number.isFinite(bateria) ? Math.round(bateria) + '%' : '-';
  }

  function formatarGrau(valor, casas) {    // vírgula decimal e sinal de menos de verdade
    return valor.toFixed(casas).replace('.', ',').replace('-', '−');
  }

  function ordenar(inscritos) {
    return inscritos.slice().sort(function (a, b) {
      const porEstado = PRIORIDADE[estadoSeguro(a.estado)] - PRIORIDADE[estadoSeguro(b.estado)];
      return porEstado || String(a.apelido).localeCompare(String(b.apelido), 'pt-BR');
    });
  }

  // ------------------------------------------------------------- marcadores

  function criarPartesDoIcone() {
    const icone = el('div', 'mk');
    const anel = el('div', 'mk-anel');
    const svg = document.createElementNS(NS_SVG, 'svg');
    const grupo = document.createElementNS(NS_SVG, 'g');
    const seta = document.createElementNS(NS_SVG, 'polygon');
    svg.setAttribute('class', 'mk-seta');
    svg.setAttribute('viewBox', '-12 -12 24 24');
    svg.setAttribute('aria-hidden', 'true');
    seta.setAttribute('points', '0,-10 7,8 0,4 -7,8');   // o traço da seta é do CSS
    grupo.appendChild(seta);
    svg.appendChild(grupo);
    anel.appendChild(svg);
    // Rótulo: "Coruja" e, no perdido, "Coruja · perdido · último sinal há 2 min 10 s". O número é o tempo desde o
    // último sinal, não o tempo "perdido". No celular o CSS quebra em duas linhas: "Coruja · perdido" e o resto.
    const rotulo = el('span', 'mk-apelido');
    const partesDoRotulo = {
      nome: el('span', 'mk-nome'), sep: el('span', 'mk-sep'), estado: el('span', 'mk-estado'),
      sep2: el('span', 'mk-sep2'), tempo: el('span', 'mk-tempo'),
    };
    rotulo.append(partesDoRotulo.nome, partesDoRotulo.sep, partesDoRotulo.estado, partesDoRotulo.sep2, partesDoRotulo.tempo);
    icone.append(anel, rotulo);
    return { icone: icone, anel: anel, grupo: grupo, seta: seta, rotulo: rotulo, texto: partesDoRotulo };
  }

  function atualizarRotulo(partes, inscrito, estado) {
    const perdido = estado === 'perdido';
    const comTempo = perdido && Number.isFinite(inscrito.segundos);
    const texto = partes.texto;
    texto.nome.textContent = inscrito.apelido;
    texto.sep.textContent = perdido ? ' · ' : '';
    texto.estado.textContent = perdido ? 'perdido' : '';
    texto.sep2.textContent = comTempo ? ' · ' : '';
    texto.tempo.textContent = comTempo ? 'último sinal há ' + formatarSegundos(inscrito.segundos) : '';
  }

  function atualizarIcone(partes, inscrito) {
    const estado = estadoSeguro(inscrito.estado);
    const rumo = Number.isFinite(inscrito.rumo) ? inscrito.rumo : 0;   // rumo null: sem giro
    // O perdido ganha os colchetes de alvo (classe alvo, no app.css).
    partes.icone.className = 'mk estado-' + estado + (estado === 'perdido' ? ' alvo' : '');
    partes.anel.className = 'mk-anel estado-' + estado;
    partes.seta.setAttribute('fill', corSegura(inscrito.cor));
    partes.grupo.setAttribute('transform', 'rotate(' + rumo + ')');
    atualizarRotulo(partes, inscrito, estado);
  }

  // ------------------------------------------------- rótulos dos marcadores

  function limitesDoQuadro() {
    const quadro = mapa.getContainer().getBoundingClientRect();
    return { esq: quadro.left + ESPESSURA_REGUA + 4, dir: quadro.right - 4, topo: quadro.top + ESPESSURA_REGUA + 4, base: quadro.bottom - 4 };
  }

  // Retângulo do anel com a folga dos colchetes de alvo (12 px para fora, só no perdido).
  function areaDoAnel(partes, estado) {
    const anel = partes.anel.getBoundingClientRect();
    const folga = estado === 'perdido' ? 12 : 2;
    return { left: anel.left - folga, right: anel.right + folga, top: anel.top - folga, bottom: anel.bottom + folga };
  }

  function mover(caixa, d) {
    return { left: caixa.left + d.dx, right: caixa.right + d.dx, top: caixa.top + d.dy, bottom: caixa.bottom + d.dy };
  }

  function encosta(a, b) {
    return a.left < b.right + 1 && a.right > b.left - 1 && a.top < b.bottom + 1 && a.bottom > b.top - 1;
  }

  // Deslocamento mínimo para a caixa ficar dentro do quadro (e fora das réguas).
  function dentroDoQuadro(caixa, d, limite) {
    let dx = d.dx;
    let dy = d.dy;
    dx -= Math.max(0, caixa.right + dx - limite.dir);
    dx += Math.max(0, limite.esq - (caixa.left + dx));
    dy -= Math.max(0, caixa.bottom + dy - limite.base);
    dy += Math.max(0, limite.topo - (caixa.top + dy));
    return { dx: dx, dy: dy };
  }

  // Onde o rótulo pode ficar em relação ao anel, do mais natural ao mais longe: à direita (origem), à esquerda, acima,
  // abaixo, nos quatro cantos e, por fim, acima e abaixo com mais folga.
  function candidatosDoRotulo(caixa, anel, folga) {
    const meioX = (anel.left + anel.right) / 2 - (caixa.left + caixa.right) / 2;
    const acima = anel.top - folga - caixa.bottom;
    const abaixo = anel.bottom + folga - caixa.top;
    const direita = anel.right + folga - caixa.left;
    const esquerda = anel.left - folga - caixa.right;
    return [
      { dx: 0, dy: 0 }, { dx: esquerda, dy: 0 }, { dx: meioX, dy: acima }, { dx: meioX, dy: abaixo },
      { dx: direita, dy: acima }, { dx: esquerda, dy: acima }, { dx: direita, dy: abaixo }, { dx: esquerda, dy: abaixo },
      { dx: meioX, dy: acima - 36 }, { dx: meioX, dy: abaixo + 36 },
    ];
  }

  // Primeiro lugar que cabe no quadro sem cobrir o próprio anel, outro anel ou outro rótulo.
  function posicaoLivre(caixa, anel, folga, limite, obstaculos) {
    return candidatosDoRotulo(caixa, anel, folga)
      .map(function (candidato) { return dentroDoQuadro(caixa, candidato, limite); })
      .find(function (d) {
        const nova = mover(caixa, d);
        return !encosta(nova, anel) && !obstaculos.some(function (obstaculo) { return encosta(nova, obstaculo); });
      });
  }

  // Sem lugar livre (só o perdido chega aqui): o que cobre menos, e nunca o próprio anel.
  function posicaoMenosRuim(caixa, anel, folga, limite, obstaculos) {
    let melhor = null;
    let menor = Infinity;
    candidatosDoRotulo(caixa, anel, folga).forEach(function (candidato) {
      const d = dentroDoQuadro(caixa, candidato, limite);
      const nova = mover(caixa, d);
      const encostos = (encosta(nova, anel) ? 100 : 0) + obstaculos.filter(function (o) { return encosta(nova, o); }).length;
      if (encostos < menor) { menor = encostos; melhor = d; }
    });
    return melhor;
  }

  function aplicarPosicao(partes, caixa, d) {
    partes.rotulo.style.transform = d.dx || d.dy ? 'translate(' + Math.round(d.dx) + 'px, ' + Math.round(d.dy) + 'px)' : '';
    return mover(caixa, d);
  }

  // O perdido nunca fica sem rótulo: se o inteiro não couber livre, tenta o curto ("Coruja · perdido") e, em último caso,
  // fica onde cobrir menos (nunca o próprio anel). Os outros se escondem quando não há lugar livre (devolve null).
  function posicionarRotulo(atual, obstaculos, limite) {
    const partes = atual.partes;
    const perdido = atual.estado === 'perdido';
    const folga = perdido ? 14 : 6;
    let caixa = null;
    for (const curto of perdido ? [false, true] : [false]) {
      partes.rotulo.classList.toggle('curto', curto);
      partes.rotulo.style.transform = '';
      caixa = partes.rotulo.getBoundingClientRect();
      const d = posicaoLivre(caixa, partes.anel.getBoundingClientRect(), folga, limite, obstaculos);
      if (d) { return aplicarPosicao(partes, caixa, d); }
    }
    if (!perdido) { return null; }
    return aplicarPosicao(partes, caixa, posicaoMenosRuim(caixa, partes.anel.getBoundingClientRect(), folga, limite, obstaculos));
  }

  function compararPrioridade(a, b) {
    return (PRIORIDADE[a.estado] - PRIORIDADE[b.estado]) || a.apelido.localeCompare(b.apelido, 'pt-BR');
  }

  // Cada rótulo cabe no quadro e não cobre outro anel nem outro rótulo. Quem tem prioridade (perdido, atrasado, ativo,
  // depois o apelido) escolhe primeiro. No celular e abaixo do zoom 17 só o perdido e o atrasado levam rótulo.
  function ajustarRotulos() {
    if (!mapa) { return; }
    const poucos = window.matchMedia('(max-width: 719px)').matches || mapa.getZoom() < ZOOM_DOS_ROTULOS;
    const ordem = Array.from(marcadores.values()).sort(compararPrioridade);
    ordem.forEach(function (atual) { atual.partes.rotulo.hidden = false; });
    const limite = limitesDoQuadro();
    const aneis = ordem.map(function (atual) { return areaDoAnel(atual.partes, atual.estado); });
    const fixos = Array.from(mapa.getContainer().querySelectorAll(PECAS_FIXAS)).map(function (peca) { return peca.getBoundingClientRect(); });
    const ocupados = [];
    ordem.forEach(function (atual, indice) {
      const comRotulo = !poucos || atual.estado === 'perdido' || atual.estado === 'atrasado';
      const outros = aneis.filter(function (_, i) { return i !== indice; }).concat(ocupados, fixos);
      const lugar = comRotulo ? posicionarRotulo(atual, outros, limite) : null;
      atual.partes.rotulo.hidden = !lugar;
      if (lugar) { ocupados.push(lugar); }
    });
  }

  function criarMarcador(inscrito) {
    const partes = criarPartesDoIcone();
    atualizarIcone(partes, inscrito);
    const icone = L.divIcon({
      html: partes.icone, className: 'mk-leaflet', iconSize: [36, 36], iconAnchor: [18, 18],
    });
    const marcador = L.marker([inscrito.lat, inscrito.lon], { icon: icone, interactive: false });
    marcador.addTo(mapa);
    return { marcador: marcador, partes: partes, estado: 'sem_sinal', apelido: '' };
  }

  function atualizarMarcadores(inscritos) {
    const vistos = new Set();
    inscritos.filter(temPosicao).forEach(function (inscrito) {
      vistos.add(inscrito.inscricao_id);
      let atual = marcadores.get(inscrito.inscricao_id);
      if (atual) {
        atual.marcador.setLatLng([inscrito.lat, inscrito.lon]);
        atualizarIcone(atual.partes, inscrito);
      } else {
        atual = criarMarcador(inscrito);
        marcadores.set(inscrito.inscricao_id, atual);
      }
      atual.estado = estadoSeguro(inscrito.estado);
      atual.apelido = String(inscrito.apelido);
      atual.marcador.setZIndexOffset(PESO_Z[atual.estado]);
    });
    marcadores.forEach(function (atual, id) {
      if (!vistos.has(id)) { mapa.removeLayer(atual.marcador); marcadores.delete(id); }
    });
  }

  function ajustarVistaUmaVez() {
    if (ajustouVista || marcadores.size === 0) { return; }
    const pontos = Array.from(marcadores.values()).map(function (m) { return m.marcador.getLatLng(); });
    mapa.fitBounds(L.latLngBounds(pontos), { paddingTopLeft: [90, 100], paddingBottomRight: [90, 70], maxZoom: 18 });
    ajustouVista = true;
  }

  // ----------------------------------------------- réguas, retícula e escala

  // Menor múltiplo de 0,001° que deixa PX_ENTRE_NUMEROS px entre dois números da régua.
  function multiploDoPasso(pxPorMilesimo) {
    const multiplos = [1, 2, 5, 10, 20, 50, 100];
    const achado = multiplos.find(function (k) { return k * pxPorMilesimo >= PX_ENTRE_NUMEROS; });
    return achado || multiplos[multiplos.length - 1];
  }

  // Tracinho a cada meio passo; número nos passos inteiros (n par).
  function marcasDoEixo(minimo, maximo, multiplo, posicaoDe) {
    const meio = multiplo * MILESIMO / 2;
    const marcas = [];
    for (let n = Math.ceil(minimo / meio); n * meio <= maximo && marcas.length < 400; n += 1) {
      marcas.push({ pos: posicaoDe(n * meio), valor: n * meio, maior: n % 2 === 0 });
    }
    return marcas;
  }

  function elementoDaMarca(marca, propriedade, comNumero) {
    const itens = [];
    const tracinho = el('i', marca.maior ? 'maior' : null);
    tracinho.style[propriedade] = marca.pos + 'px';
    itens.push(tracinho);
    if (marca.maior && comNumero) {
      const numero = el('span', null, formatarGrau(marca.valor, 3));
      numero.style[propriedade] = marca.pos + 'px';
      itens.push(numero);
    }
    return itens;
  }

  function desenharRegua(regua, marcas, propriedade, cabeNumero) {
    const itens = [];
    marcas.forEach(function (marca) { itens.push(...elementoDaMarca(marca, propriedade, cabeNumero(marca.pos))); });
    regua.replaceChildren(...itens);
  }

  // Marcas das duas réguas, no sistema de coordenadas do mapa (y já descontado da régua do topo).
  function marcasDaTela() {
    const lim = mapa.getBounds();
    const meio = mapa.getCenter();
    const emX = function (lon) { return mapa.latLngToContainerPoint([meio.lat, lon]).x; };
    const emY = function (lat) { return mapa.latLngToContainerPoint([lat, meio.lng]).y - ESPESSURA_REGUA; };
    const kLon = multiploDoPasso(Math.abs(emX(meio.lng + MILESIMO) - emX(meio.lng)));
    const kLat = multiploDoPasso(Math.abs(emY(meio.lat + MILESIMO) - emY(meio.lat)));
    return {
      lon: marcasDoEixo(lim.getWest(), lim.getEast(), kLon, emX),
      lat: marcasDoEixo(lim.getSouth(), lim.getNorth(), kLat, emY),
    };
  }

  function dentroDe(minimo, maximo) {
    return function (marca) { return marca.pos > minimo && marca.pos < maximo; };
  }

  function posicionarReticula() {
    const ponto = mapa.latLngToContainerPoint(centroOperacao);
    reguas.reticula.style.left = ponto.x + 'px';
    reguas.reticula.style.top = ponto.y + 'px';
  }

  function atualizarReguas() {
    if (!mapa || !reguas) { return; }
    const tam = mapa.getSize();
    const marcas = marcasDaTela();
    desenharRegua(reguas.topo, marcas.lon.filter(dentroDe(30, tam.x - 4)), 'left',
      function (x) { return x < tam.x - 90; });
    desenharRegua(reguas.esq, marcas.lat.filter(dentroDe(6, tam.y - ESPESSURA_REGUA - 4)), 'top',
      function (y) { return y < tam.y - ESPESSURA_REGUA - 80; });    // o número ocupa uns 70 px abaixo do tracinho
    posicionarReticula();
  }

  function criarReguas() {
    const quadro = mapa.getContainer();
    reguas = { topo: el('div', 'regua regua-topo'), esq: el('div', 'regua regua-esq'), reticula: el('div', 'reticula') };
    reguas.topo.setAttribute('aria-hidden', 'true');
    reguas.esq.setAttribute('aria-hidden', 'true');
    reguas.reticula.setAttribute('aria-hidden', 'true');
    quadro.append(reguas.topo, reguas.esq, reguas.reticula);
    mapa.on('move zoom zoomend moveend resize', function () { atualizarReguas(); ajustarRotulos(); });
    atualizarReguas();
  }

  // ------------------------------------------------------------------ lista

  function celulaDoTime(inscrito) {
    const celula = el('td');
    const amostra = el('span', 'amostra-time');
    amostra.style.backgroundColor = corSegura(inscrito.cor);
    amostra.setAttribute('aria-hidden', 'true');
    celula.append(amostra, document.createTextNode(inscrito.time));
    return celula;
  }

  function linhaDoInscrito(inscrito) {
    const estado = estadoSeguro(inscrito.estado);
    const linha = el('tr', 'linha-' + estado);
    const selo = el('span', 'selo estado-' + estado, ROTULO[estado]);
    const celulaEstado = el('td');
    celulaEstado.appendChild(selo);
    const nome = el('th', null, inscrito.apelido);
    nome.setAttribute('scope', 'row');
    const baixa = Number.isFinite(inscrito.bateria) && inscrito.bateria < 20;
    linha.append(
      nome,
      celulaDoTime(inscrito),
      celulaEstado,
      el('td', 'num', formatarSegundos(inscrito.segundos)),
      el('td', baixa ? 'num bateria-baixa' : 'num', formatarBateria(inscrito.bateria))
    );
    return linha;
  }

  function desenharLista(inscritos) {
    lista.replaceChildren(...ordenar(inscritos).map(linhaDoInscrito));
  }

  // ----------------------------------------------------------------- faixa

  // O leitor de tela só é avisado quando a contagem de perdidos ou de atrasados muda, e não a cada 3 s.
  function anunciarMudancas(conta) {
    const resumo = conta.perdido + (conta.perdido === 1 ? ' operador perdido' : ' operadores perdidos') +
      ', ' + conta.atrasado + (conta.atrasado === 1 ? ' atrasado.' : ' atrasados.');
    if (resumo === ultimoResumo) { return; }
    ultimoResumo = resumo;
    resumoDeSituacao.textContent = resumo;
  }

  // Contagem por estado, feita no navegador com a mesma resposta que desenha o mapa.
  function desenharFaixa(dados) {
    const conta = { perdido: 0, atrasado: 0, ativo: 0, sem_sinal: 0 };
    dados.inscritos.forEach(function (inscrito) { conta[estadoSeguro(inscrito.estado)] += 1; });
    Object.keys(conta).forEach(function (estado) {
      document.getElementById('n-' + estado).textContent = String(conta[estado]);
    });
    document.getElementById('n-inscritos').textContent = String(dados.inscritos.length);
    anunciarMudancas(conta);
    descartados.textContent = String(dados.descartados || 0);
  }

  // ----------------------------------------------------------- atualização

  function horaAgora() {
    return new Date().toLocaleTimeString('pt-BR');
  }

  function mostrarAviso(texto) {
    aviso.textContent = texto;
    aviso.hidden = false;
  }

  function avisarFalha(erro) {
    let motivo = 'Sem conexão com o servidor.';
    if (erro && erro.status === 401) { motivo = 'Sessão expirada. Entre de novo.'; }
    else if (erro && erro.status) { motivo = 'O servidor respondeu com erro ' + erro.status + '.'; }
    else if (erro && erro.name === 'SyntaxError') { motivo = 'Resposta inesperada do servidor.'; }
    const resto = horaDaUltima ? ' Mostrando os dados de ' + horaDaUltima + '.' : '';
    mostrarAviso('Não consegui atualizar. ' + motivo + resto);
  }

  async function buscarSituacao() {
    const controle = new AbortController();
    const prazo = setTimeout(function () { controle.abort(); }, TEMPO_LIMITE_MS);
    try {
      const resposta = await fetch(urlSituacao, {
        credentials: 'same-origin', cache: 'no-store', signal: controle.signal,
        headers: { Accept: 'application/json' },
      });
      if (!resposta.ok) { throw Object.assign(new Error('HTTP ' + resposta.status), { status: resposta.status }); }
      const dados = await resposta.json();
      if (!dados || !Array.isArray(dados.inscritos)) { throw new SyntaxError('situacao sem inscritos'); }
      return dados;
    } finally {
      clearTimeout(prazo);
    }
  }

  function desenhar(dados) {
    desenharFaixa(dados);
    desenharLista(dados.inscritos);
    if (mapa) {
      atualizarMarcadores(dados.inscritos);
      ajustarVistaUmaVez();
      ajustarRotulos();
    }
  }

  async function atualizar() {
    if (emAndamento) { return; }
    emAndamento = true;
    try {
      desenhar(await buscarSituacao());
      horaDaUltima = horaAgora();
      atualizacao.textContent = 'Atualizado às ' + horaDaUltima;
      if (avisoDoMapa) { mostrarAviso(avisoDoMapa); } else { aviso.hidden = true; }
    } catch (erro) {
      avisarFalha(erro);
    } finally {
      emAndamento = false;
    }
  }

  // ----------------------------------------------------------------- início

  function criarMapa() {
    const lat = parseFloat(raiz.dataset.centroLat);
    const lon = parseFloat(raiz.dataset.centroLon);
    centroOperacao = Number.isFinite(lat) && Number.isFinite(lon) ? [lat, lon] : CENTRO_PADRAO;
    const novo = L.map('mapa', { minZoom: ZOOM_MINIMO }).setView(centroOperacao, 17);
    novo.zoomControl.setPosition('topright');
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      // O app manda Referrer-Policy: same-origin, e o OpenStreetMap bloqueia tile sem Referer.
      referrerPolicy: 'strict-origin-when-cross-origin',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(novo);
    L.control.scale({ imperial: false, position: 'bottomleft' }).addTo(novo);
    return novo;
  }

  if (typeof L !== 'undefined') {
    mapa = criarMapa();
    criarReguas();
  } else {
    avisoDoMapa = 'A biblioteca do mapa não carregou. A lista continua sendo atualizada.';
    mostrarAviso(avisoDoMapa);
  }
  atualizar();
  setInterval(atualizar, INTERVALO_MS);
})();
