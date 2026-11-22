/* Carrinho: atualiza a quantidade sem recarregar a página.
   Funciona ao mudar o campo ou ao clicar em "Atualizar". */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  var aviso = document.getElementById('aviso-carrinho');
  var totalGeral = document.getElementById('total-geral');

  function cookie(nome) {
    var partes = ('; ' + document.cookie).split('; ' + nome + '=');
    return partes.length === 2 ? decodeURIComponent(partes.pop().split(';').shift()) : null;
  }

  function csrf(form) {
    var campo = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return campo ? campo.value : cookie('csrftoken');
  }

  function dinheiro(valor) {
    return '$ ' + parseFloat(valor).toFixed(2);
  }

  function atualizar(form) {
    var campo = form.querySelector('input[name="quantity"]');
    var quantidade = parseInt(campo.value, 10);
    if (!quantidade || quantidade < 1) {
      campo.value = 1;
      quantidade = 1;
    }
    var linha = form.closest('tr');
    linha.classList.add('atualizando');

    fetch(form.action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf(form) },
      body: JSON.stringify({ quantity: quantidade })
    })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (dados) {
        if (!dados.success) throw new Error('falhou');
        var subtotal = document.getElementById('subtotal-' + form.dataset.productId);
        if (subtotal) subtotal.textContent = dinheiro(dados.item_total);
        if (totalGeral) totalGeral.textContent = dinheiro(dados.cart_total);
        if (aviso) aviso.textContent = 'Quantity updated. New total: ' + dinheiro(dados.cart_total) + '.';
      })
      .catch(function () {
        if (aviso) aviso.textContent = 'Could not update the quantity. Please try again.';
      })
      .finally(function () {
        linha.classList.remove('atualizando');
      });
  }

  document.querySelectorAll('.form-atualizar-quantidade').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      atualizar(form);
    });
    form.querySelector('input[name="quantity"]').addEventListener('change', function () {
      atualizar(form);
    });
  });
});
