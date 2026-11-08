/* Mapa ao vivo (US06). Busca /api/v1/situacao a cada 3 s e desenha marcadores e lista.
 * Todo texto vindo do servidor entra por textContent ou setAttribute, nunca por innerHTML. */
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

  const aviso = document.getElementById('aviso');
  const atualizacao = document.getElementById('atualizacao');
  const descartados = document.getElementById('descartados');
  const lista = document.getElementById('lista');
  const urlSituacao = raiz.dataset.urlSituacao + '?operacao=' + encodeURIComponent(raiz.dataset.operacaoId);

  const marcadores = new Map();   // inscricao_id -> { marcador, partes }
  let mapa = null;
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
    seta.setAttribute('points', '0,-10 7,8 0,4 -7,8');
    seta.setAttribute('stroke', '#ffffff');
    seta.setAttribute('stroke-width', '1.5');
    seta.setAttribute('stroke-linejoin', 'round');
    grupo.appendChild(seta);
    svg.appendChild(grupo);
    anel.appendChild(svg);
    const rotulo = el('span', 'mk-apelido');
    icone.append(anel, rotulo);
    return { icone: icone, anel: anel, grupo: grupo, seta: seta, rotulo: rotulo };
  }

  function atualizarIcone(partes, inscrito) {
    const rumo = Number.isFinite(inscrito.rumo) ? inscrito.rumo : 0;   // rumo null: sem giro
    partes.anel.className = 'mk-anel estado-' + estadoSeguro(inscrito.estado);
    partes.seta.setAttribute('fill', corSegura(inscrito.cor));
    partes.grupo.setAttribute('transform', 'rotate(' + rumo + ')');
    partes.rotulo.textContent = inscrito.apelido;
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
    mapa.fitBounds(L.latLngBounds(pontos), { padding: [40, 40], maxZoom: 18 });
    ajustouVista = true;
  }

  // ------------------------------------------------------------------ lista

  function celulaDoTime(inscrito) {
    const celula = el('td');
    const amostra = el('span', 'amostra-time');
    amostra.style.backgroundColor = corSegura(inscrito.cor);
    celula.append(amostra, document.createTextNode(' ' + inscrito.time));
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
      el('td', null, formatarSegundos(inscrito.segundos)),
      el('td', baixa ? 'bateria-baixa' : null, formatarBateria(inscrito.bateria))
    );
    return linha;
  }

  function desenharLista(inscritos) {
    lista.replaceChildren(...ordenar(inscritos).map(linhaDoInscrito));
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
    descartados.textContent = String(dados.descartados || 0);
    desenharLista(dados.inscritos);
    if (mapa) {
      atualizarMarcadores(dados.inscritos);
      ajustarVistaUmaVez();
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
    const centro = Number.isFinite(lat) && Number.isFinite(lon) ? [lat, lon] : CENTRO_PADRAO;
    const novo = L.map('mapa').setView(centro, 17);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      // O app manda Referrer-Policy: same-origin, e o OpenStreetMap bloqueia tile sem Referer.
      referrerPolicy: 'strict-origin-when-cross-origin',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(novo);
    return novo;
  }

  if (typeof L !== 'undefined') {
    mapa = criarMapa();
  } else {
    avisoDoMapa = 'A biblioteca do mapa não carregou. A lista continua sendo atualizada.';
    mostrarAviso(avisoDoMapa);
  }
  atualizar();
  setInterval(atualizar, INTERVALO_MS);
})();
