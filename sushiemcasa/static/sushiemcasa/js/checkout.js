/* Checkout: o cliente escolhe um dia e depois um dos horários livres desse dia.
   A lista vem do servidor (horário de funcionamento definido no painel, a
   pelo menos 24h de agora) e a escolha é conferida de novo no OrderForm.
   Sem JavaScript, todos os dias aparecem com seus horários e o envio funciona. */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  var agenda = document.getElementById('agenda');
  var botao = document.getElementById('confirm-order-btn');
  var feedback = document.getElementById('feedback-data');
  if (!agenda || !botao) return;

  var dias = agenda.querySelectorAll('input[name="dia"]');
  var grupos = agenda.querySelectorAll('.agenda__horarios');

  if (!dias.length) { // nenhum horário disponível
    botao.disabled = true;
    return;
  }

  agenda.classList.add('agenda--js');

  function mensagem(texto, tipo) {
    feedback.textContent = texto;
    feedback.className = 'feedback-data ' + (tipo || '');
  }

  function horarioMarcado() {
    return agenda.querySelector('input[name="delivery_datetime"]:checked');
  }

  function atualizarBotao() {
    var marcado = horarioMarcado();
    botao.disabled = !marcado;
    if (marcado) mensagem('Delivery scheduled for ' + marcado.dataset.extenso + '.', 'ok');
    else mensagem('Choose a delivery time to continue.');
  }

  function mostrarDia(valor) {
    grupos.forEach(function (g) {
      var ativo = g.dataset.dia === valor;
      g.hidden = !ativo;
      if (!ativo) {
        g.querySelectorAll('input:checked').forEach(function (i) { i.checked = false; });
      }
    });
    atualizarBotao();
  }

  dias.forEach(function (d) {
    d.addEventListener('change', function () { mostrarDia(d.value); });
  });
  agenda.addEventListener('change', function (e) {
    if (e.target.name === 'delivery_datetime') atualizarBotao();
  });

  var diaAtual = agenda.querySelector('input[name="dia"]:checked') || dias[0];
  diaAtual.checked = true;
  mostrarDia(diaAtual.value);
});
