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

  function marcar(botoes, tema) {
    botoes.forEach(function (botao) {
      botao.setAttribute('aria-pressed', String(botao.dataset.tema === tema));
    });
  }

  function ligarSeletor() {
    const grupo = document.getElementById('seletor-tema');
    if (!grupo) { return; }
    const botoes = Array.prototype.slice.call(grupo.querySelectorAll('button[data-tema]'));
    marcar(botoes, lerEscolha());
    grupo.hidden = false;
    botoes.forEach(function (botao) {
      botao.addEventListener('click', function () {
        const tema = botao.dataset.tema;
        aplicar(tema);
        guardarEscolha(tema);
        marcar(botoes, tema);
      });
    });
  }

  aplicar(lerEscolha());
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ligarSeletor);
  } else {
    ligarSeletor();
  }
})();
