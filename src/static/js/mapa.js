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

  const aviso = document.getElementById('aviso');
  const atualizacao = document.getElementById('atualizacao');
  const descartados = document.getElementById('descartados');
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
    // Rótulo: "Coruja" e, no perdido, " · perdido há 2 min 10 s". No celular o CSS quebra em duas linhas.
    const rotulo = el('span', 'mk-apelido');
    const nome = el('span', 'mk-nome');
    const separador = el('span', 'mk-sep', ' · ');
    const tempo = el('span', 'mk-tempo');
    rotulo.append(nome, separador, tempo);
    icone.append(anel, rotulo);
    return { icone: icone, anel: anel, grupo: grupo, seta: seta, rotulo: rotulo, nome: nome, separador: separador, tempo: tempo };
  }

  function textoDoTempoPerdido(inscrito) {
    return Number.isFinite(inscrito.segundos) ? 'perdido há ' + formatarSegundos(inscrito.segundos) : 'perdido';
  }

  function atualizarRotulo(partes, inscrito, estado) {
    const perdido = estado === 'perdido';
    partes.nome.textContent = inscrito.apelido;
    partes.separador.hidden = !perdido;
    partes.separador.textContent = perdido ? ' · ' : '';
    partes.tempo.hidden = !perdido;
    partes.tempo.textContent = perdido ? textoDoTempoPerdido(inscrito) : '';
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

  // O rótulo nunca sai do quadro do mapa: se passaria da borda (ou das réguas), desliza para dentro.
  function limitesDoQuadro() {
    const quadro = mapa.getContainer().getBoundingClientRect();
    return { esq: quadro.left + ESPESSURA_REGUA + 4, dir: quadro.right - 4, topo: quadro.top + ESPESSURA_REGUA + 4, base: quadro.bottom - 4 };
  }

  // Quanto o rótulo precisa andar para caber no quadro. Se, deslizando de lado, ele cobrisse o anel,
  // vai para baixo do marcador (ou para cima, se faltar espaço), fora dos colchetes de alvo.
  function deslocamentoDoRotulo(caixa, anel, limite) {
    let dx = caixa.right > limite.dir ? limite.dir - caixa.right : 0;
    if (caixa.left + dx < limite.esq) { dx = limite.esq - caixa.left; }
    let dy = 0;
    if (caixa.left + dx < anel.right - 2) {
      dy = anel.bottom + 14 - caixa.top;
      if (caixa.bottom + dy > limite.base) { dy = anel.top - 14 - caixa.bottom; }
    }
    if (caixa.bottom + dy > limite.base) { dy = limite.base - caixa.bottom; }
    if (caixa.top + dy < limite.topo) { dy = limite.topo - caixa.top; }
    return { dx: dx, dy: dy };
  }

  function manterRotuloNoQuadro(partes) {
    partes.rotulo.style.transform = '';
    const desvio = deslocamentoDoRotulo(partes.rotulo.getBoundingClientRect(), partes.anel.getBoundingClientRect(), limitesDoQuadro());
    if (desvio.dx || desvio.dy) {
      partes.rotulo.style.transform = 'translate(' + Math.round(desvio.dx) + 'px, ' + Math.round(desvio.dy) + 'px)';
    }
  }

  function ajustarRotulos() {
    marcadores.forEach(function (atual) { manterRotuloNoQuadro(atual.partes); });
  }

  function criarMarcador(inscrito) {
    const partes = criarPartesDoIcone();
    atualizarIcone(partes, inscrito);
    const icone = L.divIcon({
      html: partes.icone, className: 'mk-leaflet', iconSize: [36, 36], iconAnchor: [18, 18],
    });
    const marcador = L.marker([inscrito.lat, inscrito.lon], { icon: icone, interactive: false });
    marcador.addTo(mapa);
    return { marcador: marcador, partes: partes };
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
      atual.marcador.setZIndexOffset(PESO_Z[estadoSeguro(inscrito.estado)]);
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
      function (y) { return y > 80; });
    posicionarReticula();
  }

  function criarReguas() {
    const quadro = mapa.getContainer();
    reguas = { topo: el('div', 'regua regua-topo'), esq: el('div', 'regua regua-esq'), reticula: el('div', 'reticula') };
    reguas.topo.setAttribute('aria-hidden', 'true');
    reguas.esq.setAttribute('aria-hidden', 'true');
    reguas.reticula.setAttribute('aria-hidden', 'true');
    quadro.append(reguas.topo, reguas.esq, reguas.reticula);
    mapa.on('move zoom resize', function () { atualizarReguas(); ajustarRotulos(); });
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

  // Contagem por estado, feita no navegador com a mesma resposta que desenha o mapa.
  function desenharFaixa(dados) {
    const conta = { perdido: 0, atrasado: 0, ativo: 0, sem_sinal: 0 };
    dados.inscritos.forEach(function (inscrito) { conta[estadoSeguro(inscrito.estado)] += 1; });
    Object.keys(conta).forEach(function (estado) {
      document.getElementById('n-' + estado).textContent = String(conta[estado]);
    });
    document.getElementById('n-inscritos').textContent = String(dados.inscritos.length);
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
    const novo = L.map('mapa').setView(centroOperacao, 17);
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
