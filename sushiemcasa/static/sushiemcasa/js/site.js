/* Comportamentos comuns a todas as páginas: menu mobile,
   menu do usuário e confirmação de ações destrutivas. */
(function () {
  'use strict';

  // ---- Menu mobile (gaveta) ----
  var botaoAbrir = document.getElementById('abrir-menu');
  var gaveta = document.getElementById('gaveta');
  var fundo = document.getElementById('gaveta-fundo');
  var ultimoFoco = null;

  function focaveis() {
    return gaveta.querySelectorAll('a[href], button:not([disabled])');
  }

  function abrir() {
    ultimoFoco = document.activeElement;
    gaveta.classList.add('aberta');
    gaveta.removeAttribute('aria-hidden');
    fundo.hidden = false;
    document.body.classList.add('gaveta-aberta');
    botaoAbrir.setAttribute('aria-expanded', 'true');
    var itens = focaveis();
    if (itens.length) itens[0].focus();
  }

  function fechar() {
    gaveta.classList.remove('aberta');
    gaveta.setAttribute('aria-hidden', 'true');
    fundo.hidden = true;
    document.body.classList.remove('gaveta-aberta');
    botaoAbrir.setAttribute('aria-expanded', 'false');
    if (ultimoFoco) ultimoFoco.focus();
  }

  if (botaoAbrir && gaveta && fundo) {
    botaoAbrir.addEventListener('click', abrir);
    fundo.addEventListener('click', fechar);
    gaveta.querySelectorAll('[data-fechar-menu]').forEach(function (b) {
      b.addEventListener('click', fechar);
    });
    document.addEventListener('keydown', function (e) {
      if (!gaveta.classList.contains('aberta')) return;
      if (e.key === 'Escape') { fechar(); return; }
      if (e.key === 'Tab') { // mantém o foco dentro da gaveta
        var itens = focaveis();
        var primeiro = itens[0];
        var ultimo = itens[itens.length - 1];
        if (e.shiftKey && document.activeElement === primeiro) { e.preventDefault(); ultimo.focus(); }
        else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primeiro.focus(); }
      }
    });
  }

  // ---- Menu do usuário (<details>): fecha ao clicar fora ou com Esc ----
  var menuUsuario = document.querySelector('.menu-usuario');
  if (menuUsuario) {
    document.addEventListener('click', function (e) {
      if (menuUsuario.open && !menuUsuario.contains(e.target)) menuUsuario.open = false;
    });
    menuUsuario.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menuUsuario.open) {
        menuUsuario.open = false;
        menuUsuario.querySelector('summary').focus();
      }
    });
  }

  // ---- Confirmação: <form data-confirmar="Mensagem"> ----
  document.addEventListener('submit', function (e) {
    var form = e.target;
    var msg = form.getAttribute && form.getAttribute('data-confirmar');
    if (msg && !window.confirm(msg)) e.preventDefault();
  });

  // ---- Cartões surgem ao rolar a página ----
  // Só esconde o que vai animar quando o navegador suporta IntersectionObserver
  // e a pessoa não pediu menos movimento; sem isso, tudo aparece normalmente.
  var calmo = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!calmo && 'IntersectionObserver' in window) {
    var alvos = document.querySelectorAll('.produto-card, .pedido-card, .canal');
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (entrada.isIntersecting) {
          entrada.target.classList.add('visivel');
          observador.unobserve(entrada.target);
        }
      });
    }, { rootMargin: '0px 0px -40px 0px' });
    Array.prototype.forEach.call(alvos, function (el, i) {
      el.style.setProperty('--atraso', (i % 4) * 70 + 'ms');
      el.classList.add('revelar');
      // terminada a entrada, tira as classes para o efeito de hover voltar a valer
      el.addEventListener('animationend', function fim(e) {
        if (e.target !== el) return;
        el.classList.remove('revelar', 'visivel');
        el.removeEventListener('animationend', fim);
      });
      observador.observe(el);
    });
  }
})();
