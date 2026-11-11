/* Tema da interface: Sistema (padrão), Claro ou Escuro.
 * Carregado no <head>, sem defer, para marcar o <html> antes da primeira pintura.
 * Sistema = sem atributo (vale o CSS e o esquema do sistema); Claro e Escuro = data-tema.
 * Sem JS, o seletor fica escondido e vale o modo Sistema. */
(function () {
  'use strict';

  const CHAVE = 'meshtracker-tema';
  const TEMAS = ['sistema', 'claro', 'escuro'];
  const raiz = document.documentElement;

  function lerEscolha() {
    try {
      const guardado = window.localStorage.getItem(CHAVE);
      return TEMAS.indexOf(guardado) >= 0 ? guardado : 'sistema';
    } catch (erro) {
      return 'sistema';     // armazenamento bloqueado: vale o modo Sistema
    }
  }

  function guardarEscolha(tema) {
    try {
      window.localStorage.setItem(CHAVE, tema);
    } catch (erro) {
      // sem armazenamento, a escolha vale só até recarregar a página
    }
  }

  function aplicar(tema) {
    if (tema === 'sistema') { raiz.removeAttribute('data-tema'); } else { raiz.setAttribute('data-tema', tema); }
  }

  function marcar(grupo, tema) {
    grupo.querySelectorAll('button[data-tema]').forEach(function (botao) {
      botao.setAttribute('aria-pressed', String(botao.dataset.tema === tema));
    });
    const lista = grupo.querySelector('select');      // a lista do celular acompanha os botões
    if (lista) { lista.value = tema; }
  }

  function escolher(grupo, tema) {
    aplicar(tema);
    guardarEscolha(tema);
    marcar(grupo, tema);
  }

  function ligarSeletor() {
    const grupo = document.getElementById('seletor-tema');
    if (!grupo) { return; }
    marcar(grupo, lerEscolha());
    grupo.hidden = false;
    grupo.querySelectorAll('button[data-tema]').forEach(function (botao) {
      botao.addEventListener('click', function () { escolher(grupo, botao.dataset.tema); });
    });
    const lista = grupo.querySelector('select');
    if (lista) { lista.addEventListener('change', function () { escolher(grupo, lista.value); }); }
  }

  aplicar(lerEscolha());
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ligarSeletor);
  } else {
    ligarSeletor();
  }
})();
