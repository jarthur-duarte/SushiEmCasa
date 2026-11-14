/* Checkout: valida a data/hora de entrega no navegador e explica
   o motivo quando o horário não é aceito. As mesmas regras são
   conferidas de novo no servidor (OrderForm). */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  var campo = document.getElementById('id_delivery_datetime');
  var botao = document.getElementById('confirm-order-btn');
  var feedback = document.getElementById('feedback-data');
  if (!campo || !botao) return;

  var UM_DIA = 24 * 60 * 60 * 1000;
  var ABRE = 10;   // 10:00
  var FECHA = 20;  // 20:00

  function paraInput(data) { // formato aceito por datetime-local
    var p = function (n) { return String(n).padStart(2, '0'); };
    return data.getFullYear() + '-' + p(data.getMonth() + 1) + '-' + p(data.getDate()) +
      'T' + p(data.getHours()) + ':' + p(data.getMinutes());
  }

  // não deixa escolher antes de agora + 24h
  campo.min = paraInput(new Date(Date.now() + UM_DIA));

  function mensagem(texto, tipo) {
    feedback.textContent = texto;
    feedback.className = 'feedback-data ' + (tipo || '');
    campo.setAttribute('aria-invalid', tipo === 'erro' ? 'true' : 'false');
  }

  function validar() {
    var valor = campo.value;
    var erro = null;

    if (!valor) {
      botao.disabled = true;
      mensagem('Choose a delivery date and time to continue.');
      return;
    }

    var data = new Date(valor);
    var hora = data.getHours() + data.getMinutes() / 60;

    if (isNaN(data.getTime())) erro = 'Invalid date.';
    else if (data.getTime() <= Date.now() + UM_DIA) erro = 'Choose a time at least 24 hours from now.';
    else if (data.getDay() === 0) erro = 'We don\'t deliver on Sundays. Please choose another day.';
    else if (hora < ABRE || hora >= FECHA) erro = 'Deliveries are made between 10:00 AM and 8:00 PM.';

    botao.disabled = !!erro;
    if (erro) {
      mensagem(erro, 'erro');
    } else {
      var texto = data.toLocaleString('en-US', { weekday: 'long', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit' });
      mensagem('Delivery scheduled for ' + texto + '.', 'ok');
    }
  }

  campo.addEventListener('input', validar);
  campo.addEventListener('change', validar);
  validar();
});
