/* Painel: filtros simples no navegador (status e busca por texto).
   Não muda nada no servidor; só mostra/esconde linhas da tabela. */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  var tabela = document.querySelector('[data-filtravel]');
  if (!tabela) return;

  var linhas = Array.prototype.slice.call(tabela.querySelectorAll('tbody tr[data-busca]'));
  var busca = document.getElementById('filtro-busca');
  var chips = Array.prototype.slice.call(document.querySelectorAll('[data-filtro-status]'));
  var contagem = document.getElementById('contagem-filtro');
  var statusAtivo = 'todos';

  function aplicar() {
    var termo = busca ? busca.value.trim().toLowerCase() : '';
    var visiveis = 0;
    linhas.forEach(function (tr) {
      var okStatus = statusAtivo === 'todos' || tr.dataset.status === statusAtivo;
      var okBusca = !termo || tr.dataset.busca.toLowerCase().indexOf(termo) !== -1;
      tr.hidden = !(okStatus && okBusca);
      if (!tr.hidden) visiveis++;
    });
    if (contagem) {
      contagem.textContent = visiveis + (visiveis === 1 ? ' resultado' : ' resultados');
    }
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      statusAtivo = chip.dataset.filtroStatus;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      aplicar();
    });
  });
  if (busca) busca.addEventListener('input', aplicar);
  aplicar();
});
